import os
import logging
from collections import defaultdict

from flask import Flask, request, jsonify, url_for, redirect
from functools import partial
from gevent.pywsgi import WSGIServer

from ...gitlab.api import Gitlab

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
        self.port = int(os.environ.get("IXU_PORT", "8080"))
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
        print("PROJECT ID: {}".format(self.project_id))
        project = gitlab.get_project(self.project_id)
        milestones = project.get_milestones()
        issues = []
        for milestone in milestones:
            issues = [*issues, *milestone.get_issues()]

        labels = defaultdict(list)
        for issue in issues:
            for label in issue.labels:
                labels[label].append(issue.title)

        response = jsonify({
            'result': labels,
        })

        return response
