"""
Test basic CLI commands of the project.

This file checks that:
- the `daiana` command exists and can run,
- the root `daiana` screen shows the custom branded landing screen,
- each main command (compile, save, show, update, hunt, oracle) responds to `--help`.

Note:
Rich / Typer output may differ slightly across environments, so assertions
target stable text fragments rather than exact full blocks.
"""

from __future__ import annotations

import subprocess


def _run_cli(args: list[str], check: bool = True) -> subprocess.CompletedProcess:
    """
    Helper: run `daiana` with given arguments and capture the result.

    Args:
        args: Arguments to pass after "daiana".
        check: If True, raise an exception on non-zero exit code.

    Returns:
        A subprocess.CompletedProcess with returncode, stdout, stderr.
    """
    return subprocess.run(
        ["daiana"] + args,
        capture_output=True,
        text=True,
        check=check,
    )


def _output(result: subprocess.CompletedProcess) -> str:
    return result.stdout + result.stderr


def test_main_help():
    """
    Test that `daiana --help` runs successfully.
    """
    result = _run_cli(["--help"], check=False)
    output = _output(result)

    assert result.returncode == 0
    assert "Usage" in output or "Commands" in output or "dAIana" in output


def test_compile_help():
    """
    Test that `daiana compile --help` runs and prints the compile help text.
    """
    result = _run_cli(["compile", "--help"], check=False)
    output = _output(result)

    assert result.returncode == 0
    assert "Do you want to craft new weapons for your next hunt? Craft it!" in output
    assert "Options" in output


def test_save_help():
    """
    Test that `daiana save --help` runs and prints the save help text.
    """
    result = _run_cli(["save", "--help"], check=False)
    output = _output(result)

    assert result.returncode == 0
    assert "A new job hunt trophy to add to the records? Add it!" in output
    assert "Options" in output


def test_show_help():
    """
    Test that `daiana show --help` runs and prints the show help text.
    """
    result = _run_cli(["show", "--help"], check=False)
    output = _output(result)

    assert result.returncode == 0
    assert "Do you want to see your latest hunt trophies? Show it!" in output
    assert "Options" in output


def test_update_help():
    """
    Test that `daiana update --help` runs and prints the update help text.
    """
    result = _run_cli(["update", "--help"], check=False)
    output = _output(result)

    assert result.returncode == 0
    assert "Information to be updated for your latest prey? Update it!" in output
    assert "Options" in output


def test_hunt_help():
    """
    Test that `daiana hunt --help` runs and prints the hunt help text.
    """
    result = _run_cli(["hunt", "--help"], check=False)
    output = _output(result)

    assert result.returncode == 0
    assert "Ask guidance. Craft weapons. Track job preys. Hunt!" in output
    assert "Options" in output


def test_oracle_help():
    """
    Test that `daiana oracle --help` runs and prints the oracle help text.
    """
    result = _run_cli(["oracle", "--help"], check=False)
    output = _output(result)

    assert result.returncode == 0
    assert "Willing to get guidance from the AI oracle for next hunt? Ask it!" in output
    assert "Options" in output
