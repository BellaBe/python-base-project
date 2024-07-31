import logging
import os
import re

from dotenv import load_dotenv
from git import Repo
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

load_dotenv()


def get_chain():
    """Get the language model.
    Returns:
    chain: The language model chain.
    """
    model_name = "llama3-70b-8192"
    api_key = os.getenv("GROQ_API_KEY", None)
    if api_key is None:
        raise ValueError("Please set the GROQ_API_KEY environment variable.")
    llm = ChatGroq(model=model_name, api_key=api_key)
    prompt = PromptTemplate.from_template(
        """
        **Role:** Software Tester
        **Objective:** Create a comprehensive set of test cases for a given code
          snippet to ensure its functionality and identify potential errors.
        **Target Audience:** Software Developers, Quality Assurance Teams\n\n

        **Instructions:**
        1. Review the provided `{function_code}` and identify the key functionality
           and potential areas of error.
        2. Write a set of test cases to validate the correctness of the code, including:
            * Positive test cases: Test scenarios that verify the code's expected behavior.
            * Negative test cases: Test scenarios that verify the code's error handling
              and boundary cases
            * Edge cases: Test scenarios that push the code's functionality to its limits.
        3. Ensure test cases are clear, concise, and well-structured, with descriptive names and comments
        4. Provide a brief explanation for each test case, outlining the expected outcome and any assumptions made.
        5. Name the test cases following the convention `test_functionname_scenario`, e.g., `test_add_positive_numbers`.

        **Constraints:**
            * Avoid duplicating test cases or scenarios.
            * Ensure test cases are independent and do not interfere with each other.

        **Output Requirements:**
            * The output should include a minimum of 5 test cases, with at least 2 positive, 2 negative, and 1 edge case
            * Each test case should include:
                + A descriptive name
                + A clear explanation of the test scenario
                + The expected outcome
                + Any necessary setup or teardown code
            * The output should be written in a format compatible with the python and easily executable by a testing
              framework pytest.
            * Return only the test cases without any additional code or comments.

        **Additional Guidance:**
                * Consider the code snippet's functionality, inputs, and expected outputs when creating test
                  cases.
                * Ensure test cases cover a range of scenarios, including normal operation, error handling, and boundary
                  cases.
        """,
    )
    chain = prompt | llm | StrOutputParser()
    return chain


def get_changed_files():
    """Get the list of changed files using git status.
    Returns:
    list: A list of changed files.
    """
    repo = Repo(".")
    changed_files = [item.a_path for item in repo.index.diff(None)] + [item.a_path for item in repo.index.diff("HEAD")]
    logging.debug("CHANGED FILES: %s", changed_files)
    return changed_files


def get_deleted_functions(repo):
    """Get the list of deleted functions using git diff.
    Returns:
    dict: A dictionary where the keys are file paths and the values are lists of deleted function names.
    """
    deleted_functions = {}
    diff = repo.git.diff("HEAD~1", "--diff-filter=D", name_only=True)
    for file_path in diff.splitlines():
        if file_path.startswith("src/") and file_path.endswith(".py"):
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
                for line in lines:
                    if line.startswith("def ") and line.endswith(":"):
                        function_name = line.split("(")[0].replace("def ", "").strip()
                        if file_path not in deleted_functions:
                            deleted_functions[file_path] = []
                        deleted_functions[file_path].append(function_name)
    logging.info("DELETED FUNCTIONS: %s", deleted_functions)
    return deleted_functions


def parse_functions(file_path):
    """Parse the functions in a file.
    Args:
    file_path (str): The path to the file.
    Returns:
    list: A list of function names.
    """
    functions = []
    with open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()
        for line in lines:
            logging.debug("LINE======= %s", line.strip())

            if line.strip().startswith("def ") and line.strip().endswith(":"):
                function_name = line.split("(")[0].replace("def ", "").strip()
                functions.append(function_name)
    logging.info("FUNCTIONS IN %s: %s", file_path, functions)
    return functions


def get_function_code(file_path, function_name):
    """Get the code of the function from the file.
    Args:
    file_path (str): The path to the file.
    function_name (str): The name of the function.
    Returns:
    str: The code of the function.
    """
    function_code = []
    capture = False
    with open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()
        for i, line in enumerate(lines):
            stripped_line = line.strip()
            if stripped_line.startswith(
                f"def {function_name}(",
            ) and stripped_line.endswith(":"):
                capture = True
                function_code.append(line)
                # Capture subsequent lines until the next double newline
                for j in range(i + 1, len(lines)):
                    if lines[j] == "\n" and lines[j + 1] == "\n":
                        break
                    function_code.append(lines[j])
                break
    return "".join(function_code)


def generate_test(function_code, is_new_function):
    """Generate a pytest test for the function.
    Args:
    function_code (str): The code of the function.
    is_new_function (bool): Whether the function is new or modified.
    Returns:
    str: The pytest test code.
    """
    chain = get_chain()
    result = chain.invoke({"function_code": function_code})

    # Extract test code from result by removing code block markers and comments
    test_code = re.findall(r"```(.*?)```", result, re.DOTALL)
    if test_code:
        test_code = test_code[0].strip()
    else:
        test_code = ""

    return test_code


def update_or_create_test_file(file_path, function_name, test_code):
    """Update or create a test file with the pytest test code.
    Args:
    file_path (str): The path to the file.
    function_name (str): The name of the function.
    test_code (str): The pytest test code.
    """
    test_file_dir = os.path.join("tests", os.path.dirname(file_path).replace("src", ""))
    if not os.path.exists(test_file_dir):
        os.makedirs(test_file_dir)
    test_file_path = os.path.join(
        test_file_dir,
        f'test_{os.path.basename(file_path).replace(".py", "")}.py',
    )

    if not os.path.exists(test_file_path):
        with open(test_file_path, "w", encoding="utf-8") as test_file:
            test_file.write(f"import pytest\n\n{test_code}")
    else:
        with open(test_file_path, "r+", encoding="utf-8") as test_file:
            existing_tests = test_file.read()
            # Regex to find if the function is already tested
            test_pattern = re.compile(rf"def test_{function_name}\(.*\):")
            if test_pattern.search(existing_tests):
                # Overwrite the existing test
                new_tests = test_pattern.sub(
                    f"def test_{function_name}():\n    {test_code}",
                    existing_tests,
                )
            else:
                # Add new test
                new_tests = f"{existing_tests}\n\n{test_code}"
            test_file.seek(0)
            test_file.write(new_tests)
            test_file.truncate()


def main():
    """Main function to generate pytest tests for new or modified functions in a Git commit."""
    repo = Repo(".")
    changed_files = get_changed_files()
    deleted_functions = get_deleted_functions(repo)
    for file_path in changed_files:
        if file_path.startswith("src/") and file_path.endswith(".py"):
            functions = parse_functions(file_path)
            for function_name in functions:
                function_code = get_function_code(file_path, function_name)
                logging.info("Generating test for %s in %s", function_name, file_path)
                is_new_function = True  # Determine if the function is new or modified (not shown here)
                test_code = generate_test(function_code, is_new_function)
                update_or_create_test_file(file_path, function_name, test_code)
                logging.info(
                    "Test for %s in %s generated and saved",
                    function_name,
                    file_path,
                )


if __name__ == "__main__":
    main()
