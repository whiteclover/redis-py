#!/usr/bin/env python


from redispy.errors import ResponseError
from redispy.connection.base import RedisSocket, BaseConnection
import logging

LOGGER = logging.getLogger('connection')


class StreamConnection(BaseConnection):

    def __init__(self, options={}):
        BaseConnection.__init__(self, options)

        self.stream = RedisSocket()

    def __del__(self):
        if self.options.get('persistent'):
            self.disconnect()

    def connect(self):

        if self.init_cmds:
            self.send_initialization_commands()

    def disconect(self):
        self.stream.disconect()

    def send_initialization_commands(self):
        for command in self.initCmds:
            self.write_command(command)

        for command in self.initCmds:
            self.read_response(command)

    def write(self, data):
        sock = self.get_resource()
        return sock.write(data)

    def read(self):
        sock = self.get_resource()
        line = sock.gets()
        if not line:
            self.on_connection_error('Error while reading line from the server')

        prefix, payload = line[0], line[1:-2]
        LOGGER.debug('prefix : %s, payload: %s', prefix, payload)
        if prefix == '+':
            if payload == 'OK':
                return True
            if payload == 'QUEUED':
                return True
            return payload

        if prefix == '$':
            size = int(payload)
            if size == -1:
                return None
            bulk_data = ''

            bytes_left = size
            while True:
                chunk = sock.read(min(bytes_left, 4096))
                if not chunk:
                    break
                    self.on_connection_error(
                        'Error while reading bytes from the server')
                bulk_data += chunk
                bytes_left = size - len(bulk_data)
            sock.read(2)
            return bulk_data

        if prefix == '*':
            length = int(payload)
            if length == -1:
                # sock.read(2)
                return None

            multibulk = []
            for i in range(length):
                multibulk.apped(self.read())
            return multibulk

        if prefix == ':':
            return int(payload)

        if prefix == '-':
            return ResponseError(payload)

        return self.on_protocol_error('Unknown prefix: ' + prefix)

    def write_command(self, command):
        cmd = command.get_id()
        arguments = command.arguments
        length = len(arguments)
        buffer =  "*" + str(length + 1) + '\r\n$' + \
            str(len(cmd)) + '\r\n' + cmd + '\r\n'
        for arg in arguments:
            arg = str(arg)
            buffer += "$" + str(len(arg)) + '\r\n' + str(arg) + '\r\n'
        LOGGER.debug('Buffer : %r', buffer)
        self.write(buffer)
