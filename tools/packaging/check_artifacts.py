"""Verify standalone built artifacts without editable startup hooks."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import sysconfig
import tarfile
import tempfile
import zipfile
from pathlib import Path


def check(wheel: Path, sdist: Path | None = None):
    with tempfile.TemporaryDirectory(prefix="korail-independent-artifact-") as temporary:
        work = Path(temporary)
        installed = work / "installed"
        installed.mkdir()
        with zipfile.ZipFile(wheel) as archive:
            names = archive.namelist()
            assert any(n.endswith("/licenses/NOTICE") for n in names)
            assert any(n.endswith("/licenses/THIRD_PARTY_NOTICES.md") for n in names)
            assert any(n.endswith("/licenses/LICENSE") for n in names)
            top_level = next(n for n in names if n.endswith(".dist-info/top_level.txt"))
            assert archive.read(top_level).decode().split() == ["korail_api"]
            assert any(n.endswith("korail_api/models/records.pyi") for n in names)
            assert not any(
                n.endswith(".apk")
                or "parser-observations" in n
                or n.startswith(
                    (
                        "reference/",
                        "tools/compatibility/",
                        "tools/performance/",
                        "tools/reports/",
                        "tools/validation/",
                    )
                )
                for n in names
            )
        subprocess.run(
            [
                sys.executable,
                "-I",
                "-m",
                "pip",
                "--isolated",
                "install",
                "--no-index",
                "--no-deps",
                "--no-compile",
                "--disable-pip-version-check",
                "--target",
                str(installed),
                str(wheel),
            ],
            cwd=work,
            capture_output=True,
            text=True,
            check=True,
        )
        site = sysconfig.get_paths()["purelib"]
        bootstrap = f"import sys;sys.path[:0] = {[str(installed), site]!r};"
        smoke = """
import json, pathlib, pickle, httpx
import korail_api as api
from importlib.metadata import distribution
assert len(api.__all__) == 239
root = pathlib.Path(api.__file__).resolve().parents[1]
for name, module in list(sys.modules.items()):
    if name.startswith('korail_api') and getattr(module, '__file__', None):
        assert pathlib.Path(module.__file__).resolve().is_relative_to(root), (name, module.__file__)
raw = {'strResult': 'SUCC', 'h_next_pg_flg': 'N', 'trn_infos': {'trn_info': [{'h_trn_no': '90001'}]}}
with api.KorailClient(api.KorailConfig(netfunnel_enabled=False), transport=httpx.MockTransport(lambda request: httpx.Response(200, json=raw))) as client:
    result = client.search_trains(api.TrainSearchQuery('서울', '부산', '20991230', '090000'))
    assert result.trains[0].train_no == '90001' and result.raw == raw
assert pickle.loads(pickle.dumps(result)) == result
assert api.get_error_message('S003') is not None
assert distribution('korail-api').metadata['Name'] == 'korail-api'
assert api.__version__ == distribution('korail-api').version
print(json.dumps({'isolated_wheel': 'passed', 'exports': len(api.__all__), 'package': str(root)}))
"""
        result = subprocess.run(
            [sys.executable, "-I", "-S", "-c", bootstrap + smoke],
            cwd=work,
            capture_output=True,
            text=True,
            check=True,
        )
        print(result.stdout.strip())
        if sdist is not None:
            source = work / "source"
            source.mkdir()
            with tarfile.open(sdist) as archive:
                names = archive.getnames()
                assert any(n.endswith("/LICENSE") for n in names)
                assert any(n.endswith("/NOTICE") for n in names)
                assert any(n.endswith("/THIRD_PARTY_NOTICES.md") for n in names)
                assert not any(
                    "parser-observations" in n
                    or "/reference/" in n
                    or "/tools/compatibility/" in n
                    or "/tools/performance/" in n
                    or "/tools/reports/" in n
                    or "/tools/validation/" in n
                    or n.endswith(".apk")
                    for n in names
                )
                source_packages = {
                    n.split("/src/", 1)[1].split("/", 1)[0]
                    for n in names
                    if "/src/" in n and not n.split("/src/", 1)[1].split("/", 1)[0].endswith(".egg-info")
                }
                assert source_packages == {"korail_api"}
                archive.extractall(source, filter="data")
            project = next(source.iterdir())
            bootstrap = f"import sys;sys.path[:0] = {[str(project / 'src'), site]!r};"
            invocation = (
                bootstrap
                + f'import pytest;sys.exit(pytest.main(["-q", "-c", {str(project / "pyproject.toml")!r}, {str(project / "tests")!r}]))'
            )
            result = subprocess.run(
                [sys.executable, "-I", "-S", "-c", invocation],
                cwd=work,
                capture_output=True,
                text=True,
                check=True,
            )
            print(result.stdout.strip())
    return {"wheel": wheel.name, "sdist": sdist.name if sdist else None, "status": "passed"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("wheel", type=Path)
    parser.add_argument("--sdist", type=Path)
    args = parser.parse_args()
    print(json.dumps(check(args.wheel.resolve(), args.sdist.resolve() if args.sdist else None)))
