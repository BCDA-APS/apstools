#!/usr/bin/env python

"""
Create release notes for a new release of a GitHub repository.

Run this from the package's root directory.
"""

# Requires:
#
# * assumes current directory is within a repository clone
# * pyGithub (conda or pip install) - https://pygithub.readthedocs.io/
# * Github personal access token (https://github.com/settings/tokens)
#
# Github token access is needed or the GitHub API limit
# will likely interfere with making a complete report
# of the release.

import argparse
import datetime
import github
import logging
import os


logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger("create_release_notes")


def findGitConfigFile():
    """
    return full path to .git/config file

    must be in current working directory or some parent directory

    This is a simplistic search that could be improved by using
    an open source package.

    Needs testing for when things are wrong.
    """
    path = os.getcwd()
    for _i in range(99):
        config_file = os.path.join(path, ".git", "config")
        if os.path.exists(config_file):
            return config_file  # found it!

        # next, look in the parent directory
        path = os.path.abspath(os.path.join(path, ".."))

    msg = "Could not find .git/config file in any parent directory."
    logger.error(msg)
    raise ValueError(msg)


def parse_git_url(url):
    """
    return (organization, repository) tuple from url line of .git/config file
    """
    if url.startswith("git@"):  # deal with git@github.com:org/repo.git
        url = url.split(":")[1]
    org, repo = url.rstrip(".git").split("/")[-2:]
    return org, repo


def getRepositoryInfo():
    """
    return (organization, repository) tuple from .git/config file

    This is a simplistic search that could be improved by using
    an open source package.

    Needs testing for when things are wrong.
    """
    config_file = findGitConfigFile()

    with open(config_file, "r") as f:
        for line in f.readlines():
            line = line.strip()
            if line.startswith("url"):
                url = line.split("=")[-1].strip()
                if url.find("github.com") < 0:
                    msg = "Not a GitHub repo: " + url
                    logger.error(msg)
                    raise ValueError(msg)
                return parse_git_url(url)


def get_release_info(
    token, base_tag_name, head_branch_name, milestone_name
):
    """Mine the Github API for information about this release."""
    organization_name, repository_name = getRepositoryInfo()
    gh = github.Github(token)  # GitHub Personal Access Token

    user = gh.get_user(organization_name)
    logger.debug(f"user: {user}")

    repo = user.get_repo(repository_name)
    logger.debug(f"repo: {repo}")

    milestones = [
        m
        for m in repo.get_milestones(state="all")
        if m.title == milestone_name
    ]
    if len(milestones) == 0:
        msg = f"Could not find milestone: {milestone_name}"
        logger.error(msg)
        raise ValueError(msg)
    milestone = milestones[0]
    logger.debug(f"milestone: {milestone}")

    compare = repo.compare(base_tag_name, head_branch_name)
    logger.debug(f"compare: {compare}")

    commits = {c.sha: c for c in compare.commits}
    logger.debug(f"# commits: {len(commits)}")

    tags = {}
    earliest = None
    for t in repo.get_tags():
        if t.commit.sha in commits:
            tags[t.name] = t
        elif t.name == base_tag_name:
            # PyGitHub oddity:
            #   t.commit == commit
            #   t.commit.last_modified != commit.last_modified
            commit = repo.get_commit(t.commit.sha)
            dt = str2time(commit.last_modified)
            earliest = min(dt, earliest or dt)
    logger.debug(f"# tags: {len(tags)}")

    pulls = {
        p.number: p
        for p in repo.get_pulls(state="closed")
        if p.closed_at > earliest
    }
    logger.debug(f"# pulls: {len(pulls)}")

    issues = {
        i.number: i
        for i in repo.get_issues(milestone=milestone, state="closed")
        if (
            (milestone is not None or i.closed_at > earliest)
            and i.number not in pulls
        )
    }
    logger.debug(f"# issues: {len(issues)}")

    return repo, milestone, tags, pulls, issues, commits


def parse_command_line():
    """Command line argument parser."""
    doc = __doc__.strip()
    parser = argparse.ArgumentParser(description=doc)

    help_text = "name of tag to start the range"
    parser.add_argument("base", action="store", help=help_text)

    help_text = "name of milestone"
    parser.add_argument("milestone", action="store", help=help_text)

    parser.add_argument(
        "token",
        action="store",
        help=(
            "personal access token "
            "(see: https://github.com/settings/tokens)"
        ),
    )

    help_text = "name of tag, branch, SHA to end the range"
    help_text += ' (default="master")'
    parser.add_argument(
        "--head",
        action="store",
        dest="head",
        nargs="?",
        help=help_text,
        default="master",
    )

    return parser.parse_args()


