from sadhu import models
import threading
import subprocess
import os
import datetime

from . import testers

import logging

logger = logging.getLogger(__name__)


class TestRunner(threading.Thread):
    def __init__(self, queue, settings):
        super().__init__()

        self.queue = queue
        self.daemon = True
        self.running = False

        self.settings = settings
        self.testers = dict(
            C=testers.CTester(settings),
            CPP=testers.CppTester(settings),
            Python=testers.PythonTester(settings),
        )

    def process(self, solution):

        tester = self.testers.get(solution.language, None)
        if not tester:
            solution.messages = "{} Tester Not Impremented".format(solution.language)
            solution.status = "Fail"
            solution.executed_date = datetime.datetime.now()
            solution.executed_ended_date = datetime.datetime.now()
            solution.save()
            return

        test_cases = solution.challenge.test_cases
        tester.process(solution, test_cases)

        if solution.type == "challenge":
            self.fill_testcase(solution)

    def fill_testcase(self, solution):
        logger.debug(f"fill output to testcase solution of {solution.id}")
        challenge = solution.challenge

        test_cases = solution.challenge.test_cases
        test_results = solution.test_results

        for test_result in test_results:
            for test_case in test_cases:
                if test_result.test_case != test_case:
                    continue

                test_case.output_string = test_result.output
                test_case.save()

    def run(self):
        self.running = True
        while self.running:
            solution = self.queue.get()
            logger.debug(
                "process solution {} for challenge {} of user {}".format(
                    solution.id, solution.challenge.id, solution.owner.id
                )
            )
            try:
                self.process(solution)
            except Exception as e:
                logger.exception(e)

    def stop(self):
        self.running = False


class SolutionController:
    def __init__(self, queue):
        self.queue = queue

    def get_waiting_solution(self):
        solutions = models.Solution.objects(status="waiting")
        for solution in solutions:
            solution.status = "in-queue"
            solution.save()
            self.queue.put(solution)

        return len(solutions)
