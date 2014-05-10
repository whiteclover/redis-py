#!/usr/bin/env python

from redispy.client import Client
import logging
import unittest


class TestClient(unittest.TestCase):

    def test_execute(self):

        c = Client()
        assert c.execute('ping')() == True

    def test_set_and_get(self):
        c = Client()
        assert c.set('test', 'test_set_and_get') == True
        assert c.get('test') == 'test_set_and_get'


if __name__ == '__main__':

    debug = True
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(level=level,
                        format='%(asctime)s %(levelname)-8s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S', filemode='a+')

    unittest.main()
