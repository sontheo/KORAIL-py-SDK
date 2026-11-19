"""Session state transitions without automatic account actions or login retries."""

from __future__ import annotations

import re
import time

from korail_py_sdk.models import errors as E
from korail_py_sdk.models.records import KorailSession, LoginCryptoInfo
from korail_py_sdk.protocol.codec import scalar
from korail_py_sdk.protocol.schema import load
from korail_py_sdk.security.passwords import transform_login_password


def infer_login_input_flag(member_no):
    if not isinstance(member_no, str):
        raise E.KorailProtocolError("Login ID must contain digits only or be an email address")
    if re.fullmatch(r"[0-9]+", member_no):
        return "4" if len(member_no) == 11 else "2"
    if re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", member_no):
        return "5"
    raise E.KorailProtocolError("Login ID must contain digits only or be an email address")


class KorailSessionClient:
    def __init__(self, http):
        self.http = http
        self.current = None
        self.pending = None

    def clear(self):
        self.current = None
        self.pending = None
        self.http.cookies.clear()

    def login(self, member_no, password, *, input_flag=None, check_valid_pw="Y", cust_id="", etr_path=""):
        flag = input_flag if input_flag is not None else infer_login_input_flag(member_no)
        self.clear()
        try:
            self.http.post_form(
                "/file/CACHE/MobileService.cache", {"timeStamp": int(time.time() * 1000)}, include_common=False
            )
            config = self.http.config
            codes = load("constants")["KORAIL_COMMON_CODE_BOOTSTRAP_CODES"]["items"]
            bootstrap = self.http.post_form(
                "/classes/com.korail.mobile.common.code.do",
                {
                    "code": codes,
                    "deviceWidth": config.device_width,
                    "deviceHeight": config.device_height,
                    "OSVersion": config.android_sdk_int,
                },
            )
            crypto = bootstrap.raw.get("app.login.cphd")
            if not isinstance(crypto, dict):
                raise E.KorailProtocolError("Login encryption parameters are missing")
            transformed = transform_login_password(
                password,
                LoginCryptoInfo(
                    idx=scalar(crypto.get("idx")),
                    key=scalar(crypto.get("key")),
                    pwd_aes_cphd=scalar(crypto.get("pwdAESCphd")),
                ),
            )
            response = self.http.post_form(
                "/classes/com.korail.mobile.login.Login",
                {
                    "txtInputFlg": flag,
                    "txtMemberNo": member_no,
                    "txtPwd": transformed,
                    "custId": cust_id,
                    "checkValidPw": check_valid_pw,
                    "etrPath": etr_path,
                    "idx": crypto.get("idx"),
                },
                raise_on_fail=False,
            )
            code = response.h_msg_cd
            raw = response.raw
            if code in {"WRC000116", "WRC000420"}:
                error = E.KorailAuthContinuationRequired(
                    raw.get("strRedirectUrl") if isinstance(raw.get("strRedirectUrl"), str) else "", raw=raw
                )
                error.code = code
                self.pending = error
                raise error
            if code not in {"IRZ000001", "S200"}:
                mapped = E.classify_app_error(code, response.h_msg_txt, raw=raw)
                if code == "WRC000390":
                    mapped = E.KorailAccountLockedError(code, response.h_msg_txt, raw=raw)
                if type(mapped) is E.KorailAppError:
                    error = E.KorailAuthError("Login was rejected")
                    error.code, error.message, error.raw = code, response.h_msg_txt, raw
                    raise error
                raise mapped
            cookie = next((c.value for c in self.http.cookies.jar if c.name == "JSESSIONID"), None)
            if not cookie:
                error = E.KorailAuthError("Login did not establish a session")
                error.code, error.raw = code, raw
                raise error

            def identifier(key):
                val = scalar(raw.get(key))
                return val if val and val.strip() else None

            self.current = KorailSession(
                cookie, member_no, raw, identifier("strMbCrdNo"), identifier("strCustNo")
            )
            return self.current
        except E.KorailAuthContinuationRequired:
            raise
        except BaseException:
            self.clear()
            raise

    def logout(self):
        try:
            if self.current is not None:
                self.http.post_form(
                    "/classes/com.korail.mobile.login.Logout",
                    {"timeStamp": int(time.time() * 1000)},
                    raise_on_fail=False,
                )
        finally:
            self.clear()
