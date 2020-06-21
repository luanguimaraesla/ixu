from . import server

commands = [
    server.up.UpServerCommand().export(),
]


class CommandFinder:
    @staticmethod
    def find(root, name):
        for command in commands:
            if command['root'] == root and command['name'] == name:
                return command['export']
        else:
            raise KeyError("Command not found")
