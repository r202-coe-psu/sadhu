
from sadhu import models
import threading
import subprocess
import os
import datetime


import logging
logger = logging.getLogger(__name__)

class TestResult:
    ouput = ''
    error = ''
    is_error = ''
    message = ''

class Tester:
    def __init__(self, settings):
        self.directory = settings.get('SADHU_CHECKER_DIRECTORY', '/tmp')

    def prepare_file(self, code):
        filename = '{}/{}'.format(self.directory if self.directory[-1] != '/' \
                else self.directory[:-1], code.filename)
        data = code.read()
        f = open(filename, 'wb')
        f.write(data)
        f.close()
        return filename

    def remove_file(self, filename):
        os.remove(filename)

    def validate(solutuib, test_cases):
        raise 'Validate method not Impremented'

    def process(self, solution, test_cases):
        solution.status = 'process'
        solution.executed_date = datetime.datetime.now()
        solution.save()

        self.validate(solution, test_cases)


        solution.status = 'complete'
        solution.executed_ended_date = datetime.datetime.now()
        solution.save()

class CTester(Tester):
    def __init__(self, settings):
        super().__init__(settings)

    def validate(self, solution, test_cases):
        filename = self.prepare_file(solution.code)
        

        result = TestResult()
        coutput = subprocess.run(['gcc', '-Wall', filename, '-o',
            filename[:filename.rfind('.')]])
        if coutput.returncode == 0:
            output = subprocess.run([filename[:filename.rfind('.')]])
            result.is_error = True if output.returncode == 0 else False
            result.output = output.stdout
            result.error = output.stderr
        else:
            result.is_error = True if coutput.returncode == 0 else False
            result.output = coutput.stdout
            result.error = coutput.stderr
            result.message = coutput.stderr

        self.remove_file(filename)

        return result
     
 
class PythonTester(Tester):
    def __init__(self, settings):
        super().__init__(settings)

    def validate(self, solution, test_cases):
        filename = self.prepare_file(solution.code)

        test_case_len = len(test_cases)
        pass_tests = 0

        for t in test_cases:
            test_result = models.TestResult()
            test_result.started_date = datetime.datetime.now()
            test_result.test_case = t
            test_result.public = t.public
            test_result.expected_result = t.output_file.read().decode()

            if not t.input_file:
                output = subprocess.run(['python', filename], capture_output=True)
            else:
                input_bstr = t.input_file.read()
                output = subprocess.run(['python', filename],
                        stdin=input_bstr.decode('utf-8'), capture_output=True)

            if output.returncode == 0:
                test_result.result = output.stdout.decode()

                output_data = test_result.result.split('\n')
                testcase_data = test_result.expected_result.split('\n')
                
                is_validate = True
                for t_output, p_output in zip(testcase_data, output_data):
                    if t_output.rstrip() != p_output.rstrip():
                        is_validate = False
                        break

                test_result.validated = is_validate
                if is_validate:
                    pass_tests += 1
            
            test_result.ended_date = datetime.datetime.now()
            solution.test_results.append(test_result)

        if pass_tests == test_case_len:
            solution.passed = True
        else:
            solution.passed = False
        solution.score = pass_tests/test_case_len * solution.challenge.score
        solution.save()
        self.remove_file(filename)


class TestRunner(threading.Thread):
    def __init__(self, queue):
        super().__init__()

        self.queue = queue
        self.daemon = True
        self.running = False

        settings = dict()
        self.testers = dict(
                C=CTester(settings),
                Python=PythonTester(settings)
                )


    def process(self, solution):
       
        tester = self.testers.get(solution.language, None)
        if not tester:
            solution.messages = '{} Tester Not Impremented'.format(
                    solution.language)
            solution.status = 'Fail'
            solution.executed_date = datetime.datetime.now()
            solution.executed_ended_date = datetime.datetime.now()
            solution.save()
            return

        test_cases = solution.challenge.test_cases
        tester.process(solution, test_cases)
        

    def run(self):
        self.running = True
        while(self.running):
            solution = self.queue.get()
            logger.debug('process solution')
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
        solutions = models.Solution.objects(status='waiting')
        for solution in solutions:
            solution.status = 'in-queue'
            solution.save()
            self.queue.put(solution)

        return len(solutions)
