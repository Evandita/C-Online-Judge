from django.shortcuts import render
from django.conf import settings
import os
import subprocess
import json
import threading
from queue import Queue
import time
from .models import TestCaseResult

testCaseResult = []

# Create your views here.
def index(request):
    code_content = ""
    if request.method == "POST":
        code_content = request.POST['code']

        # Check if the code_content is not empty
        if code_content.strip():
            testCaseResult.clear()
            unit_testing_folder = os.path.join(settings.BASE_DIR, 'unit_testing')
            test_cases_file_path = os.path.join(unit_testing_folder, 'test_cases.json')
            output_file_path = os.path.join(unit_testing_folder, 'output_scores.txt')
            c_file_path = os.path.join(unit_testing_folder, 'test.c')

            # Write the content to the C file
            with open(c_file_path, 'w') as c_file:
                c_file.write(code_content)
            
            output = run_c_programs(c_file_path, test_cases_file_path, output_file_path)
    else:
        testCaseResult.clear()
        output= "Press Submit Button to test your code"
    return render(request, 'index.html', {'output': output, 'results': testCaseResult, 'code': code_content})

class TimeoutException(Exception):
    pass

def run_c_programs(c_file, test_cases_file, output_file):
    with open(test_cases_file, 'r') as f:
        test_cases = json.load(f)

    with open(output_file, 'w') as result_file:
        print(f"Running C program: {c_file}")

        # Compile the C program
        compile_result = subprocess.run(["gcc", "-o", "temp_executable", c_file], stderr=subprocess.PIPE, text=True)
        if compile_result.returncode != 0:
            print(f"  Compilation failed for {c_file}: {compile_result.stderr.strip()}")
            result_file.write(f"Compilation failed\n")
            return "Compilation Error"

        # Initialize the score for the current C file
        score = 0
        elapsed_time_first_test = None
        test_num = 1
        for test_case in test_cases:
            input_data = test_case["input"]
            expected_output = test_case["output"]

            # Run the C program with a timeout of 1 second for the first test case
            if elapsed_time_first_test is None:
                process = subprocess.Popen(["./temp_executable"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                input_queue = Queue()
                input_queue.put(input_data)

                # Use a dictionary to store the result (output and elapsed_time) outside the target function's scope
                result_data = {"output": None, "elapsed_time": None}

                def target():
                    try:
                        start_time = time.time()
                        result_data["output"], _ = process.communicate(input=input_queue.get(timeout=1))
                        result_data["elapsed_time"] = time.time() - start_time

                        if result_data["elapsed_time"] > 1:
                            raise TimeoutException("Execution timed out")
                    except TimeoutException:
                        process.kill()
                        result_data["output"] = ""
                        result_file.write(f"Timeout\n")

                thread = threading.Thread(target=target)
                thread.start()
                thread.join()

                elapsed_time_first_test = result_data["elapsed_time"]

                # If the elapsed time for the first test case exceeds 1 second, break the loop and return a timeout error
                if elapsed_time_first_test > 1:
                    break

            # For subsequent test cases, check if the elapsed time exceeds the limit
            else:
                process = subprocess.Popen(["./temp_executable"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                input_queue = Queue()
                input_queue.put(input_data)

                result_data = {"output": None, "elapsed_time": None}

                def target():
                    try:
                        start_time = time.time()
                        result_data["output"], _ = process.communicate(input=input_queue.get(timeout=1))
                        result_data["elapsed_time"] = time.time() - start_time

                        if result_data["elapsed_time"] > 1:
                            raise TimeoutException("Execution timed out")
                    except TimeoutException:
                        process.kill()
                        result_data["output"] = ""
                        result_file.write(f"Timeout\n")

                thread = threading.Thread(target=target)
                thread.start()
                thread.join()
            
            # Create a TestCaseResult instance and store the result in the results list
            result_instance = TestCaseResult(
                num = test_num,
                passed=result_data["output"].strip() == expected_output,
                input_data=input_data,
                expected_output=expected_output,
                actual_output=result_data["output"].strip(),
                time_taken=result_data["elapsed_time"],  # Store elapsed time in the time_taken field
            )
            testCaseResult.append(result_instance)

            # Compare the output with the expected output
            if result_data["output"].strip() == expected_output:
                print(f"  Test {test_num} Passed - Input: {input_data}, Expected Output: {expected_output}, Actual Output: {result_data['output'].strip()}, Elapsed Time: {result_data['elapsed_time']:.2f} seconds")
                score += 1
            else:
                print(f"  Test {test_num} Failed - Input: {input_data}, Expected Output: {expected_output}, Actual Output: {result_data['output'].strip()}, Elapsed Time: {result_data['elapsed_time']:.2f} seconds")
            test_num += 1
        # If the elapsed time for the first test case exceeded 1 second, return a timeout error
        if elapsed_time_first_test is not None and elapsed_time_first_test > 1:
            output = "Time Limit Exceeded"
            result_file.write(output + "\n")
            return output

        # Write the score to the result file
        output = f"Result: {score} out of {len(test_cases)} tests passed = {(score/len(test_cases) * 100):.2f}%\n"
        result_file.write(output)
        print("")

    # Remove temporary executable
    exe_file_path = os.path.join(settings.BASE_DIR, 'temp_executable.exe')
    os.remove(exe_file_path)

    return output