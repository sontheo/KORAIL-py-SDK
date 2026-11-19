"""Login password transformation using standard AES-CBC and Android Base64."""

import base64

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.padding import PKCS7

from korail_py_sdk.models.errors import KorailProtocolError


def transform_login_password(password, info):
    if not isinstance(password, str) or not isinstance(info.key, str):
        raise KorailProtocolError("Password and encryption key must be text")
    try:
        key = info.key.encode("utf-8")
        padder = PKCS7(128).padder()
        clear = padder.update(password.encode("utf-8")) + padder.finalize()
        cipher = Cipher(algorithms.AES(key), modes.CBC(key[:16])).encryptor()
        encrypted = cipher.update(clear) + cipher.finalize()
    except (ValueError, UnicodeError) as error:
        raise KorailProtocolError("Invalid login encryption parameters") from error
    return base64.encodebytes(base64.b64encode(encrypted)).decode("ascii")
