"""Build a message data file directly from an explicitly supplied application APK."""

import argparse
import hashlib
import json
import re
import zipfile
from pathlib import Path

RESULT_IDENTIFIER = re.compile(r"(?:[A-Z]{1,6}[0-9]+|S-ERR[0-9]+|API\.[A-Z][0-9]+|SEMGTK|SUPDATE)\Z")
LANGUAGES = {"en": "EN", "ja": "JP", "zh": "CN"}


def extract(apk, version, target):
    resource = "assets/error_json.json"
    with zipfile.ZipFile(apk) as archive:
        source = archive.read(resource)
    data = json.loads(source)
    if not isinstance(data, dict) or any(
        not isinstance(k, str) or not isinstance(v, str) for k, v in data.items()
    ):
        raise ValueError("The message resource must map identifiers to text")
    messages = {}
    for code, message in data.items():
        if RESULT_IDENTIFIER.fullmatch(code):
            translations = {"ko": message}
            translations.update(
                {
                    language: data[code + suffix]
                    for language, suffix in LANGUAGES.items()
                    if code + suffix in data
                }
            )
            messages[code] = translations
    target.mkdir(parents=True, exist_ok=True)
    (target / "messages.json").write_text(
        json.dumps(messages, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    )
    provenance = {
        "app_version": version,
        "resource": resource,
        "sha256": hashlib.sha256(source).hexdigest(),
        "code_count": len(messages),
        "translation_count": sum(len(t) for t in messages.values()),
        "origin": "KORAIL application message resource; not maintainer-authored text",
    }
    (target / "message-provenance.json").write_text(json.dumps(provenance, indent=2) + "\n")
    return provenance


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("apk", type=Path)
    parser.add_argument("--version", required=True)
    parser.add_argument(
        "--target",
        type=Path,
        default=Path(__file__).resolve().parents[2] / "src/korail_py_sdk/resources/messages",
    )
    options = parser.parse_args()
    print(json.dumps(extract(options.apk, options.version, options.target)))
