"""Radix-based v1 protocol serialization, separate from HTTP and session state.

The wire uses seven-bit character atoms, base-161 blocks, base-30 output,
and a factoradic permutation for each message's alphabet.
"""

import secrets
import string
import time
from collections import deque
from functools import lru_cache
from urllib.parse import quote_plus

from korail_py_sdk.models.errors import KorailProtocolError
from korail_py_sdk.protocol.schema import load


def string_to_xa1s(data):
    atoms = []
    for cp in map(ord, data):
        if 0xD800 <= cp <= 0xDFFF:
            continue
        if cp < 128:
            atoms.append(cp)
            continue
        length = 2 if cp < 2048 else 3 if cp < 262144 else 4
        atoms.append((128, 144, 160)[length - 2] | ((cp >> (7 * (length - 1))) & 15))
        atoms.extend((cp >> shift) & 127 for shift in range(7 * (length - 2), -1, -7))
    return atoms


def make_dynapath_key(text):
    seed = 0
    for cp in map(ord, text):
        low_word = cp & 65535
        seed = (seed << low_word.bit_length()) + cp if low_word else cp
    return seed


@lru_cache(maxsize=64)
def make_encode_table(seed, radix, alphabet):
    pool = list(alphabet[:radix])
    selected = []
    for size in range(radix, 0, -1):
        seed, index = divmod(seed, size)
        selected.append(pool.pop(index))
    return "".join(selected)


def encode_normal_be(data, table, *, i8=161, i9=30, i10=2):
    if i10 < 1 or i9 < 2 or len(table) < i9:
        raise KorailProtocolError("Invalid protocol radix settings")
    atoms = data.encode("ascii") if data.isascii() else string_to_xa1s(data)
    symbols = []
    if i10 == 2:
        for offset in range(0, len(atoms), 2):
            block = atoms[offset : offset + 2]
            packed = block[0] * i8 + block[1] if len(block) == 2 else block[0]
            if len(block) == 2:
                symbols.append(table[(packed // (i9 * i9)) % i9])
            symbols.extend((table[(packed // i9) % i9], table[packed % i9]))
        return "".join(symbols)
    for offset in range(0, len(atoms), i10):
        block = atoms[offset : offset + i10]
        packed = sum(atom * (i8 ** (len(block) - index - 1)) for index, atom in enumerate(block))
        symbols.extend(table[(packed // (i9**exponent)) % i9] for exponent in range(len(block), -1, -1))
    return "".join(symbols)


def build_dynapath_prefix(*, table, table_index=1, i11=2, i12=30):
    return chr(97 + table_index) + "".join(table[index] for index in (2, 37, i11, i12 - 1))


def java_urlencode(value):
    return quote_plus(value, safe="*").replace("~", "%7E")


def generate_dynapath_token(settings, *, timestamp_ms=None, random_text=None, recent_intervals=()):
    stamp = int(time.time() * 1000) if timestamp_ms is None else timestamp_ms
    noise = (
        "".join(secrets.choice(string.ascii_letters + string.digits) for _ in range(4))
        if random_text is None
        else random_text
    )
    wire_names = (
        ("ai", "app_id"),
        ("di", "device_id"),
        ("as", "as_value"),
        ("su", "secure_user"),
        ("dbg", "debug"),
        ("emu", "emulator"),
        ("hk", "hooked"),
        ("it", "app_start_ts"),
    )
    pairs = [
        (
            key,
            str(getattr(settings, attr)).lower()
            if isinstance(getattr(settings, attr), bool)
            else str(getattr(settings, attr)),
        )
        for key, attr in wire_names
    ]
    pairs.append(("ts", str(stamp)))
    pairs.extend(("rt", str(interval)) for interval in recent_intervals)
    pairs.extend(
        (key, str(getattr(settings, attr)))
        for key, attr in (
            ("os", "os_version"),
            ("dm", "device_model"),
            ("st", "os_type"),
            ("sv", "sdk_version"),
        )
    )
    body = "&".join(java_urlencode(k) + "=" + java_urlencode(v) for k, v in pairs)
    context_key = "+".join((settings.sdk_version, noise, str(stamp)))
    codec = dict(i8=settings.i8, i9=settings.i9, i10=settings.i10)
    head = encode_normal_be(context_key, settings.table, **codec)
    alphabet = make_encode_table(make_dynapath_key(context_key), settings.i9, settings.table)
    return (
        build_dynapath_prefix(
            table=settings.table, table_index=settings.table_index, i11=settings.i10, i12=settings.i9
        )
        + settings.table[len(head)]
        + head
        + encode_normal_be(body, alphabet, **codec)
    )


def generate_dynapath_encoding_table(index=1):
    try:
        return load("legacy-protocol")["alphabets"][str(index)]
    except KeyError:
        raise ValueError("Unsupported protocol alphabet index") from None


class DynapathTokenGenerator:
    def __init__(self, settings, *, timestamp_ms_provider=None, random_text_provider=None):
        self.settings = settings
        self._time = timestamp_ms_provider or (lambda: int(time.time() * 1000))
        self._noise = random_text_provider
        self._previous = int(settings.app_start_ts)
        self._intervals = deque(maxlen=5)

    def __call__(self, context=None):
        now = self._time()
        self._intervals.append(now - self._previous)
        self._previous = now
        return generate_dynapath_token(
            self.settings,
            timestamp_ms=now,
            random_text=self._noise() if self._noise else None,
            recent_intervals=tuple(self._intervals),
        )
