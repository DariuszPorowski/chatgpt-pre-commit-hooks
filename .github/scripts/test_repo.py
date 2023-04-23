#!/usr/bin/env python3

from __future__ import annotations

import argparse
import logging
import os
import shutil
import subprocess
import sys
from pathlib import Path
from sys import platform

import yaml

logging.basicConfig(level=logging.DEBUG, format="%(message)s")


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--local", action="store_false", default=False)
    # parser.add_argument("--local", action=argparse.BooleanOptionalAction, default=False)
    parsed, unparsed = parser.parse_known_args()
    return parsed


def get_file_content(src: Path) -> str:
    content = src.open("r", encoding="utf-8").read()
    logging.debug(f"{str(src)}: {content}")
    return content


def clean_test_repo(cwd: Path) -> None:
    shutil.rmtree(cwd)


def prep_test_repo(src: Path, dest: Path, local: bool = False) -> None:
    shutil.rmtree(dest, ignore_errors=True)
    if local:
        os.mkdir(dest)
    else:
        shutil.copytree(src, dest, dirs_exist_ok=True)


def get_git_commit_hash_long(cwd: Path) -> str:
    # git log -n 1 --pretty=format:%H
    return __run_cmd(["git", "log", "-n", "1", "--pretty=format:%H"], cwd=cwd)


def get_git_commit_hash_short(cwd: Path) -> str:
    # git log -n 1 --pretty=format:%h
    return __run_cmd(["git", "log", "-n", "1", "--pretty=format:%h"], cwd=cwd)


def prepare_test_content(cwd: Path) -> None:
    test_file = Path(cwd, "test.md")
    with test_file.open("wt", encoding="utf-8") as handle:
        handle.write("test")
        handle.close()


def set_config_rev(file_path: Path, rev: str) -> None:
    yaml_file_path = Path(file_path)
    with yaml_file_path.open("rt", encoding="utf-8") as handle:
        yaml_content = yaml.safe_load(handle)
        yaml_content["repos"][0]["rev"] = rev
        handle.close()

    with yaml_file_path.open("wt", encoding="utf-8") as handle:
        yaml.safe_dump(yaml_content, handle, indent=2, sort_keys=False, default_flow_style=False)
        handle.close()


def git_init(cwd: Path) -> None:
    # git init
    __run_pcmd(["git", "init"], cwd=cwd)
    # git config --local user.name "github-actions[bot]"
    __run_pcmd(["git", "config", "--local", "user.name", "github-actions[bot]"], cwd=cwd)
    # git config --local user.email "41898282+github-actions[bot]@users.noreply.github.com"
    __run_pcmd(["git", "config", "--local", "user.email", "41898282+github-actions[bot]@users.noreply.github.com"], cwd=cwd)
    # git config --local commit.gpgsign false
    __run_pcmd(["git", "config", "--local", "commit.gpgsign", "false"], cwd=cwd)


def git_stage(cwd: Path) -> None:
    # git add .
    __run_pcmd(["git", "add", "."], cwd=cwd)


def git_commit(cwd: Path, message: str = "Initial commit") -> None:
    # git commit -m "Initial commit"
    __run_pcmd(["git", "commit", "-m", f'"{message}"'], cwd=cwd)


def setup_prehook(cwd: Path) -> None:
    # python -m pip install --upgrade pre-commit
    __run_pcmd(["python", "-m", "pip", "install", "--upgrade", "pre-commit"], cwd=cwd)
    # pre-commit install
    __run_pcmd(["pre-commit", "install"], cwd=cwd)
    # pre-commit clean
    __run_pcmd(["pre-commit", "clean"], cwd=cwd)


