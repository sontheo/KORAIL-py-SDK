"""Compatible operations dispatched through independently implemented engines."""

from __future__ import annotations

import dataclasses
import inspect
from functools import lru_cache

from korail_api.models import errors as E
from korail_api.models.records import CONTRACT, REGISTRY, restore
from korail_api.protocol.codec import decode
from korail_api.protocol.requests import compile_form
from korail_api.protocol.schema import load
from korail_api.services.authentication import KorailSessionClient
from korail_api.transport.admission import Admission
from korail_api.transport.cleanup import close_resources
from korail_api.transport.http import KorailHttpClient

KorailNetFunnelClient = Admission


def _signature(spec):
    parameters = []
    for p in spec["parameters"]:
        options = {"name": p["name"], "kind": getattr(inspect.Parameter, p["kind"])}
        if "default" in p:
            options["default"] = restore(p["default"])
        parameters.append(inspect.Parameter(**options))
    return inspect.Signature(parameters)


@lru_cache(maxsize=256)
def _order_members(order):
    return frozenset(order)


def order_fields(values, order):
    if not order:
        return values
    members = _order_members(tuple(order))
    return {
        **{key: values[key] for key in order if key in values},
        **{key: val for key, val in values.items() if key not in members},
    }


class KorailClient:
    def __init__(self, config=None, *, transport=None, maintenance=None):
        self.config = config or REGISTRY["KorailConfig"]()
        self.http = KorailHttpClient(self.config, transport=transport, maintenance=maintenance)
        self.maintenance = self.http.maintenance
        self.session = KorailSessionClient(self.http)
        self.netfunnel = None
        self._closed = False
        self._station_names = None
        try:
            if self.config.netfunnel_enabled:
                self.netfunnel = KorailNetFunnelClient(
                    self.config, transport=transport, maintenance=self.maintenance
                )
        except BaseException as error:
            close_resources([self.http], error)
            raise

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self._close(exc[1] if len(exc) > 1 else None)

    def close(self):
        self._close()

    def _close(self, original=None):
        if not self._closed:
            self._closed = True
            close_resources([self.http, self.netfunnel], original)

    def login(self, member_no, password, *, input_flag=None, check_valid_pw="Y", cust_id="", etr_path=""):
        return self.session.login(
            member_no,
            password,
            input_flag=input_flag,
            check_valid_pw=check_valid_pw,
            cust_id=cust_id,
            etr_path=etr_path,
        )

    def clear_session(self):
        self.session.clear()

    def logout(self):
        self.session.logout()

    def search_trains(self, query, *, continuation=None, use_special_schedule=False, peak_season=False):
        return self._invoke(
            "search_trains",
            dict(
                query=query,
                continuation=continuation,
                use_special_schedule=use_special_schedule,
                peak_season=peak_season,
            ),
        )

    def search_transfer_trains(
        self, query, *, continuation=None, use_special_schedule=False, peak_season=False
    ):
        return self._invoke(
            "search_transfer_trains",
            dict(
                query=query,
                continuation=continuation,
                use_special_schedule=use_special_schedule,
                peak_season=peak_season,
            ),
        )

    def _require_session(self, what="Operation"):
        if self.session.current is None:
            raise E.KorailAuthError(f"{what} requires a login session")

    def _require_customer_no(self, what):
        self._require_session(what)
        customer = self.session.current.customer_no
        if not customer or not customer.strip():
            raise E.KorailAuthError(f"{what} requires a customer number")
        return customer

    def _queued(self, gate, send):
        return self.netfunnel.run(gate, send) if self.netfunnel else send()

    @staticmethod
    def _inquiry_gate(*, peak_season, special=False):
        return "product_inquiry" if special else "peak_season_inquiry" if peak_season else "inquiry"

    @staticmethod
    def _parse_mutation_response(raw, parser):
        try:
            return parser(raw)
        except Exception as error:
            if isinstance(error, E.KorailApiError):
                raised = error
                if error.raw is not None and error.raw is not raw:
                    raised.parser_raw = error.raw
            else:
                raised = E.KorailProtocolError(
                    "Transaction response could not be decoded; verify its outcome before retrying"
                )
            raised.raw = raw
            if raised is error:
                raise
            raise raised from error

    def _mutation(self, route, form, *, parser=None, raise_on_fail=True):
        try:
            response = self.http.post_mutation_form(route, form, raise_on_fail=raise_on_fail)
            return response if parser is None else self._parse_mutation_response(response.raw, parser)
        except E.KorailSessionExpiredError:
            self.clear_session()
            raise

    def _resolve_station_reference(self, reference):
        if not (reference.isascii() and reference.isdigit()):
            return reference
        if self._station_names is None:
            self._station_names = {station.code: station.name for station in self.get_station_data().stations}
        if reference not in self._station_names:
            raise E.KorailProtocolError("Station code was not found")
        return self._station_names[reference]

    def _build(self, recipe, arguments, *, include_language=True):
        return compile_form(recipe).render(self, arguments, include_language)

    def _invoke(self, name, arguments):
        from korail_api.services.operations import finish, prepare

        if name != "get_service_status":
            self.maintenance.check(self.config.base_url)
        recipe = load("requests")[name]
        authorization = load("authorization")[name]
        if authorization["session"]:
            self._require_session(name)
        if authorization["customer"]:
            self._require_customer_no(name)
        steps = [row for row in recipe["exchanges"] if row["path"] != "/ts.wseq"]
        if not steps:
            raise E.KorailProtocolError("Operation does not have an HTTP exchange")
        # Request validation always precedes admission and any transaction.
        forms = [
            self._build(
                row["form"] if row["method"] == "POST" else row["query"],
                arguments,
                include_language=row.get("language", True),
            )
            for row in steps
        ]
        queries = [
            self._build(row["query"], arguments, include_language=row.get("language", True))
            if row["method"] == "POST"
            else None
            for row in steps
        ]
        steps, forms = prepare(self, name, arguments, steps, forms)
        actions = [
            row
            for row in recipe["exchanges"]
            if row["path"] == "/ts.wseq" and row["query"].get("opcode", {}).get("literal") == ["5101"]
        ]
        action = actions[0]["query"]["aid"]["literal"][0] if actions else None
        gate_name = (
            "pay"
            if name == "pay_with_card"
            else "reserve"
            if name.startswith("reserve")
            else "reservation_view"
            if name == "get_reservation_history"
            else "inquiry"
        )
        if gate_name == "inquiry":
            gate_name = (
                "product_inquiry"
                if arguments.get("use_special_schedule")
                else "peak_season_inquiry"
                if arguments.get("peak_season")
                else gate_name
            )
        if action:
            action = (self.config.netfunnel_actions or {}).get(gate_name, action)
            if name.startswith("search_") or name == "get_seat_assignment_schedule":
                action = (
                    "act_6"
                    if arguments.get("use_special_schedule")
                    else "act_8_2"
                    if arguments.get("peak_season")
                    else action
                )

        def send():
            response = None
            policy = load("response-policy")[name]
            for index, (step, form) in enumerate(zip(steps, forms)):
                if name not in {"get_ticket_list", "get_commuter_info"}:
                    form = order_fields(
                        form,
                        step.get("field_order", {}).get("form" if step["method"] == "POST" else "query", ()),
                    )
                try:
                    result = self.http.exchange(
                        step["path"],
                        form,
                        method=step["method"],
                        include_common=False,
                        query=queries[index],
                        content_type=step.get("content_type"),
                        omit_empty_fields=step["method"] != "GET"
                        and name not in {"get_price_fare_quote", "recalculate_price", "get_deposit_banks"},
                        require_envelope=policy["require_envelope"],
                        raise_on_fail=policy["raise_on_fail"],
                    )
                except E.KorailAppError as error:
                    if error.code not in load("empty-responses").get(name, ()):
                        raise
                    result = decode("BaseKorailResponse", error.raw)
                response = result
            if response is None:
                raise E.KorailProtocolError("Operation produced no response")

            def parser(raw):
                return finish(self, name, arguments, decode(recipe["return_type"], raw))

            return self._parse_mutation_response(response.raw, parser)

        try:
            if action and self.netfunnel is not None:
                return self._queued(gate_name, send)
            return send()
        except E.KorailSessionExpiredError:
            self.clear_session()
            raise

    def search_trains_all(self, query, *, max_time=None, max_pages=15):
        if type(max_pages) is not int or max_pages < 1:
            raise E.KorailProtocolError("Page budget must be a positive integer")
        upper = max_time.ljust(6, "0") if max_time else None
        all_trains = []
        seen = set()
        continuation = None
        current = query
        for _ in range(max_pages):
            try:
                page = self.search_trains(current, continuation=continuation)
            except E.KorailNoResultsError:
                if all_trains:
                    return all_trains
                raise
            new = 0
            for train in page.trains:
                key = (
                    train.train_no,
                    train.departure_date,
                    train.departure_time,
                    train.departure_station_code,
                    train.arrival_station_code,
                )
                if key not in seen:
                    seen.add(key)
                    if not upper or (train.departure_time or "") <= upper:
                        all_trains.append(train)
                    new += 1
            if not page.trains or page.metadata.next_page_flag != "Y":
                return all_trains
            last = max(
                page.trains, key=lambda t: (t.departure_date or current.departure_date, t.departure_time or "")
            )
            if upper and (last.departure_time or "") >= upper:
                return all_trains
            next_cursor = page.next_page()
            if not new:
                error = E.KorailProtocolError("Pagination repeated a page without progress")
                error.code = "PAGINATION_STALLED"
                raise error
            if next_cursor is not None:
                continuation = next_cursor
            else:
                boundary = (last.departure_date or current.departure_date, last.departure_time or "")
                if boundary <= (current.departure_date, current.departure_time):
                    error = E.KorailProtocolError("Pagination has no advancing boundary")
                    error.code = "PAGINATION_STALLED"
                    raise error
                current = dataclasses.replace(current, departure_date=boundary[0], departure_time=boundary[1])
                continuation = None
        error = E.KorailProtocolError("Pagination reached its page budget")
        error.code = "PAGINATION_LIMIT"
        raise error

    def search_trains_with_transfer_fallback(
        self, query, *, continuation=None, use_special_schedule=False, peak_season=False
    ):
        options = dict(
            continuation=continuation, use_special_schedule=use_special_schedule, peak_season=peak_season
        )
        try:
            return self.search_trains(query, **options)
        except E.KorailNoDirectTrainError:
            options["continuation"] = None
            return self.search_transfer_trains(query, **options)


def _install_operations():
    for name, spec in CONTRACT["client"].items():
        if name in vars(KorailClient):
            continue
        signature = _signature(spec)

        def operation(self, *args, __name=name, __signature=signature, **kwargs):
            bound = __signature.bind(self, *args, **kwargs)
            bound.apply_defaults()
            arguments = dict(bound.arguments)
            del arguments["self"]
            return self._invoke(__name, arguments)

        operation.__name__ = name
        operation.__doc__ = (
            "Synthetic compatibility checks cover this operation; live acceptance is unverified (검증 못 함)."
        )
        operation.__qualname__ = f"KorailClient.{name}"
        operation.__signature__ = signature
        setattr(KorailClient, name, operation)


_install_operations()
