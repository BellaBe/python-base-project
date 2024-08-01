import argparse
import ast
import os
import re

from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq

load_dotenv()


def extract_code(text):
    """
    Extracts code blocks containing function definitions from the provided text.

    Args:
    text (str): The input text containing code and descriptions.

    Returns:
    str: The extracted code.
    """
    code_blocks = re.findall(r"```(.*?)```", text, re.DOTALL)
    function_blocks = [block for block in code_blocks if re.search(r"def\s+\w+\s*\(", block)]
    extracted_code = "\n\n".join(function_blocks)
    return extracted_code.strip()


def get_chain():
    """Get the language model chain for unit tests.

    Returns:
    chain: The language model chain.
    """
    model_name = "llama3-70b-8192"
    api_key = os.getenv("GROQ_API_KEY", None)
    if api_key is None:
        raise ValueError("Please set the GROQ_API_KEY environment variable.")
    llm = ChatGroq(model=model_name, api_key=api_key)

    instructions = """
    **Role:** Software Tester
    **Objective:** Create a comprehensive set of unit test cases for a given code snippet to ensure
      its functionality and identify potential errors.
    **Target Audience:** Software Developers, Quality Assurance Teams

    **Instructions:**
    1. Review the provided `{function_code}` and identify the key functionality and potential areas of error.
    2. Write a set of test cases to validate the correctness of the code. Include:
        * Positive test cases: Verify the code's expected behavior.
        * Negative test cases: Verify the code's error handling, such as invalid inputs (e.g., wrong types).
        * Edge cases: Push the code's functionality to its limits, such as handling very large inputs.
    3. Ensure test cases are clear, concise, and well-structured. Use descriptive names and comments.
    4. Provide a brief explanation for each test case. Outline the expected outcome and any assumptions made.
    5. Name the test cases following the convention `test_functionname_scenario`, e.g., `test_add_positive_numbers`.

    **Constraints:**
        * Do not duplicate test cases or scenarios.
        * Ensure test cases are independent and do not interfere with each other.
        * When testing for potential overflow conditions, include custom checks since Python's int
          type handles large integers gracefully without raising `OverflowError`.

    **Output Requirements:**
        * Include a minimum of 5 test cases: at least 2 positive, 2 negative, and 1 edge case.
        * Ensure each test case includes:
            + A descriptive name.
            + A clear explanation of the test scenario.
            + The expected outcome.
            + Any necessary setup or teardown code.
        * Write the output in a format compatible with Python and easily executable by pytest testing framework.
        * Return only the test cases without any additional code
        * Do not add comments of suggestions
        * Do not modify tested function, use it as it is

    **Additional Guidance:**
        * Consider the code snippet's functionality, inputs, and expected outputs when creating test cases.
        * Do not modify code snippet, test it as it is
        * Cover a range of scenarios, including normal operation, error handling, and boundary cases.
        * When testing for errors like `OverflowError` or `TypeError`, ensure that the function
          implementations explicitly raise these exceptions when the conditions are met.

    """

    prompt = PromptTemplate.from_template(instructions)
    chain = prompt | llm | StrOutputParser()
    return chain


class FunctionVisitor(ast.NodeVisitor):
    def __init__(self):
        self.functions = []

    def visit_FunctionDef(self, node):
        self.functions.append(node)
        self.generic_visit(node)


def parse_functions(file_path):
    """Parse the file to extract function definitions."""
    with open(file_path, "r") as file:
        tree = ast.parse(file.read())
    visitor = FunctionVisitor()
    visitor.visit(tree)
    return visitor.functions


def parse_test_functions(test_file_path):
    """Parse the test file to extract test function definitions."""
    if not os.path.exists(test_file_path):
        return []

    with open(test_file_path, "r") as file:
        tree = ast.parse(file.read())
    visitor = FunctionVisitor()
    visitor.visit(tree)
    return visitor.functions


def generate_test(function_code, function_name, file_name, is_new_function):
    """Generate a pytest test for the function.

    Args:
    function_code (str): The code of the function.
    function_name (str): The name of the function.
    file_name (str): The name of the file containing the function.
    is_new_function (bool): Whether the function is new or modified.

    Returns:
    str: The pytest test code.
    """
    chain = get_chain()
    result = chain.invoke({"function_code": function_code})
    test_code = extract_code(result)

    import_statement = f"from {os.path.splitext(os.path.basename(file_name))[0]} import {function_name}\n\n"
    return import_statement + test_code


def ensure_tests_dir():
    """Ensure that the 'tests' directory exists."""
    if not os.path.exists("tests"):
        os.makedirs("tests")


def update_test_file(test_code, test_file):
    """Update the test file with the generated test cases."""
    ensure_tests_dir()
    test_file_path = os.path.join("tests", test_file)
    if os.path.exists(test_file_path):
        with open(test_file_path, "r") as file:
            existing_content = file.read()
    else:
        existing_content = ""

    if not test_code.splitlines()[0] in existing_content:
        with open(test_file_path, "a") as file:
            file.write(test_code)


def main(files_to_test, functions_to_test=None):
    for file in files_to_test:
        functions = parse_functions(file)
        test_file = f"test_{os.path.splitext(os.path.basename(file))[0]}.py"
        test_file_path = os.path.join("tests", test_file)
        tested_functions = [f.name for f in parse_test_functions(test_file_path)]
        for func in functions:
            if functions_to_test is None or func.name in functions_to_test or "all" in functions_to_test:
                func_code = ast.unparse(func)
                is_new_function = func.name not in tested_functions
                test_code = generate_test(func_code, func.name, file, is_new_function)
                update_test_file(test_code, test_file)
                print(f"Updated {test_file} with tests for function {func.name}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Automate the generation of unit test cases for specified functions.")
    parser.add_argument("--files", nargs="+", required=True, help="List of files to test")
    parser.add_argument(
        "--functions",
        nargs="+",
        help="List of functions to test or 'all' to test all functions in the file",
    )
    args = parser.parse_args()
    main(files_to_test=args.files, functions_to_test=args.functions)
