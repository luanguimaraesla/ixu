from flask import Flask

from ..base import BaseCommand
from .server import Server


class UpServerCommand(BaseCommand):
    def __init__(self):
        self.server = Server()

    def execute(self, *args, **kwargs):
        self.server.run()

    def get_root(self):
        return 'server'

    def get_name(self):
        return 'up'
