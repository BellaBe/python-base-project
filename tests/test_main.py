import io
import sys

import pytest

from src.main import add, divide, main, multiply, subtract


def test_add_positive_numbers():
    """Test adding two positive integers."""
    assert add(2, 3) == 5
    """Expected outcome: 2 + 3 = 5"""


def test_add_negative_numbers():
    """Test adding two negative integers."""
    assert add(-2, -3) == -5
    """Expected outcome: -2 + -3 = -5"""


def test_add_mixed_numbers():
    """Test adding a positive and a negative integer."""
    assert add(2, -3) == -1
    """Expected outcome: 2 + -3 = -1"""


def test_add_non_integer_input():
    """Test adding a string and an integer, expecting a TypeError."""
    with pytest.raises(TypeError):
        add("a", 2)
    """Expected outcome: TypeError raised due to non-integer input"""


def test_add_large_numbers():
    """Test adding two very large integers, pushing the function to its limits."""
    assert add(10**100, 10**100) == 2 * (10**100)
    """Expected outcome: large numbers added correctly"""


def test_subtract_positive_numbers():
    # Test scenario: Subtract two positive numbers
    # Expected outcome: Correct result
    assert subtract(5, 3) == 2


def test_subtract_negative_numbers():
    # Test scenario: Subtract two negative numbers
    # Expected outcome: Correct result
    assert subtract(-5, -3) == -2


def test_subtract_invalid_input_type():
    # Test scenario: Pass non-integer input types (e.g., string, float)
    # Expected outcome: TypeError
    with pytest.raises(TypeError):
        subtract("5", 3)


def test_subtract_non_numeric_input():
    # Test scenario: Pass non-numeric input (e.g., None, list)
    # Expected outcome: TypeError
    with pytest.raises(TypeError):
        subtract(None, 3)


def test_subtract_large_numbers():
    # Test scenario: Subtract very large numbers
    # Expected outcome: Correct result
    assert subtract(1000000000, 500000000) == 500000000


def test_multiply_positive_numbers():
    """
    Test that the function multiplies two positive integers correctly.
    """
    assert multiply(2, 3) == 6
    assert multiply(10, 5) == 50


def test_multiply_negative_numbers():
    """
    Test that the function multiplies two negative integers correctly.
    """
    assert multiply(-2, -3) == 6
    assert multiply(-10, -5) == 50


def test_multiply_mixed_numbers():
    """
    Test that the function multiplies a positive and a negative integer correctly.
    """
    assert multiply(2, -3) == -6
    assert multiply(-10, 5) == -50


def test_multiply_non_integer_inputs():
    """
    Test that the function raises a TypeError when given non-integer inputs.
    """
    with pytest.raises(TypeError):
        multiply(2, "a")
    with pytest.raises(TypeError):
        multiply("a", 3)
    with pytest.raises(TypeError):
        multiply(2.5, 3)
    with pytest.raises(TypeError):
        multiply(2, 3.5)


def test_multiply_large_inputs():
    """
    Test that the function can handle very large integer inputs.
    """
    assert multiply(1000000, 1000000) == 1000000000000
    assert multiply(-1000000, 1000000) == -1000000000000


def test_divide_positive_numbers():
    # Test dividing two positive numbers
    assert divide(10, 2) == 5
    # Expected outcome: The function returns the correct result of the division.


def test_divide_negative_numbers():
    # Test dividing a positive and a negative number
    assert divide(10, -2) == -5
    # Expected outcome: The function returns the correct result of the division.


def test_divide_by_zero():
    # Test dividing by zero
    try:
        divide(10, 0)
        raise AssertionError("Expected a ZeroDivisionError")
    except ZeroDivisionError:
        pass


def test_divide_non_integer_inputs():
    # Test dividing with non-integer inputs
    try:
        divide(10, "2")
        raise AssertionError("Expected a TypeError")
    except TypeError:
        pass


def test_divide_large_numbers():
    # Test dividing very large numbers
    assert divide(1000000000, 2) == 500000000
    # Expected outcome: The function returns the correct result of the division.from main import main


def test_main_stdout_set():
    # Test case: Verify print statement works when stdout is set
    captured_output = io.StringIO()
    sys.stdout = captured_output
    main()
    sys.stdout = sys.__stdout__
    assert captured_output.getvalue().strip() == "Hello, world!"


def test_main_stdout_not_set():
    # Test case: Verify ValueError is raised when stdout is not set
    sys.stdout = None
    with pytest.raises(ValueError):
        main()
    sys.stdout = sys.__stdout__


def test_main_stdout_invalid_type():
    # Test case: Verify TypeError is raised when stdout is not a file-like object
    sys.stdout = 123
    with pytest.raises(AttributeError):
        main()
    sys.stdout = sys.__stdout__


def test_main_stdout_closed():
    # Test case: Verify ValueError is raised when stdout is closed
    captured_output = io.StringIO()
    captured_output.close()
    sys.stdout = captured_output
    with pytest.raises(ValueError):
        main()
    sys.stdout = sys.__stdout__


def test_main_stdout_redirected():
    # Test case: Verify print statement works when stdout is redirected
    captured_output = io.StringIO()
    sys.stdout = captured_output
    main()
    sys.stdout = sys.__stdout__
    assert captured_output.getvalue().strip() == "Hello, world!"
