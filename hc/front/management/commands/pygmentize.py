from __future__ import annotations

from pathlib import Path
from typing import Any

from django.conf import settings
from django.core.management.base import BaseCommand

try:
    from pygments import highlight, lexers
    from pygments.formatters import HtmlFormatter
    from pygments.lexer import Lexer

    have_pygments = True
except ImportError:
    have_pygments = False


def _process(name: str, lexer: Lexer, snippets_dir: Path) -> None:
    source_path = snippets_dir / f"{name}.txt"
    destination_path = snippets_dir / f"{name}.html"
    source = source_path.read_text(encoding="utf-8")
    processed = highlight(source, lexer, HtmlFormatter())
    processed = processed.replace("PING_URL", "{{ ping_url }}")
    processed = processed.replace("SITE_ROOT", "{{ SITE_ROOT }}")
    processed = processed.replace("PING_ENDPOINT", "{{ PING_ENDPOINT }}")
    destination_path.write_text(processed, encoding="utf-8")


class Command(BaseCommand):
    help = "Compiles snippets with Pygments"

    def handle(self, **options: Any) -> None:
        if not have_pygments:
            self.stdout.write("This command requires the Pygments package.")
            self.stdout.write("Please install it with:\n\n")
            self.stdout.write("  pip install Pygments\n\n")
            return

        snippets_dir = settings.BASE_DIR / "templates/front/snippets"
        examples = {
            "bash_curl": lexers.BashLexer(),
            "bash_wget": lexers.BashLexer(),
            "browser": lexers.JavascriptLexer(),
            "cs": lexers.CSharpLexer(),
            "node": lexers.JavascriptLexer(),
            "go": lexers.GoLexer(),
            "python_urllib2": lexers.PythonLexer(),
            "python_requests": lexers.PythonLexer(),
            "python_requests_fail": lexers.PythonLexer(),
            "python_requests_start": lexers.PythonLexer(),
            "python_requests_payload": lexers.PythonLexer(),
            "php": lexers.PhpLexer(startinline=True),
            "powershell": lexers.shell.PowerShellLexer(),
            "powershell_inline": lexers.shell.BashLexer(),
            "ruby": lexers.RubyLexer(),
        }
        for name, lexer in examples.items():
            _process(name, lexer, snippets_dir)
