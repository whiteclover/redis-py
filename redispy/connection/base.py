#!/usr/bin/env python


import socket
import logging
import select
import errno
from redispy.net import Stream
from redispy.errors import (
    CannotConnectError,
    ConnectionError,
)

import logging

logger = logging.getLogger(__name__)


class BaseConnection(object):

    def __init__(self, options):
        self.options = options

        self.cachedId = None
        self.init_cmds = []

    def __del__(self):
        self.disconnect()

    # def check_options(self, options):
    #    if options['scheme'] == 'unix':
    #         if path not in options:
    #             raise Exception(
    #                 'Missing UNIX domain socket path')

    #     if options['scheme'] == 'tcp':
    #         return options

    #     raise Exception('Invalid scheme')

    def create_resource(self):
        pass

    def is_connected(self):
        return bool(self.stream.socket)

    def get_resource(self):
        self.stream.ensure_connect()
        return self.stream

    def push_init_command(self, command):
        self.init_cmds.apped(command)

    def execute_command(self, command):
        self.write_command(command)
        return self.read_response(command)

    def read_response(self, command):
        return self.read()

    def on_connection_error(self, message, code=None):
        CommunicationException.handle(ConnectionError(self,
                                                      "$message [{$this->parameters->scheme}://{$this->getIdentifier()}]", code))

    def on_protocol_error(self, message):
        CommunicationException.handle(ProtocolError(self,
                                                    "$message [{$this->parameters->scheme}://{$this->getIdentifier()}]"))


class Reader(object):

    def __init__(self, fd, poll_timeout=1):
        self.fd = fd
        self.poll_timeout = poll_timeout

        if hasattr(select, 'poll'):
            self.poller = select.poll()
            self.events = select.POLLIN | select.POLLPRI
            self.poller.register(self.fd, self.events)
        else:
            self.poll_timeout = float(self.poll_timeout / 1000)
            self.poller = None

    def readable(self):
        if self.poller:
            events = self.poller.poll(self.poll_timeout)
            return bool(events)
        else:
            r, _, _ = select.select([self.fd], [], [], self.poll_timeout)
            return bool(r)


class RedisSocket(Stream):

    READ = 0x0001
    WRITE = 0x0004
    ERROR = 0x0008
    CRLF = '\r\n'

    def __init__(self,  host='127.0.0.1', port=6379,
                 path=None, timeout=2):
        Stream.__init__(self)
        self.host = host
        self.port = port
        self.path = path
        self.timeout = timeout
        self.connect()
        self.sent_size = 1024

    def readable(self):
        self.read_poller.readable()

    def ensure_connect(self):
        if not self.socket:
            self.connect()

    def connect(self):
        try:
            if self.path:
                self.socket = self.create_unix_socket()
            else:
                self.socket = self.create_tcp_scoket()
        except socket.timeout:
            error = 'Connection to %s:%s failed: timeout' % (
                    self.host, self.port)
            logger.error(error)
            raise ConnectionError(error)

                # return error
        except socket.error as error:
            error = 'Connection to %s:%s failed: %s' % (
                    self.host, self.port, error[0])
            logger.error(error)
        self._connecting = False
        self.read_poller = Reader(self.fileno())

            # return error
    def clear(self):
        self._in_buffer = ''

    def create_unix_socket(self):
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.settimeout(self.timeout)
        sock.setblocking(False)
        sock.connect(path)
        return sock

    def create_tcp_scoket(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_TCP, socket.TCP_NODELAY, 1)
        sock.settimeout(self.timeout)
        # sock.setblocking(False)
        sock.connect((self.host, self.port))
        return sock

    def fileno(self):
        return self.socket.fileno()

    def disconnetc(self):
        if self.socket:
            self.socket.close()

    def _write_to_socket(self, data):
        sent = 0
        if sent < len(data):
            sent += self.socket.send(data[sent:])
        return sent

    def _read_from_socket(self, nbytes):
        while True:
            try:
                data = self.socket.recv(nbytes)
                return data
            except errno.EWOULDBLOCK, errno.EAGAIN:
                if self.readable():
                    continue
            except socket.timeout:
                return ''
            except socket.error as error:
                return ''
