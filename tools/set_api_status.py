"""Set the manually maintained KORAIL API status badge shown in README."""

import argparse
from pathlib import Path

STATUS = {
    "on": {
        "label": "OPERATIONAL",
        "color": "#4ade80",
        "halo": "#123d35",
        "border": "#2dd4bf",
        "title": "KORAIL API status: operational (manual)",
    },
    "off": {
        "label": "OFFLINE",
        "color": "#fb7185",
        "halo": "#3f1d26",
        "border": "#fb7185",
        "title": "KORAIL API status: offline (manual)",
    },
}


def render_badge(state: str) -> str:
    values = STATUS[state]
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="390" height="76" viewBox="0 0 390 76" role="img" aria-labelledby="title desc">
<title id="title">{values["title"]}</title>
<desc id="desc">Manually maintained API status. This badge does not probe the live KORAIL service.</desc>
<rect x="1" y="1" width="388" height="74" rx="16" fill="#0b1220" stroke="{values["border"]}" stroke-width="2"/>
<circle cx="36" cy="38" r="16" fill="{values["halo"]}"/>
<circle cx="36" cy="38" r="7" fill="{values["color"]}"/>
<text x="66" y="30" fill="#8ce8d8" font-family="Arial, Helvetica, sans-serif" font-size="11" font-weight="700" letter-spacing="1.6">KORAIL API STATUS</text>
<text x="66" y="53" fill="#f4f9fc" font-family="Arial, Helvetica, sans-serif" font-size="18" font-weight="700" letter-spacing=".5">{values["label"]}</text>
<rect x="292" y="24" width="78" height="28" rx="14" fill="#203c48"/>
<text x="331" y="42" text-anchor="middle" fill="#c6d6df" font-family="Arial, Helvetica, sans-serif" font-size="10" font-weight="700" letter-spacing="1.2">MANUAL</text>
</svg>
'''


def main() -> int:
    parser = argparse.ArgumentParser(description="Set the README's manual KORAIL API status badge.")
    parser.add_argument("state", choices=STATUS, help="show operational status (on) or offline status (off)")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    target = root / "assets" / "api-status.svg"
    target.write_text(render_badge(args.state), encoding="utf-8")
    print(f"API status set to {STATUS[args.state]['label']} in {target.relative_to(root)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
