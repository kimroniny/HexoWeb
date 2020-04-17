import unittest, sys, os
sys.path.append(os.path.abspath(os.path.dirname(os.path.curdir)))
from tornado.testing import *
import web as entry
import mock, requests
import argparse


class TestServer(AsyncHTTPTestCase):
    def setUp(self) -> None:
        os.environ['ASYNC_TEST_TIMEOUT'] = "30"
        super(TestServer, self).setUp()

    def tearDown(self) -> None:
        super(TestServer, self).tearDown()
        os.environ.pop("ASYNC_TEST_TIMEOUT")

    def get_app(self) -> Application:
        entry.getArg = mock.Mock(return_value=argparse.Namespace(hd=os.environ.get("HEXO_ROOT", None)))
        args = entry.getArg()
        if not args.hd:
            raise Exception("args.hd cannot be None")
        return entry.make_app(args)

    def test_cmd_help(self):
        # requests.
        r = requests.Request(url="http://localhost/test", data={'type': "help"})
        body = r.prepare().body
        response = self.fetch("/hexo", method="POST", body=body)
        print("help: {}".format(response.body.decode()))
        self.assertEqual(response.code, 200)
    def test_cmd_show(self):
        r = requests.Request(url="http://localhost/test", data={'type': "list"})
        body = r.prepare().body
        response = self.fetch("/hexo", method="POST", body=body)
        print("list: {}".format(response.body.decode()))
        self.assertEqual(response.code, 200)

if __name__ == '__main__':
    unittest.main(verbosity=2)
