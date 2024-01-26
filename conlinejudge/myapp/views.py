from django.shortcuts import render
from django.conf import settings
import os
import subprocess
import json
import threading
from queue import Queue
import time
from .models import TestCaseResult
import shlex

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
            
            output = run_c_program("okay", code_content, test_cases_file_path, output_file_path, 1)
    else:
        testCaseResult.clear()
        output= "Press Submit Button to test your code"
    return render(request, 'index.html', {'output': output, 'results': testCaseResult, 'code': code_content})

def run_c_program(user, c_code, test_cases_file, output_file, timeout=1):
    
    with open(test_cases_file, 'r') as f:
        test_cases = json.load(f)
    
    # Save the C code to a file
    with open(user+".c", "w") as file:
        file.write(c_code)

    # Compile the C code
    with open(output_file, 'w') as result_file:
        compile_command = "gcc "+user+".c -o "+user
        compile_process = subprocess.run(shlex.split(compile_command), stderr=subprocess.PIPE)

        if compile_process.returncode != 0:
            print("Compilation error:")
            print(compile_process.stderr.decode())
            
            # Clean up: remove temporary files
            os.remove(user+".c")
            return "Compilation error: " + compile_process.stderr.decode()

        # Run the compiled program with a timeout
        run_command = "./"+user if os.name != 'nt' else user+".exe"
        
        score = 0
        test_num = 1
        
        for test_case in test_cases:
            input_data = test_case["input"]
            expected_output = test_case["output"]
            try:
                start_time = time.time()
                result = subprocess.run(shlex.split(run_command), input=input_data.encode(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)
                end_time = time.time()
                elapsed_time = end_time - start_time

                # Check if the program timed out
                if elapsed_time >= timeout:
                    print("Timeout reached ({} seconds)".format(timeout))
                    return

                # Print the output of the C program
                print("Output:")
                print(result.stdout.decode())

                
                # Print any error messages from the C program
                if result.stderr:
                    print("Error:")
                    print(result.stderr.decode())
                    
                    return "Error: " + result.stderr.decode()
                
                # Create a TestCaseResult instance and store the result in the results list
                result_instance = TestCaseResult(
                    num = test_num,
                    passed=result.stdout.decode() == expected_output,
                    input_data=input_data,
                    expected_output=expected_output,
                    actual_output=result.stdout.decode(),
                    time_taken=elapsed_time,  # Store elapsed time in the time_taken field
                )
                testCaseResult.append(result_instance)

                # Compare the output with the expected output
                if result.stdout.decode() == expected_output:
                    print(f"  Test {test_num} Passed - Input: {input_data}, Expected Output: {expected_output}, Actual Output: {result.stdout.decode()}, Elapsed Time: {elapsed_time:.2f} seconds")
                    score += 1
                else:
                    print(f"  Test {test_num} Failed - Input: {input_data}, Expected Output: {expected_output}, Actual Output: {result.stdout.decode()}, Elapsed Time: {elapsed_time:.2f} seconds")
                test_num += 1

            except subprocess.TimeoutExpired:
                # Clean up: remove temporary files
                os.remove(user+".c")
                os.remove(user+".exe")
                return "Timeout reached ({} seconds)".format(timeout)
            
        # Clean up: remove temporary files
        os.remove(user+".c")
        os.remove(user+".exe")
        
        # Write the score to the result file
        output = f"Result: {score} out of {len(test_cases)} tests passed = {(score/len(test_cases) * 100):.2f}%\n"
        result_file.write(output)
    return output
        