import unittest
import sys, os
sys.path.append(os.path.abspath(os.path.dirname(os.path.curdir)))
from commands import Command
import argparse

class TestCmds(unittest.TestCase):
    # def __init__(self, statement):
    #     super(TestCmds, self).__init__()
    #     self.statement = statement

    def testCommand(self):
        print("hexo_root: {}".format(os.environ.get("HEXO_ROOT", ".")))
        res, out, err = Command.execute(args.c, cwd=os.environ.get("HEXO_ROOT", "."))
        print("res: \n{}\noutput: \n{}\nerr: \n{}".format(res, out, err))
        self.assertEqual(res, 0)

def getArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", type=str, required=True, help="test command")
    return parser.parse_args()

args = getArgs()

if __name__ == '__main__':
    # runner = unittest.TextTestRunner()
    # suite = unittest.TestSuite()
    # suite.addTest(
    #     TestCmds(args.c)
    # )
    # runner.run(suite)

    runner = unittest.TextTestRunner()
    runner.run(
        unittest.TestLoader().loadTestsFromTestCase(TestCmds)
    )