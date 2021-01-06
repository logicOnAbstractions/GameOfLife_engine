"""" .py contenant les tests à effectuer"""

import unittest                         # our test lib
from logger import get_root_logger
from utils import *
from main import MainProgram
from classes.arg_parser import ArgParser


class SomeTests(unittest.TestCase):     # on doit hériter de TestCase

    def __init__(self, *args, **kwargs):
        super(SomeTests, self).__init__(*args, **kwargs)
        self.main_prog = None

    def setUp(self):
        """ Runs after EACH test. Here we instantiate a new instance
         each test because we don't want the values modified by a previous test to influence the results of the next one"""
        self.main_prog = MainProgram(arg_parser=argparser, logger=LOG)           # instantiated every single test, so new instances all the time

    def tearDown(self):
        """
        Runs after each test. Similar to class teardown
        """
        self.main_prog = None

    ################################################ tests

    def test_add_glider(self):
        """ adds a glider to the Game"""
        LOG.info("Testing add glider")

if __name__ == '__main__':
    import sys
    LOG = get_root_logger(BASE_LOGGER_NAME, filename=f'tests.log')
    LOG.debug(f'logger debug level msg ')
    LOG.info(f'logger info level msg ')
    LOG.warning(f'logger warn level msg ')
    LOG.error(f'logger error level msg ')
    LOG.critical(f'logger critical level msg ')

    argparser = ArgParser(logger=LOG)
    # we've parsed the args, so remove them so it doesn't trip up unitttest when it doesn't recognize them itself
    sys.argv[1:] = []
    unittest.main()