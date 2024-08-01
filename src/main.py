import sys


def add(a: int, b: int) -> int:
    return a + b


def subtract(a: int, b: int) -> int:
    return a - b


def multiply(a: int, b: int) -> int:
    if isinstance(a, int) and isinstance(b, int):
        return a * b
    raise TypeError()


def divide(a: int, b: int) -> float:
    return a / b


def main():
    if sys.stdout is None:
        raise ValueError("stdout is not set")
    print("Hello, world!")


if __name__ == "__main__":
    main()
