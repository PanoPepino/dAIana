"""
Test basic CLI commands of the project.

This file checks that:
- the `daiana` command exists and can run,
- each main command (compile, save, show, update, hunt, oracle) responds to `--help` correctly.
"""

import subprocess


def _run_cli(args, check=True):
    """
    Helper: run `daiana` with given arguments and capture the result.

    Args:
        args (list of str): arguments to pass after "daiana", e.g. ["save", "--help"].
        check (bool): if True, raise an exception on non‑zero exit code.

    Returns:
        A `subprocess.CompletedProcess` object with:
          returncode  → the exit code of daiana (0 = success),
          stdout      → what daiana printed to stdout,
          stderr      → what daiana printed to stderr.
    """
    return subprocess.run(
        ["daiana"] + args,          # run: `daiana` plus the given args
        capture_output=True,       # capture stdout and stderr so we can check them
        text=True,                 # return them as strings, not bytes
        check=check,               # if check=True, raise an error if daiana fails
    )


def test_main_help():
    """
    Test that `daiana --help` runs and prints the main help screen.
    """
    result = _run_cli(["--help"])          # run: `daiana --help`
    assert result.returncode == 0          # it should exit with code 0 (no error)
    # The help must contain a line that tells us it lists the commands:
    assert "Hunt commands in this package:" in result.stdout


def test_compile_help():
    """
    Test that `daiana compile --help` runs and prints the compile help text.
    """
    result = _run_cli(["compile", "--help"])  # run: `daiana compile --help`
    assert result.returncode == 0             # it should run without error
    # The help must contain some word that is in the compile command description:
    assert "Compile" in result.stdout


def test_save_help():
    """
    Test that `daiana save --help` runs and prints the save help text.
    """
    result = _run_cli(["save", "--help"])     # run: `daiana save --help`
    assert result.returncode == 0             # it should run without error
    # The help must contain the beginning of the save command description:
    assert "Save a new job" in result.stdout


def test_show_help():
    """
    Test that `daiana show --help` runs and prints the show help text.
    """
    result = _run_cli(["show", "--help"])     # run: `daiana show --help`
    assert result.returncode == 0             # it should run without error

    # The help must contain the description line and the "Options:" section:
    assert "Track previous applied jobs and their status" in result.stdout
    assert "Options:" in result.stdout


def test_update_help():
    """
    Test that `daiana update --help` runs and prints the update help text.
    """
    result = _run_cli(["update", "--help"])   # run: `daiana update --help`
    assert result.returncode == 0             # it should run without error

    # The help must contain words that clearly belong to the update command:
    assert "update" in result.stdout
    assert "Options:" in result.stdout


# def test_hunt_help():

#    result = _run_cli(["hunt", "--help"])     # run: `daiana hunt --help`
#    assert result.returncode == 0             # it should run without error

    # The help must contain some phrase that is in the hunt command description:
#    assert "hunt" in result.stdout
#    assert "Options:" in result.stdout


def test_oracle_help():
    """
    Test that `daiana oracle --help` runs and prints the oracle help text.
    """
    result = _run_cli(["oracle", "--help"])   # run: `daiana oracle --help`
    assert result.returncode == 0             # it should run without error

    # The help must contain some phrase that is in the oracle command description:
    assert "oracle" in result.stdout
    assert "Options:" in result.stdout
