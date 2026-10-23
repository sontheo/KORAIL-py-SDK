"""Failure categories shared by transport, admission and business operations."""

from __future__ import annotations

from korail_api.protocol.schema import load as _load_schema


class KorailApiError(Exception):
    raw: object = None
    parser_raw: object = None
    code: str | None = None
    status_code: int | None = None
    retry_after: float | None = None
    next_probe_at: float | None = None

    def __reduce__(self):
        return _restore_exception, (type(self), self.args, self.__dict__)


def _restore_exception(cls, args, attributes):
    instance = cls.__new__(cls)
    Exception.__init__(instance, *args)
    instance.__dict__.update(attributes)
    return instance


class KorailProtocolError(KorailApiError):
    pass


class KorailTransportError(KorailApiError):
    pass


class KorailAuthError(KorailApiError):
    pass


class KorailDynaPathError(KorailApiError):
    def __init__(self, message: str | None = None, *, raw: object | None = None) -> None:
        self.raw = raw
        super().__init__(message or "Server rejected protocol access")


class KorailAppError(KorailApiError):
    def __init__(self, code: str | None, message: str | None, *, raw: object = None):
        self.code = code
        self.message = message
        self.raw = raw
        super().__init__(f"{code or 'UNKNOWN'}: {message or 'Request rejected'}")

    @property
    def display_message(self) -> str:
        from korail_api.messages.catalog import resolve_error_message

        return resolve_error_message(self.code, self.message)


class KorailAuthContinuationRequired(KorailAuthError):
    def __init__(self, redirect_url: str, *, raw: object = None):
        self.redirect_url = redirect_url
        self.raw = raw
        super().__init__("Account action is required before login can complete")


class _ErrorDetails:
    def __init__(self, code=None, message=None, *, raw=None):
        self.code, self.message, self.raw = code, message, raw
        super().__init__(f"{code or 'UNKNOWN'}: {message or 'Request rejected'}")

    @property
    def display_message(self):
        from korail_api.messages.catalog import resolve_error_message

        return resolve_error_message(self.code, self.message)


def _declare_categories():
    from korail_api.protocol.schema import load

    pending = dict(load("public-interface")["errors"])
    while pending:
        progressed = False
        for name, parents in list(pending.items()):
            parents = ["_ErrorDetails" if p.startswith("_") else p for p in parents]
            if name in globals():
                del pending[name]
                progressed = True
                continue
            if all(p in globals() for p in parents):
                globals()[name] = type(name, tuple(globals()[p] for p in parents), {"__module__": __name__})
                del pending[name]
                progressed = True
        if not progressed:
            raise RuntimeError(f"Unresolved exception hierarchy: {sorted(pending)}")


_declare_categories()

_APP_ERROR_BY_CODE = {code: globals()[name] for code, name in _load_schema("error-categories").items()}


def classify_app_error(code, message, *, raw=None):
    from korail_api.protocol.schema import load

    category = load("error-categories").get(code, "KorailAppError")
    return globals().get(category, KorailAppError)(code, message, raw=raw)
