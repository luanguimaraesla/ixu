import os
import logging
from collections import defaultdict

from flask import Flask, make_response, request, jsonify, url_for, redirect
from functools import partial
from gevent.pywsgi import WSGIServer

from ...gitlab.api import Gitlab
from ...exporter.metrics import Exporter

registered_routes = {}


def register_route(route=None, methods=None):
    """
    Simple decorator for class based views
    """
    def inner(fn):
        registered_routes[route] = fn, methods
        return fn
    return inner


class Server(Flask):
    def __init__(self, *args, **kwargs):
        Flask.__init__(self, Server.__name__)
        self.host = os.environ.get("IXU_HOST", "0.0.0.0")
        self.port = int(os.environ.get("IXU_PORT", 8080))
        self.project_id = os.environ.get("IXU_GITLAB_PROJECT_ID")

        for route, action in registered_routes.items():
            fn, methods = action
            partial_fn = partial(fn, self)
            partial_fn.__name__ = fn.__name__
            self.route(route, methods=methods)(partial_fn)

    def run(self):
        logging.info(f'ixu server listening to {self.host}:{self.port}')
        http_server = WSGIServer((self.host, self.port), self)
        http_server.serve_forever()

    @register_route("/health", ['GET'])
    def health(self):
        response = {'ok': "I am here!"}
        return jsonify(response)

    @register_route("/issues", ['GET'])
    def issues(self):
        gitlab = Gitlab()
        project = gitlab.get_project(self.project_id)
        issues = project.get_issues()

        labels = defaultdict(list)
        for issue in issues:
            for label in issue.labels:
                labels[label].append(issue.title)

        response = jsonify({
            'result': labels,
        })

        return response

    @register_route("/export", ['GET'])
    def export(self):
        '''
        Openmetrics endpoint that exports useful metrics related
        to some Gitlab project
        '''

        # get data from gitlab
        gitlab = Gitlab()
        project = gitlab.get_project(self.project_id)
        issues = project.get_issues()

        # create the exporter
        exp = Exporter()

        # build metrics
        self.build_metrics_gitlab_issues_by_label(exp, issues)
        self.build_metrics_gitlab_issues_by_milestone(exp, issues)
        self.build_metrics_gitlab_issues_by_weight(exp, issues)
        self.build_metrics_gitlab_issues_weight_by_assignee(exp, issues)

        # return content
        content = str(exp)
        response = make_response(content, 200)
        response.mimetype = "text/plain"

        return response

    def build_metrics_gitlab_issues_by_label(self, exp, issues):
        '''
        Exports Gilab issues gauge spplited by labels
        '''

        for issue in issues:
            for label in issue.labels:
                exp.gauge(
                    "gitlab_issues_by_label",
                    "Issues by label"
                ).add(
                    num=1,
                    tags={
                        "label": label,
                        "state": issue.state,
                    }
                )

    def build_metrics_gitlab_issues_by_milestone(self, exp, issues):
        '''
        Exports Gilab issues gauge spplited by milestone titles
        '''

        for issue in issues:
            exp.gauge(
                "gitlab_issues_by_milestone",
                "Issues by milestone titles"
            ).add(
                num=1,
                tags={
                    "milestone": issue.milestone['title'] if issue.milestone else "None",
                    "state": issue.state,
                    "author": issue.author['username'],
                }
            )

    def build_metrics_gitlab_issues_by_weight(self, exp, issues):
        '''
        Exports Gilab issues gauge spplited by weight
        '''

        for issue in issues:
            for assignee in issue.assignees:
                exp.gauge(
                    "gitlab_issues_by_weight",
                    "Issues by weight and assignee"
                ).add(
                    num=1,
                    tags={
                        "state": issue.state,
                        "weight": str(issue.weight),
                        "assignee": assignee["username"],
                    }
                )

    def build_metrics_gitlab_issues_weight_by_assignee(self, exp, issues):
        '''
        Exports Gilab issues weight by assignee
        '''

        for issue in issues:
            if issue.weight:
                for assignee in issue.assignees:
                    exp.gauge(
                        "gitlab_issues_weight_by_assignee",
                        "Total issues weight by assignee"
                    ).add(
                        num=issue.weight,
                        tags={
                            "state": issue.state,
                            "assignee": assignee["username"],
                        }
                    )
