from django.shortcuts import render
from django.conf import settings
import os
import subprocess
import json

# Create your views here.
def index(request):
    if request.method == "POST":
        code_content = request.POST['code']

        # Check if the code_content is not empty
        if code_content.strip():
            
            unit_testing_folder = os.path.join(settings.BASE_DIR, 'unit_testing')
            test_cases_file_path = os.path.join(unit_testing_folder, 'test_cases.json')
            output_file_path = os.path.join(unit_testing_folder, 'output_scores.txt')
            c_file_path = os.path.join(unit_testing_folder, 'test.c')

            # Write the content to the C file
            with open(c_file_path, 'w') as c_file:
                c_file.write(code_content)
            
            output = run_c_programs(c_file_path, test_cases_file_path, output_file_path)
    else:
        output= "Press Submit Button to test your code"
    return render(request, 'index.html', {'output': output})


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

        for test_case in test_cases:
            input_data = test_case["input"]
            expected_output = test_case["output"]

            # Run the C program and capture the output
            process = subprocess.Popen(["./temp_executable"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
            actual_output, _ = process.communicate(input=input_data)
            actual_output = actual_output.strip()

            # Compare the output with the expected output
            if actual_output == expected_output:
                print(f"  Test Passed: Input - {input_data}, Output - {actual_output}")
                score += 1
            else:
                print(f"  Test Failed: Input - {input_data}, Expected Output - {expected_output}, Actual Output - {actual_output}")

        # Write the score to the result file
        output = f"Result: {score} out of {len(test_cases)} tests passed = {score/len(test_cases) * 100}%\n"
        result_file.write(output)
        print("")

    # Remove temporary executable
    exe_file_path = os.path.join(settings.BASE_DIR, 'temp_executable.exe')
    os.remove(exe_file_path)
    return output