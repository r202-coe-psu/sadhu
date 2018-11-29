
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
        self.timeout = 60 # time in second

    def validate(self, solution, test_cases):
        filename = self.prepare_file(solution.code)

        test_case_len = len(test_cases)
        pass_tests = 0

        for t in test_cases:
            test_result = models.TestResult()
            test_result.started_date = datetime.datetime.now()
            test_result.test_case = t
            test_result.public = t.public
            test_result.expected_result = t.output_string

            input_str = t.input_string

            if t.is_inputfile:
                pass

            output = None
            try:
                output = subprocess.run(['python', filename],
                    input=input_str,
                    timeout=self.timeout,
                    capture_output=True)
            except Exception as e:
                test_result.timeout = True

                test_result.ended_date = datetime.datetime.now()
                solution.test_results.append(test_result)
                logger.exception(e)
                continue

            if output and output.returncode == 0:
                test_result.result = output.stdout.decode()

                output_data = test_result.result.split('\n')
                testcase_data = test_result.expected_result.split('\n')

                
                is_validate = True

                if abs(len(output_data) - len(testcase_data)) > 1:
                    is_validate = False
                else:
                    for t_output, p_output in zip(testcase_data, output_data):
                        if t_output.rstrip() != p_output.rstrip():
                            is_validate = False
                            break
                
                test_result.validated = is_validate
                if is_validate:
                    pass_tests += 1
            else:
                test_result.result = '{}\n{}'.format(
                        output.stdout.decode(),
                        output.stderr.decode())

            test_result.ended_date = datetime.datetime.now()
            solution.test_results.append(test_result)

        if pass_tests == test_case_len:
            solution.passed = True
        else:
            solution.passed = False
        solution.score = pass_tests/test_case_len * solution.challenge.score
        solution.save()
        self.remove_file(filename)
