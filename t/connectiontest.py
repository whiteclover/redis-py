


#!/usr/bin/env python

from redispy.connection import StreamConnection
from redispy.connection.base import RedisSocket
import logging
import unittest


class TestRedisSocket(unittest.TestCase):

    def test_write_and_read(self):
        s = RedisSocket()
        data = '*1\r\n$4\r\nPING\r\n'
        s.write(data) == len(data)
        assert s.read(1) == '+'
        assert s.read(4) == 'PONG'
        assert s.gets() == '\r\n'


if __name__ == '__main__':

    debug = True
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(level=level,
                        format='%(asctime)s %(levelname)-8s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S', filemode='a+')

    unittest.main()