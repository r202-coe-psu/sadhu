import time
import queue

from .. import models
from . import testrunners

import logging

logger = logging.getLogger(__name__)


class Server:
    def __init__(self, settings):
        self.settings = settings
        self.running = False
        self.queue = queue.Queue()

        self.solc = testrunners.SolutionController(self.queue)
        self.test_runners = testrunners.TestRunner(self.queue, settings)
        self.test_runners.start()

        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s %(name)-12s %(levelname)-8s %(message)s",
            datefmt="%m-%d %H:%M",
        )

        models.init_mongoengine(settings)

    def run(self):
        self.running = True
        while self.running:
            logger.debug("start query waiting solutions")
            solution_count = self.solc.get_waiting_solution()
            if solution_count == 0:
                time.sleep(10)
            else:
                logger.debug("got {} solutions to process".format(solution_count))
                time.sleep(1)

            self.test_runners.clear_executors()


def create_server(settings):
    return Server(settings)