def prep_venv(cwd: Path) -> None:
    # python -m venv .venv
    __run_pcmd(["python", "-m", "venv", ".venv"], cwd=cwd)

    logging.debug(f"Platform: {platform}")
    if platform == "win32":
        activate = cwd.joinpath(".venv", "Scripts", "Activate.ps1")
        # __run_cmd(["tree"], cwd=cwd, shell=True)
        activate.chmod(0o777)
        __run_pcmd(["powershell.exe", "-File", str(activate)], cwd=cwd, shell=True)
    else:
        activate = cwd.joinpath(".venv", "bin", "activate")
        # __run_cmd(["tree", "-n"], cwd=cwd, shell=True)
        activate.chmod(0o777)
        __run_pcmd(["source", str(activate)], cwd=cwd, shell=True)


def __run_cmd(commands: list[str], cwd: Path, shell: bool = False) -> str:
    command = " ".join(commands)
    try:
        completed_process = subprocess.run(commands, capture_output=True, encoding="utf-8", check=True, cwd=str(cwd), shell=shell)  # noqa: S603
        stdout = completed_process.stdout.strip()
        logging.debug(f"{command}\n{stdout}")
        return stdout
    except subprocess.CalledProcessError as err:
        stderr = err.stderr.strip()
        logging.debug(f"::error {command}\n{stderr}")
        return stderr


def __run_pcmd(commands: list[str], cwd: Path, shell: bool = False) -> str:
    command = " ".join(commands)
    try:
        result = subprocess.Popen(commands, cwd=str(cwd), encoding="utf-8", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=shell)
        stdout, stderr = result.communicate()
        if result.returncode != 0:
            raise subprocess.CalledProcessError(result.returncode, result.args)

        logging.debug(f"{command}\n{stdout}")
        return stdout.strip()
    except subprocess.CalledProcessError as err:
        logging.debug(f"::error {command}\n{err}")
        return err.stderr


def local_repo_try(cwd: Path, dst: Path) -> None:
    # pre-commit try-repo ../chatgpt-pre-commit-hooks chatgpt-commit-message --verbose --all-files \
    # --hook-stage prepare-commit-msg --commit-msg-filename .git/COMMIT_MSG --prepare-commit-message-source message --commit-object-name test"
    __run_pcmd(
        [
            "pre-commit",
            "try-repo",
            str(cwd),
            "chatgpt-commit-message",
            "--verbose",
            "--all-files",
            "--hook-stage",
            "prepare-commit-msg",
            "--commit-msg-filename",
            ".git/COMMIT_MSG",
            "--prepare-commit-message-source",
            "message",
            "--commit-object-name",
            "test",
        ],
        cwd=dst,
    )


args = get_args()

CWD = Path.cwd()
commit_hash_short = get_git_commit_hash_short(CWD)
SRC = CWD.joinpath("tests", "repo")
DST = CWD.parent.joinpath(f"{commit_hash_short}_test_repo")
logging.debug(f"[CWD] {CWD}")
logging.debug(f"[SRC] {SRC}")
logging.debug(f"[DST] {DST}")

prep_test_repo(SRC, DST, args.local)

if args.local:
    git_init(DST)
    prepare_test_content(DST)
    get_file_content(DST.joinpath("test.md"))
    git_stage(DST)
    git_commit(DST)
    get_file_content(DST.joinpath(".git", "COMMIT_EDITMSG"))
    local_repo_try(CWD, DST)
    get_file_content(DST.joinpath(".git", "COMMIT_EDITMSG"))
    get_file_content(DST.joinpath("debug.log"))
    clean_test_repo(DST)
    sys.exit(0)
else:
    git_init(DST)
    commit_hash_long = get_git_commit_hash_long(CWD)
    set_config_rev(DST.joinpath(".pre-commit-config.yaml"), commit_hash_long)
    git_stage(DST)
    git_commit(DST)
    get_file_content(DST.joinpath(".git", "COMMIT_EDITMSG"))
    setup_prehook(DST)
    prepare_test_content(DST)
    get_file_content(DST.joinpath("test.md"))
    git_stage(DST)
    git_commit(DST, "test markdown")
    get_file_content(DST.joinpath("debug.log"))
