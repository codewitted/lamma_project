import unittest

class TestSimple(unittest.TestCase):
    def test_hello(self):
        print("Hello from test")
        self.assertTrue(True)

if __name__ == "__main__":
    unittest.main()
