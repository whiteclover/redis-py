from redispy import command

import unittest

class TestCommand(unittest.TestCase):


	def test_auth(self):

		c = command.ConnectionAuth()

		assert c.get_id() == 'AUTH'



if __name__ == '__main__':

	unittest.main()