import os
import requests
import json
from urllib3.exceptions import HTTPError
import logging


class MetaGitlab(type):
    __GITLAB_URL = os.environ.get("IXU_GITLAB_URL", "http://gitlab.com/")
    __GITLAB_TOKEN = os.environ.get("IXU_GITLAB_TOKEN")
    __GITLAB_API_PATHS = {
        "projects":
            "/api/v4/projects",
        "project__id":
            "/api/v4/projects/{}",
        "milestones__project_id":
            "/api/v4/projects/{}/milestones",
        "milestone__project_id__id":
            "/api/v4/projects/{}/milestones/{}",
        "issues__project_id__milestone_id":
            "/api/v4/projects/{}/milestones/{}/issues",
        "issue__project_id__issue_iid":
            "/api/v4/projects/{}/issues/{}",
    }

    def __new__(cls, name, bases, dct):
        dct["get"] = MetaGitlab.get
        dct["make_path"] = MetaGitlab.make_path
        dct["remote_update"] = MetaGitlab.remote_update
        kls = super().__new__(cls, name, bases, dct)
        kls.__url = MetaGitlab.__GITLAB_URL
        kls.__token = MetaGitlab.__GITLAB_TOKEN
        kls.__paths = MetaGitlab.__GITLAB_API_PATHS

        return kls

    @staticmethod
    def get(self, path, *args):
        if path in self.__paths:
            rendered_path = self.__paths[path].format(*args)
        else:
            raise KeyError

        headers = {
            "PRIVATE-TOKEN": self.__token
        }

        url = requests.compat.urljoin(self.__url, rendered_path)
        response = requests.get(url, headers=headers)

        print("URL: ", url, " CODE: ", response.status_code)

        if response.status_code == 200:
            return json.loads(response.content)

        raise HTTPError

    @staticmethod
    def make_path(self, pattern, *args):
        return pattern.format(*args)

    @staticmethod
    def remote_update(self, path, *args):
        info = {}
        try:
            info = self.get(path, *args)
        except HTTPError as err:
            logging.fatal(err)

        self.__dict__.update(info)


class Gitlab(metaclass=MetaGitlab):
    def get_project(self, project_id):
        return GitlabProject(project_id)


class GitlabProject(metaclass=MetaGitlab):
    def __init__(self, id):
        self.load(id)

    def load(self, id):
        try:
            self.remote_update("project__id", id)
        except (HTTPError, KeyError) as err:
            logging.fatal(err)
            exit(1)

    def get_milestone(self, milestone_id):
        return GitlabMilestone(self, milestone_id)

    def get_milestones(self):
        info = []
        try:
            info = self.get("milestones__project_id", self.id)
        except HTTPError as err:
            logging.fatal(err)

        return [GitlabMilestone(self, milestone["id"]) for milestone in info]


class GitlabMilestone(metaclass=MetaGitlab):
    def __init__(self, project, id):
        self.project = project
        self.load(id)

    def load(self, id):
        try:
            self.remote_update("milestone__project_id__id", self.project.id, id)
        except (HTTPError, KeyError) as err:
            logging.fatal(err)

    def get_issues(self):
        info = []
        try:
            info = self.get(
                "issues__project_id__milestone_id",
                self.project.id,
                self.id
            )
        except HTTPError as err:
            logging.fatal(err)

        return [GitlabIssue(self.project, issue["iid"]) for issue in info]


class GitlabIssue(metaclass=MetaGitlab):
    def __init__(self, project, iid):
        self.project = project
        self.load(iid)

    def load(self, iid):
        try:
            self.remote_update(
                "issue__project_id__issue_iid",
                self.project.id,
                iid
            )
        except (HTTPError, KeyError) as err:
            logging.fatal(err)

    def __str__(self):
        return self.title
