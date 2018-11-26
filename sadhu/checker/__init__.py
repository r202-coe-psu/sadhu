import time
import queue

from .. import models
from . import testrunners


class Server:
    def __init__(self, settings):
        self.settings = settings
        self.running = False
        self.queue = queue.Queue()

        self.solc = testrunners.SolutionController(self.queue)
        self.test_runners = testrunners.TestRunner(self.queue)
        self.test_runners.start()

        models.init_mongoengine(
                settings)

    def run(self):
        self.running = True
        while(self.running):
            solution_count = self.solc.get_waiting_solution()
            print('Hello ')
            if solution_count == 0:
                time.sleep(10)
            else:
                time.sleep(1)


def create_server(settings):
    return Server(settings)
