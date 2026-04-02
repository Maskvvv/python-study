class Dict(dict):
    def __init__(self, **kw):
        super().__init__(**kw)
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(r"'Dict' object has no attribute '%s'" %key)
    def __setattr__(self, key, value):
        self[key] = value

    def setUp(self):
        print('setUp...')
    def tearDown(self):
        print('tearDown...')


import unittest
# from test import Dict

class TestDict(unittest.TestCase):
    def test_init(self):
        d = Dict(a=1, b=2)
        self.assertEqual(d.a, 1)
        self.assertEqual(d.b, 2)
        self.assertTrue('a' in d)
        self.assertTrue('b' in d)

    def test_getattr(self):
        d = Dict()
        d['a'] = 1
        self.assertEqual(d.a, 1)

    def test_setattr(self):
        d = Dict()
        d.a = 1
        self.assertTrue('a' in d)
        self.assertEqual(d['a'], 1)

if __name__ == '__main__':
    unittest.main()


# python -m unittest mydict_test
# python -m unittest mydict_test.TestDict.test_attr