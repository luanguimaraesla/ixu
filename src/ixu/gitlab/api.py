import os
import requests
import json
from urllib3.exceptions import HTTPError
import logging
import pprint


class MetaGitlab(type):
    __GITLAB_URL = os.environ.get("IXU_GITLAB_URL", "http://gitlab.com/")
    __GITLAB_TOKEN = os.environ.get("IXU_GITLAB_TOKEN")
    __GITLAB_API_PATHS = {
        "projects":
            "/api/v4/projects",
        "project__id":
            "/api/v4/projects/{}",
        "issues__project_id":
            "/api/v4/projects/{}/issues",
        "issue__project_id__issue_iid":
            "/api/v4/projects/{}/issues/{}",
    }

    def __new__(cls, name, bases, dct):
        dct["get"] = MetaGitlab.get
        dct["get_paged"] = MetaGitlab.get_paged
        dct["make_path"] = MetaGitlab.make_path
        dct["remote_update"] = MetaGitlab.remote_update
        dct["update"] = MetaGitlab.update
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
    def get_paged(self, path, per_page, *args):
        if per_page < 1 and per_page > 100:
            logging.fatal("per_page value should be between 1 and 100")

        if path in self.__paths:
            rendered_path = self.__paths[path].format(*args)
            rendered_path += "?pagination=keyset&per_page={}".format(per_page)
        else:
            raise KeyError

        headers = {
            "PRIVATE-TOKEN": self.__token
        }

        url = requests.compat.urljoin(self.__url, rendered_path)
        full_body = []

        while True:
            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                body = json.loads(response.content)
                full_body.extend(body)

                # get the next URL
                next_link = response.links.get("next")
                if next_link is None:
                    break

                url = next_link["url"]

            else:
                raise HTTPError

        return full_body

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

    @staticmethod
    def update(self, body):
        self.__dict__.update(body)


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

    def get_issues(self):
        info = []
        try:
            info = self.get_paged("issues__project_id", 50, self.id)
        except HTTPError as err:
            logging.fatal(err)

        pprint.pprint(info)

        return [GitlabIssue(self, body=issue) for issue in info]



class GitlabIssue(metaclass=MetaGitlab):
    def __init__(self, project, iid=None, body=None):
        self.project = project
        self.load(iid, body)

    def load(self, iid, body):
        if body is None and iid is None:
            logging.fatal("error loading issue without information")

        if body is None:
            try:
                self.remote_update(
                    "issue__project_id__issue_iid",
                    self.project.id,
                    iid
                )
            except (HTTPError, KeyError) as err:
                logging.fatal(err)
        else:
            self.update(body)

    def __str__(self):
        return self.title
