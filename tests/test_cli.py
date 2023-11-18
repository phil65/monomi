from __future__ import annotations

from jinjarope import cli
from typer.testing import CliRunner


def test_render_with_cli():
    runner = CliRunner()
    result = runner.invoke(
        cli.cli,
        [
            "-i",
            "file://tests/testresources/testfile.jinja",
            "-j",
            "src/jinjarope/resources/tests.toml",
        ],
        catch_exceptions=False,
    )

    assert result.exit_code == 0
    assert "CONTENT!" in result.output
