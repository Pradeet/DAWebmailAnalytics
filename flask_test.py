import os
import unittest
import run

#class flask_test(unittest.TestCase):
def test_invalid_JSON(self):
	response = self.app.post('/json', data='{"name": "jahaha"}')
	self.assertEqual(response.status_code, 405)

if __name__ == '__main__':
	unittest.main()
	test_invalid_JSON()