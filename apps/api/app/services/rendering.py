from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape


TEMPLATE_DIR = Path(__file__).resolve().parents[1] / "templates"
jinja_env = Environment(
    loader=FileSystemLoader(str(TEMPLATE_DIR)),
    autoescape=select_autoescape(enabled_extensions=("html", "xml")),
    trim_blocks=True,
    lstrip_blocks=True,
)


def render_mjml(payload: dict[str, Any]) -> str:
    return jinja_env.get_template("newsletter.mjml.j2").render(newsletter=payload)


def render_html_fallback(payload: dict[str, Any]) -> str:
    return jinja_env.get_template("newsletter.html.j2").render(newsletter=payload)


def render_html(payload: dict[str, Any], mjml: str | None = None) -> tuple[str, str]:
    mjml_markup = mjml or render_mjml(payload)
    if shutil.which("mjml") is None:
        return mjml_markup, render_html_fallback(payload)

    with tempfile.NamedTemporaryFile("w+", suffix=".mjml", delete=False) as handle:
        handle.write(mjml_markup)
        handle.flush()
        result = subprocess.run(["mjml", handle.name, "-s"], capture_output=True, text=True, check=False)
    if result.returncode != 0:
        return mjml_markup, render_html_fallback(payload)
    return mjml_markup, result.stdout

