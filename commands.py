'''

'''
import subprocess, shlex

class Command:
    def __init__(self):
        pass

    @staticmethod
    def execute(statement, cwd='.', **kwargs):
        # statement = shlex.split(statement)
        result = subprocess.Popen(
            args=statement,
            cwd=cwd,
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE,
            shell=True,
            **kwargs
        )
        result.wait()
        return result.returncode, result.stdout.read().decode(), result.stderr.read().decode()

class HexoCommand(Command):
    def __init__(self):
        super(HexoCommand, self).__init__()