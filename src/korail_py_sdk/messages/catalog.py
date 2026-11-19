"""Display text is separate from raw responses and failure classification."""

import re
from html.parser import HTMLParser


class _Text(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.fragments = []
        self.hidden = 0

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style"}:
            self.hidden += 1
        elif tag in {"br", "p", "div", "li"}:
            self.fragments.append("\n")

    def handle_endtag(self, tag):
        if tag in {"script", "style"} and self.hidden:
            self.hidden -= 1
        elif tag in {"p", "div", "li"}:
            self.fragments.append("\n")

    def handle_data(self, data):
        if not self.hidden:
            self.fragments.append(data)


def plain_text(message):
    if not isinstance(message, str):
        return ""
    parser = _Text()
    parser.feed(message)
    return "\n".join(
        re.sub(r"[^\S\n]+", " ", line).strip()
        for line in "".join(parser.fragments).splitlines()
        if line.strip()
    ).strip()


def _locale(language):
    key = language.replace("_", "-").split("-", 1)[0].lower() if isinstance(language, str) else ""
    key = {"jp": "ja", "cn": "zh"}.get(key, key)
    if key not in {"ko", "en", "ja", "zh"}:
        raise ValueError("Unsupported message language")
    return key


def get_error_message(code, *, language="ko"):
    from korail_py_sdk.protocol.schema import load

    locale = _locale(language)
    translations = load("messages").get(code, {})
    return translations.get(locale) or translations.get("ko")


def resolve_error_message(code, message=None, *, language="ko"):
    locale = _locale(language)
    displayed = plain_text(message) or plain_text(get_error_message(code, language=language))
    if displayed:
        return displayed
    if code == "P058":
        return {
            "ko": "로그인이 만료되었습니다. 다시 로그인해 주세요.",
            "en": "Your session has expired. Please log in again.",
            "ja": "ログインの有効期限が切れました。再度ログインしてください。",
            "zh": "登录已过期，请重新登录。",
        }[locale]
    return None