def str2time(time_string):
    """
    Convert date/time string to datetime object.

    input string example: ``Tue, 20 Dec 2016 17:35:40 GMT``
    """
    if time_string is None:
        msg = f"need valid date/time string, not: {time_string}"
        logger.error(msg)
        raise ValueError(msg)
    return datetime.datetime.strptime(
        time_string, "%a, %d %b %Y %H:%M:%S %Z"
    )


def report(title, repo, milestone, tags, pulls, issues, commits):
    print(f"## {title}")
    print("")
    print(f"* **date/time**: {datetime.datetime.now()}")
    print("* **release**: ")
    print("* **documentation**: [PDF]()")
    if milestone is not None:
        print(f"* **milestone**: [{milestone.title}]({milestone.url})")
        print("")
    print("section | quantity")
    print("-" * 5, " | ", "-" * 5)
    print(f"[New Tags](#tags) | {len(tags)}")
    print(f"[Pull Requests](#pull-requests) | {len(pulls)}")
    print(f"[Issues](#issues) | {len(issues)}")
    print(f"[Commits](#commits) | {len(commits)}")
    print("")
    print("### Tags")
    print("")
    if len(tags) == 0:
        print("-- none --")
    else:
        print("tag | date | commit")
        print("-" * 5, " | ", "-" * 5, " | ", "-" * 5)
        for k, tag in sorted(tags.items(), reverse=True):
            commit = repo.get_commit(tag.commit.sha)
            when = str2time(commit.last_modified).strftime("%Y-%m-%d")
            base_url = tag.commit.html_url
            tag_url = "/".join(
                base_url.split("/")[:-2] + ["releases", "tag", k]
            )
            print(
                f"[{k}]({tag_url})"
                f" | {when}"
                f" | [{tag.commit.sha[:7]}]({tag.commit.html_url})"
            )
    print("")
    print("### Pull Requests")
    print("")
    if len(pulls) == 0:
        print("-- none --")
    else:
        print("pull request | date | state | title")
        print("-" * 5, " | ", "-" * 5, " | ", "-" * 5, " | ", "-" * 5)
        for k, pull in sorted(pulls.items(), reverse=True):
            state = {True: "merged", False: "closed"}[pull.merged]
            when = str2time(pull.last_modified).strftime("%Y-%m-%d")
            print(
                f"[#{pull.number}]({pull.html_url}) | {when} | {state} | {pull.title}"
            )
    print("")
    print("### Issues")
    print("")
    if len(issues) == 0:
        print("-- none --")
    else:

        def isorter(o):
            k, v = o
            logger.debug("[closed: %s] %d %s", v.closed_at, k, v.title)
            return v.closed_at

        print("issue | date | title")
        print("-" * 5, " | ", "-" * 5, " | ", "-" * 5)
        for k, issue in sorted(issues.items(), key=isorter, reverse=True):
            if k not in pulls:
                when = issue.closed_at.strftime("%Y-%m-%d")
                print(
                    f"[#{issue.number}]({issue.html_url})"
                    f" | {when}"
                    f" | {issue.title}"
                )
    print("")
    print("### Commits")
    print("")
    if len(commits) == 0:
        print("-- none --")
    else:

        def csorter(o):
            k, v = o
            ts = v.raw_data["commit"]["committer"]["date"]
            logger.debug("[closed: %s] %s", ts, k)
            return v.raw_data["commit"]["committer"]["date"]

        print("commit | date | message")
        print("-" * 5, " | ", "-" * 5, " | ", "-" * 5)
        for k, commit in sorted(
            commits.items(), key=csorter, reverse=True
        ):
            message = commit.commit.message.splitlines()[0]
            when = commit.raw_data["commit"]["committer"]["date"].split(
                "T"
            )[0]
            print(f"[{k[:7]}]({commit.html_url}) | {when} | {message}")


def main(base=None, head=None, milestone=None, token=None, debug=False):
    if debug:
        base_tag_name = base
        head_branch_name = head
        milestone_name = milestone
        logger.setLevel(logging.DEBUG)
    else:
        cmd = parse_command_line()
        base_tag_name = cmd.base
        head_branch_name = cmd.head
        milestone_name = cmd.milestone
        token = cmd.token
        logger.setLevel(logging.WARNING)

    info = get_release_info(
        token, base_tag_name, head_branch_name, milestone_name
    )
    # milestone, repo, tags, pulls, issues, commits = info
    report(milestone_name, *info)


if __name__ == "__main__":
    main()
