import copy
import os
from redispy.errors import TimeoutError


def io(func):
    def _(*args):
        try:
            func(*args)
        except TimeoutError:
            pass
    return _


class Client(object):

    """docstring for Client"""
    DEFAULTS = {


    }

    @property
    def options():
        return copy.deepcopy(self.options)

    @property
    def scheme(self):
        return self.options['scheme']

    @property
    def host(self):
        return self.options['host']

    @property
    def port(self):
        return self.options['port']

    def __init__(self, **kwargs):
        self.options = kwargs
        self.reconnect = True
        self.connection = None
        self.command_map = {}
        self.proile = profile.autoload(self.kwargs['redis_ver'])

    def connect(self):
        self.pid = os.getpid()

        self.connection = self.adapter(self.options['adapter'])

    def adapter(self, adapter):
        pass

    def disconnect(self):
        if self.connected:
            self.connection.disconnect()

    def __getattr__(self, cmd):

        def _(*args, **kwargs):

            cmd = self.proile.get(cmd)
            cmd.bind(args, kwargs)
            self.write(cmd)
            self.read(cmd)
            return cmd.response()
        return _

    @io
    def read(self, command):
        self.connection.read(cmd)

    @io
    def write(self, command):
        self.connection.write(command)
