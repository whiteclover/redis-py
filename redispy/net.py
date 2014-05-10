
import logging
import socket

logger = logging.getLogger(__name__)


def create_unix_socket(path, timeout):
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    #sock.setblocking(False)
    sock.connect(path)
    return sock

def create_tcp_scoket(host, port, timeout):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_TCP, socket.TCP_NODELAY, 1)
    sock.settimeout(timeout)
    #sock.setblocking(False)
    sock.connect((host, port))
    return sock


class BaseStream(object):

    CRLF = '\r\n'

    def __init__(self):
        self._in_buffer = ''
        self._close_callback = None
        self._connected = False

    def fileno(self):
        raise NotImplementedError()

    def close_socket(self):
        raise NotImplementedError()

    def _read_from_socket(self):
        raise NotImplementedError()

    def _write_to_socket(self, data):
        raise NotImplementedError()


class Stream(BaseStream):

    """docstring for stream"""

    def __init__(self):
        BaseStream.__init__(self)

    def gets(self):
        crlf_index = self._in_buffer.find(self.CRLF)
        while crlf_index == -1:
            self._in_buffer += self._read_from_socket(4096)
            crlf_index = self._in_buffer.find(self.CRLF)
        i = crlf_index + len(self.__class__.CRLF)
        result = self._in_buffer[0:i]
        self._in_buffer = self._in_buffer[i:]
        return result

    def read(self, nbytes):
        if len(self._in_buffer) < nbytes:
            result = self._in_buffer
            result += self._read_from_socket(nbytes - len(self._in_buffer))
        else:
            result = self._in_buffer[0:nbytes]
            self._in_buffer = self._in_buffer[nbytes:]
        return result

    def write(self, data):
        return self._write_to_socket(data)