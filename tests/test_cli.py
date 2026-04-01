"""
Test basic CLI commands of the project.

This file checks that:
- the `daiana` command exists and can run,
- each main command (compile, save, show, update, hunt, oracle) responds to `--help` correctly.

Note: Click's echo() may route styled output to stderr in non-TTY environments
(e.g. GitHub Actions). All assertions check `stdout + stderr` to be safe.
"""

import subprocess


def _run_cli(args, check=True):
    """
    Helper: run `daiana` with given arguments and capture the result.

    Args:
        args (list of str): arguments to pass after "daiana", e.g. ["save", "--help"].
        check (bool): if True, raise an exception on non-zero exit code.

    Returns:
        A `subprocess.CompletedProcess` object with:
          returncode  -> the exit code of daiana (0 = success),
          stdout      -> what daiana printed to stdout,
          stderr      -> what daiana printed to stderr.
    """
    return subprocess.run(
        ["daiana"] + args,
        capture_output=True,
        text=True,
        check=check,
    )


def test_main_help():
    """
    Test that `daiana --help` runs and prints the main help screen.
    """
    result = _run_cli(["--help"], check=False)
    output = result.stdout + result.stderr  # Click may use stderr in non-TTY envs
    assert result.returncode == 0
    assert "Hunt commands in this package:" in output


def test_compile_help():
    """
    Test that `daiana compile --help` runs and prints the compile help text.
    """
    result = _run_cli(["compile", "--help"], check=False)
    output = result.stdout + result.stderr
    assert result.returncode == 0
    assert "Compile" in output


def test_save_help():
    """
    Test that `daiana save --help` runs and prints the save help text.
    """
    result = _run_cli(["save", "--help"], check=False)
    output = result.stdout + result.stderr
    assert result.returncode == 0
    assert "Save a new job" in output


def test_show_help():
    """
    Test that `daiana show --help` runs and prints the show help text.
    """
    result = _run_cli(["show", "--help"], check=False)
    output = result.stdout + result.stderr
    assert result.returncode == 0
    assert "Track previous applied jobs and their status" in output
    assert "Options:" in output


def test_update_help():
    """
    Test that `daiana update --help` runs and prints the update help text.
    """
    result = _run_cli(["update", "--help"], check=False)
    output = result.stdout + result.stderr
    assert result.returncode == 0
    assert "Update the status of a saved job application" in output
    assert "Options:" in output


def test_hunt_help():
    result = _run_cli(["hunt", "--help"], check=False)
    output = result.stdout + result.stderr
    assert result.returncode == 0
    assert "Ask AI, choose skills, compile documents & track job" in output
    assert "Options:" in output


def test_oracle_help():
    """
    Test that `daiana oracle --help` runs and prints the oracle help text.
    DaianaCommand.format_help() prints the help= string, not the command name,
    so we assert on the actual help text defined in oracler_cli.py.
    """
    result = _run_cli(["oracle", "--help"], check=False)
    output = result.stdout + result.stderr
    assert result.returncode == 0
    assert "Ask AI to tune CV" in output  # from help= in oracler_cli.py
    assert "Options:" in output
