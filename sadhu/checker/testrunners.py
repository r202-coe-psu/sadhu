
from sadhu import models
import threading
import subprocess
import os
import datetime

class TestResult:
    ouput = ''
    error = ''
    is_error = ''
    message = ''

class Tester:
    def __init__(self, settings):
        self.directory = '/tmp/'

    def prepare_file(self, code):
        filename = self.directory + code.filename
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
        self.validate(solution, test_cases)

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

        for t in test_cases:
            test_result = models.TestResult()
            test_result.started_date = datetime.datetime.now()
            test_result.test_case = t
            test_result.public = t.public
            test_result.expected_result = t.output_file.read().decode()

            if not t.input_file:
                output = subprocess.run(['python', filename], capture_output=True)
            else:
                print('need input')

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
            
            test_result.ended_date = datetime.datetime.now()
            solution.test_results.append(test_result)
        
        solution.status = 'complete'
        solution.save()
                # result.is_error = False if coutput.returncode == 0 else True
                # result.output = coutput.stdout.decode('utf-8')
                # result.error = coutput.stderr.decode('utf-8')
                # result.message = coutput.stderr.decode('utf-8')

        self.remove_file(filename)


class TestRunner(threading.Thread):
    def __init__(self, queue):
        super().__init__()

        self.queue = queue
        self.running = False

        settings = dict()
        self.testers = dict(
                c=CTester(settings),
                python=PythonTester(settings)
                )


    def process(self, solution):
        solution.status = 'process'
        solution.save()

        tester = self.testers.get('python')
        test_cases = solution.challenge.test_cases
        result = tester.process(solution, test_cases)
        

    def run(self):
        self.running = True
        while(self.running):
            solution = self.queue.get()
            print('process solution')
            self.process(solution)

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

        return solutions.count()
