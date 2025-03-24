#!/usr/bin/env nix-shell
#!nix-shell -i python3 -p python3Packages.gitpython

import sys
import os
import subprocess
import json

import git
import tomllib

from argparse import ArgumentParser


def load_config(file_path):

    file_path = os.path.expanduser(file_path)

    try:
        with open(f"{file_path}", "rb") as f:
            config = tomllib.load(f)
        return config
    except FileNotFoundError:
        print(f"{file_path} not found. Please refer to the help section (--help) for instructions on providing a configuration file.")
        return None
    except tomllib.TOMLDecodeError as e:
        print(f"Error decoding {file_path}: {e}")
        return None


def run_npins_update(name=None):
    try:
        env = os.environ.copy()

        if name:
            subprocess.run(["npins", "update", name], check=True, env=env)
        else:
            subprocess.run(["npins", "update"], check=True, env=env)

        print("npins update completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"npins update failed with error: {e}")


def read_sources_json():
    try:
        with open("npins/sources.json", encoding="utf-8") as f:
            sources = json.load(f)

            if sources["version"] is None or sources["version"] not in [3, 4, 5]:
                print("unsupported npins sources version")
                sys.exit(1)

            if sources["pins"] is None:
                print("no npins sources found")
                sys.exit(1)

        return sources["pins"]

    except FileNotFoundError:
        print("sources.json file not found.")
        return None
    except json.JSONDecodeError as e:
        print(f"Error decoding sources.json: {e}")
        return None


def repo_fetch(repo_path=".", remote_name=""):
    try:
        repo = git.Repo(f"{repo_path}", search_parent_directories=True)
        if remote_name:
            repo.git.fetch(remote_name)
        else:
            repo.git.fetch()
        print("Repo fetch completed successfully.")
        return True
    except Exception as e:
        print(f"Error fetching repo: {e}")
        return False


def check_uncommitted_changes(file_path):
    try:
        repo = git.Repo(".", search_parent_directories=True)
        changed_files = [item.a_path for item in repo.index.diff(None)]
        if file_path in changed_files:
            print(f"There are uncommitted changes in {file_path}.")
            return True
        # print('No uncommitted changes.')
        return False
    except Exception as e:
        print(f"Error checking uncommitted changes: {e}")
        return False


def check_staged_files():
    try:
        repo = git.Repo(".", search_parent_directories=True)
        staged_files = [item.a_path for item in repo.index.diff("HEAD")]
        if staged_files:
            print(
                "Error: There are already staged files. Please commit or unstage them before proceeding."
            )
            return True
        return False
    except Exception as e:
        print(f"Error checking staged files: {e}")
        return True


def get_first_line_with_ellipsis(message):
    lines = message.split("\n")
    if len(lines) > 1:
        return lines[0] + " ..."
    return lines[0]


def commit_file(file_path, message, sign=False):
    try:
        repo = git.Repo(".", search_parent_directories=True)
        repo.index.add([file_path])
        if sign:
            repo.index.write()
            repo.git.commit("-m", message, "-S")
        else:
            repo.index.commit(message)
        print(
            f'Committed {file_path} with message: "{get_first_line_with_ellipsis(message)}"'
        )
    except Exception as e:
        print(f"Error committing file: {e}")


def find_matching_repo_config(long_url, config_repo):
    best_match = None
    longest_match_length = 0

    for _, key in config_repo.items():
        if key["url"] in long_url:
            match_length = len(key["url"])
            if match_length > longest_match_length:
                longest_match_length = match_length
                best_match = key

    return best_match


def get_log(repo_path, old_rev, new_rev):
    try:
        repo = git.Repo(f"{repo_path}", search_parent_directories=True)

        output = repo.git.log("--oneline", "--no-decorate", "--no-merges", f"{old_rev}..{new_rev}")
        return output
    except Exception as e:
        print(f"Error getting log: {e}")
        sys.exit(1)


def arg_parser():
    parser = ArgumentParser(description="Update npins sources and commit changes with a changelog")

    parser.add_argument('PACKAGE', type=str, help='The repo to update, if none is provided it will update all', nargs='?')

    parser.add_argument("--no-changelog", action="store_false",
                        help="do not create a changelog")

    parser.add_argument("-c", "--config", dest="config",
                        help="provide a config file, default is ~/.config/npins-updater/config.toml",
                        metavar="CONFIG", default="~/.config/npins-updater/config.toml")

    parser.add_argument("-S", "--sign", action="store_true", help="GPG-sign commits.")

    return parser.parse_args()


def main():
    file = "npins/sources.json"

    args = arg_parser()

    config = load_config(args.config)

    if config is None:
        sys.exit(1)

    # Check that there are no staged files
    if check_staged_files():
        sys.exit(1)

    # check that we don't overwrite uncommitted changes
    if check_uncommitted_changes(file):
        sys.exit(1)

    # read sources.json
    sources = read_sources_json()
    if sources is None:
        sys.exit(1)

    # if a package is provided, only try updating that package
    if args.PACKAGE:
        if args.PACKAGE not in sources:
            print(f"Error: {args.PACKAGE} not found in sources.json")
            sys.exit(1)
        print(f"Updating {args.PACKAGE}")
        sources = {args.PACKAGE: sources[args.PACKAGE]}

    # process sources one by one
    for name in sources:
        source = sources[name]
        # print(f"proccessing {name}")

        old_rev = source["revision"]

        if (source["type"].lower() != "Git".lower()):
            print(f"Error: {name} is not a Git source")
            continue

        run_npins_update(name)

        # read sources.json again
        new_sources = read_sources_json()
        if new_sources is None:
            sys.exit(1)

        new_source = new_sources[name]

        new_rev = new_source["revision"]

        if old_rev == new_rev:
            print(f"no changes for {name} detected")
            continue

        commit_message = f"npins: update {name}"

        if source["repository"]["type"] == "GitHub":
            if not new_source["repository"]["owner"] and not new_source["repository"]["repo"]:
                print(f"Error: owner and or repo not found for {name} in {file}")

            commit_message += f'\n\nView changes: https://github.com/{new_source["repository"]["owner"]}/{new_source["repository"]["repo"]}/compare/{old_rev}...{new_rev}'

        if args.no_changelog:

            repo_url = new_source["url"] if new_source["url"] is not None else new_source["repository"]["url"];

            config_repo = find_matching_repo_config(repo_url, config["repo"])

            if config_repo is None:
                print(f"No config match found for {new_source['url']}")
                sys.exit(1)

            repo_path = ""
            if "path" in config_repo:
                repo_path = config_repo["path"]

            if repo_path == "":
                print(f"No path found in config for {new_source['url']}")
                sys.exit(1)

            fetch = True;
            if "fetch" in config_repo:
                fetch = config_repo["fetch"]

            if fetch is True:
                print("Fetching repo")
                if repo_fetch(repo_path) is False:
                    print("Error fetching repo")
                    sys.exit(1)
            elif fetch is not False:
                print(f"fetching repo from {fetch}")
                if repo_fetch(repo_path, fetch) is False:
                    print("Error fetching repo")
                    sys.exit(1)

            log_result = get_log(repo_path, old_rev, new_rev)

            commit_message += f"\n\nChangelog:\n\n{log_result}"

        commit_file(file, commit_message, args.sign)


if __name__ == "__main__":
    main()
