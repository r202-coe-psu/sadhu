from sadhu import models
import threading
import subprocess
import os
import datetime

from pathlib import Path
import shutil


import logging

logger = logging.getLogger(__name__)


class TestResult:
    ouput = ""
    error = ""
    is_error = ""
    message = ""


class Tester:
    def __init__(self, settings):
        self.timeout = 60  # time in second
        directory = settings.get("SADHU_CHECKER_DIRECTORY", "/tmp")
        self.directory = directory if directory[-1] != "/" else directory[:-1]
        self.settings = settings

    def prepare_file(self, solution):
        p = Path(
            "{}/{}/{}".format(self.directory, solution.owner.id, solution.challenge.id)
        )
        if not p.exists():
            p.mkdir(parents=True, exist_ok=True)

        filename = "{}/{}".format(str(p), solution.code.filename)
        with open(filename, "wb") as f:
            data = solution.code.read()
            f.write(data)

        return filename

    def remove_file(self, filename):
        file_path = Path(filename)
        directory_path = file_path.parents[0]

        shutil.rmtree(file_path, ignore_errors=True)

    def build_executable_options(self, filename):
        return [filename]

    def prepair_executable(self, filename):
        result = dict(executable=filename, status=True)

        return result

    def process(self, solution, test_cases):
        solution.status = "process"
        solution.executed_date = datetime.datetime.now()
        solution.save()

        self.validate(solution, test_cases)

        solution.status = "complete"
        solution.executed_ended_date = datetime.datetime.now()
        solution.save()

    def validate(self, solution, test_cases):
        filename = self.prepare_file(solution)

        result = self.prepair_executable(filename)
        executable_file = result["executable"]

        solution.metadata["compilation"] = result

        executable_list = self.build_executable_options(executable_file)
        solution.metadata["executable"] = executable_list

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
                output = subprocess.run(
                    executable_list,
                    input=input_str.encode(),
                    timeout=self.timeout,
                    capture_output=True,
                )
            except Exception as e:
                test_result.timeout = True

                test_result.ended_date = datetime.datetime.now()
                solution.test_results.append(test_result)
                logger.exception(e)
                continue

            if output and output.returncode == 0:
                test_result.output = output.stdout.decode("utf-8", errors="replace")

                output_data = (
                    test_result.output.strip().splitlines()
                    if test_result.output
                    else []
                )
                testcase_data = (
                    test_result.expected_result.strip().splitlines()
                    if test_result.expected_result
                    else []
                )

                is_validate = True

                if len(output_data) == 0:
                    is_validate = False
                elif not testcase_data:
                    is_validate = False
                elif abs(len(output_data) - len(testcase_data)) != 0:
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
                test_result.result = "{}\n{}".format(
                    output.stdout.decode(), output.stderr.decode()
                )

            test_result.ended_date = datetime.datetime.now()
            solution.test_results.append(test_result)

        if pass_tests == test_case_len:
            solution.passed = True
        else:
            solution.passed = False
        solution.score = pass_tests / test_case_len * solution.challenge.score
        solution.save()

        self.remove_file(filename)


class CTester(Tester):
    def __init__(self, settings):
        super().__init__(settings)
        self.compiler_options = [
            s.strip() for s in self.settings["TESTRUNNER_C_COMPILER"].split(" ")
        ]

    def prepair_executable(self, filename):
        exe_file = filename[: filename.rfind(".")]
        compilation = self.compiler_options + [filename, "-o", exe_file, "-lm"]
        output = subprocess.run(compilation, capture_output=True)

        result = dict(
            executable=exe_file,
            compiled_date=datetime.datetime.now(),
            status=True,
            compilation=compilation,
        )

        if output.returncode != 0:
            if output.stderr:
                result["error"] = output.stderr.decode("utf-8", errors="replace")

        if output.stdout:
            result["output"] = output.stdout.decode("utf-8", errors="replace")

        return result


class CppTester(Tester):
    def __init__(self, settings):
        super().__init__(settings)
        self.compiler_options = [
            s.strip() for s in self.settings["TESTRUNNER_CPP_COMPILER"].split(" ")
        ]


class PythonTester(Tester):
    def __init__(self, settings):
        super().__init__(settings)

        self.runner_options = [
            s.strip() for s in self.settings["TESTRUNNER_PYTHON_RUNNER"].split(" ")
        ]

    def build_executable_options(self, filename):
        return self.runner_options + [filename]


class GoTester(Tester):
    def __init__(self, settings):
        super().__init__(settings)

        self.runner_options = [
            s.strip() for s in self.settings["TESTRUNNER_GO_RUNNER"].split(" ")
        ]

    def build_executable_options(self, filename):
        return self.runner_options + [filename]
