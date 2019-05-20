#!/usr/bin/env python

# Coded for both python2 and python3.

'''
Create release notes for a new release of the GitHub repository.
'''

from __future__ import print_function
from datetime import datetime
import os
import github       # pip install pygithub or conda install -c conda-forge pygithub
import collections
import argparse


CREDS_FILE_NAME = "__github_creds__.txt"
# GITHUB_ORGANIZATION = "BCDA-APS"        # see below, after get_GitHub_org_and_repo()
# GITHUB_REPOSITORY = "apstools"
GITHUB_PER_PAGE = 30


def str2time(time_string):
    # Tue, 20 Dec 2016 17:35:40 GMT
    fmt = "%a, %d %b %Y %H:%M:%S %Z"
    return datetime.strptime(time_string, fmt)


def find_creds_file(fname):
    candidates = [os.path.dirname(__file__),]
    home = os.environ.get("HOME")
    if home is not None:
        candidates.append(os.path.join(home, ".config"))
    for path in candidates:
        filename = os.path.join(path, fname)
        if os.path.exists(filename):
            return filename
    raise ValueError('Missing file: ' + fname)


def get_GitHub_org_and_repo():
    """
    get the GitHub organization name and repository name
    
    Simplistic search of ``<root>/.git/config``::

        [remote "origin"]
            url = https://github.com/BCDA-APS/apstools
            fetch = +refs/heads/*:refs/remotes/origin/*
    """
    config_file = os.path.join(os.path.dirname(__file__), ".git", "config")
    if not os.path.exists(config_file):
        msg = "Could not find file: " + config_file
        raise RuntimeError(msg)
    
    with open(config_file, "r") as fp:
        get_next_url = False        # a trigger
        for line in fp.readlines():
            text = line.strip()
            if text == '[remote "origin"]':
                get_next_url = True
            elif get_next_url and text.startswith("url = https://github.com/"):
                org, repo = text.split("/")[-2:]
                repo = os.path.splitext(repo)[0]
                return org, repo
        msg = "Could not find GitHub info in: " + config_file
        raise RuntimeError(msg)


GITHUB_ORGANIZATION, GITHUB_REPOSITORY = get_GitHub_org_and_repo()


class ReleaseNotes(object):
    
    def __init__(self, base, head=None, milestone=None):
        self.base = base
        self.head = head or "master"
        self.milestone_title = milestone
        self.milestone = None

        self.commit_db = {}
        self.db = dict(tags={}, pulls={}, issues={}, commits={})
        self.creds_file_name = find_creds_file(CREDS_FILE_NAME)
    
    def connect(self):
        uname, pwd = open(self.creds_file_name, 'r').read().split()
        self.gh = github.Github(uname, password=pwd, per_page=GITHUB_PER_PAGE)
        self.user = self.gh.get_user(GITHUB_ORGANIZATION)
        self.repo = self.user.get_repo(GITHUB_REPOSITORY)
    
    def learn(self):
        base_commit = None
        earliest = None
        compare = self.repo.compare(self.base, self.head)
        commits = self.db["commits"] = collections.OrderedDict()
        for commit in compare.commits:
            commits[commit.sha] = commit
#         commits = self.db["commits"] = {commit.sha: commit for commit in compare.commits}
        
        for milestone in self.repo.get_milestones():
            if milestone.title == self.milestone_title:
                self.milestone = milestone

        tags = self.db["tags"]
        for tag in self.repo.get_tags():
            if tag.commit.sha in commits:
                tags[tag.name] = tag
            elif tag.name == self.base:
                base_commit = self.repo.get_commit(tag.commit.sha)
                earliest = str2time(base_commit.last_modified)

        pulls = self.db["pulls"]
        for pull in self.repo.get_pulls(state="closed"):
            if pull.closed_at > earliest:
                pulls[pull.number] = pull

        issues = self.db["issues"]
        for issue in self.repo.get_issues(milestone=self.milestone, state="closed"):
            if self.milestone is not None or issue.closed_at > earliest:
                if issue.number not in pulls:
                    issues[issue.number] = issue

    def print_report(self):
        print("## " + self.milestone_title)
        print("")
        if self.milestone is not None:
            print("**milestone**: [%s](%s)" % (self.milestone.title, self.milestone.url))
            print("")
        print("section | number")
        print("-"*5, " | ", "-"*5)
        print("New Tags | ", len(self.db["tags"]))
        print("Pull Requests | ", len(self.db["pulls"]))
        print("Issues | ", len(self.db["issues"]))
        print("Commits | ", len(self.db["commits"]))
        print("")
        print("### Tags")
        print("")
        for k, tag in sorted(self.db["tags"].items()):
            print("* [%s](%s) %s" % (tag.commit.sha[:7], tag.commit.html_url, k))
        print("")
        print("### Pull Requests")
        print("")
        for k, pull in sorted(self.db["pulls"].items()):
            state = {True: "merged", False: "closed"}[pull.merged]
            print("* [#%d](%s) (%s) %s" % (pull.number, pull.html_url, state, pull.title))
        print("")
        print("### Issues")
        print("")
        for k, issue in sorted(self.db["issues"].items()):
            if k not in self.db["pulls"]:
                print("* [#%d](%s) %s" % (issue.number, issue.html_url, issue.title))
        print("")
        print("### Commits")
        print("")
        for k, commit in self.db["commits"].items():
            message = commit.commit.message.splitlines()[0]
            print("* [%s](%s) %s" % (k[:7], commit.html_url, message))
        print("")


def main(base="2017.711.0", head="master", milestone="2017-09 release"):
    # github.enable_console_debug_logging()
    notes = ReleaseNotes(base, head=head, milestone=milestone)
    notes.connect()
    notes.learn()
    notes.print_report()


def parse_command_line():
    doc = __doc__.strip()
    parser = argparse.ArgumentParser(description=doc)

    help_text = "name of tag to start the range"
    parser.add_argument('base', action='store', help=help_text)

    help_text = "name of milestone"
    parser.add_argument('milestone', action='store', help=help_text)

    help_text = "name of tag, branch, SHA to end the range"
    help_text += ' (default="master")'
    parser.add_argument(
        "--head", 
        action='store', 
        dest='head',
        nargs='?', 
        help = help_text, 
        default="master")

    return parser.parse_args()


if __name__ == '__main__':
    cmd = parse_command_line()
    main(cmd.base, head=cmd.head, milestone=cmd.milestone)
