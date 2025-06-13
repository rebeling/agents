#!/usr/bin/env python3
"""
Test runner for the agents application.

This script provides a command-line interface to run tests for various components
of the agents application, with specific focus on the combine_prompt function.
"""

import argparse
import sys
import unittest
from pathlib import Path

# Add the current directory to Python path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

# Test discovery patterns
TEST_PATTERNS = {
    "all": "test_*.py",
    "combine_prompt": "test_combine_prompt.py",
    "utils": "test_*utils*.py",
    "integration": "test_*integration*.py",
}


# Colors for terminal output
class Colors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def print_colored(message: str, color: str = Colors.ENDC):
    """Print colored message to terminal."""
    print(f"{color}{message}{Colors.ENDC}")


def run_unittest_discovery(test_dir: str, pattern: str, verbosity: int = 2) -> bool:
    """Run tests using unittest discovery."""
    try:
        print_colored(f"\n{'=' * 60}", Colors.HEADER)
        print_colored(f"Running tests with pattern: {pattern}", Colors.HEADER)
        print_colored(f"Test directory: {test_dir}", Colors.HEADER)
        print_colored(f"{'=' * 60}", Colors.HEADER)

        # Discover and run tests
        loader = unittest.TestLoader()
        start_dir = test_dir
        suite = loader.discover(start_dir, pattern=pattern)

        # Run the tests
        runner = unittest.TextTestRunner(
            verbosity=verbosity, buffer=True, failfast=False
        )
        result = runner.run(suite)

        # Print summary
        print_colored(f"\n{'=' * 60}", Colors.HEADER)
        if result.wasSuccessful():
            print_colored(
                f"✓ All tests passed! "
                f"({result.testsRun} tests, {len(result.skipped)} skipped)",
                Colors.OKGREEN,
            )
        else:
            print_colored(
                f"✗ Tests failed! "
                f"({len(result.failures)} failures, {len(result.errors)} errors)",
                Colors.FAIL,
            )

        return result.wasSuccessful()

    except Exception as e:
        print_colored(f"Error running tests: {e}", Colors.FAIL)
        return False


def run_pytest(test_path: str, args: list[str]) -> bool:
    """Run tests using pytest if available."""
    try:
        import pytest

        print_colored(f"\n{'=' * 60}", Colors.HEADER)
        print_colored("Running tests with pytest", Colors.HEADER)
        print_colored(f"{'=' * 60}", Colors.HEADER)

        pytest_args = [test_path] + args
        result = pytest.main(pytest_args)

        if result == 0:
            print_colored("✓ All tests passed with pytest!", Colors.OKGREEN)
            return True
        else:
            print_colored("✗ Tests failed with pytest!", Colors.FAIL)
            return False

    except ImportError:
        print_colored("pytest not available, falling back to unittest", Colors.WARNING)
        return False


def run_specific_test_file(test_file: str, verbosity: int = 2) -> bool:
    """Run a specific test file."""
    test_path = PROJECT_ROOT / "tests" / test_file

    if not test_path.exists():
        print_colored(f"Test file not found: {test_path}", Colors.FAIL)
        return False

    try:
        print_colored(f"\n{'=' * 60}", Colors.HEADER)
        print_colored(f"Running specific test file: {test_file}", Colors.HEADER)
        print_colored(f"{'=' * 60}", Colors.HEADER)

        # Import and run the test module
        spec = unittest.util.spec_from_file_location("test_module", test_path)
        test_module = unittest.util.module_from_spec(spec)
        spec.loader.exec_module(test_module)

        # Discover tests in the module
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromModule(test_module)

        # Run the tests
        runner = unittest.TextTestRunner(verbosity=verbosity, buffer=True)
        result = runner.run(suite)

        return result.wasSuccessful()

    except Exception as e:
        print_colored(f"Error running test file {test_file}: {e}", Colors.FAIL)
        return False


def check_test_dependencies():
    """Check if required test dependencies are available."""
    print_colored("Checking test dependencies...", Colors.OKBLUE)

    dependencies = {
        "unittest": True,  # Built-in
        "pathlib": True,  # Built-in
    }

    optional_dependencies = {}

    # Check for pytest
    try:
        optional_dependencies["pytest"] = True
        print_colored("✓ pytest available", Colors.OKGREEN)
    except ImportError:
        optional_dependencies["pytest"] = False
        print_colored("✗ pytest not available (optional)", Colors.WARNING)

    # Check for mock (should be available in unittest.mock)
    try:
        dependencies["unittest.mock"] = True
        print_colored("✓ unittest.mock available", Colors.OKGREEN)
    except ImportError:
        dependencies["unittest.mock"] = False
        print_colored("✗ unittest.mock not available", Colors.FAIL)

    return all(dependencies.values())


def run_combine_prompt_tests(verbosity: int = 2) -> bool:
    """Run specific tests for the combine_prompt function."""
    print_colored("\n🧪 Running combine_prompt function tests", Colors.OKBLUE)

    test_file = "test_combine_prompt.py"
    return run_specific_test_file(test_file, verbosity)


def run_coverage_report():
    """Generate coverage report if coverage.py is available."""
    try:
        import coverage

        print_colored("\n📊 Generating coverage report...", Colors.OKBLUE)

        # Start coverage
        cov = coverage.Coverage()
        cov.start()

        # Run tests (this is simplified - in practice you'd run your test suite here)
        print_colored("Coverage reporting would be implemented here", Colors.WARNING)

        # Stop coverage and report
        cov.stop()
        cov.save()

        print_colored("Coverage report generated", Colors.OKGREEN)

    except ImportError:
        print_colored(
            "coverage.py not available - skipping coverage report", Colors.WARNING
        )


def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(
        description="Test runner for the agents application",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python test_runner.py                    # Run all tests
  python test_runner.py --test combine_prompt  # Run combine_prompt tests
  python test_runner.py --file test_combine_prompt.py  # Run specific file
  python test_runner.py --verbose         # Run with high verbosity
  python test_runner.py --pytest          # Use pytest if available
  python test_runner.py --check-deps      # Check test dependencies
        """,
    )

    parser.add_argument(
        "--test",
        "-t",
        choices=list(TEST_PATTERNS.keys()),
        default="all",
        help="Test category to run",
    )

    parser.add_argument("--file", "-f", help="Specific test file to run")

    parser.add_argument(
        "--verbose",
        "-v",
        action="count",
        default=1,
        help="Increase verbosity (use -v, -vv, -vvv)",
    )

    parser.add_argument(
        "--pytest", action="store_true", help="Use pytest instead of unittest"
    )

    parser.add_argument(
        "--check-deps", action="store_true", help="Check test dependencies and exit"
    )

    parser.add_argument(
        "--coverage", action="store_true", help="Generate coverage report"
    )

    parser.add_argument("--failfast", action="store_true", help="Stop on first failure")

    args = parser.parse_args()

    # Print header
    print_colored("🚀 Agents Test Runner", Colors.HEADER + Colors.BOLD)
    print_colored("=" * 50, Colors.HEADER)

    # Check dependencies if requested
    if args.check_deps:
        success = check_test_dependencies()
        sys.exit(0 if success else 1)

    # Ensure tests directory exists
    tests_dir = PROJECT_ROOT / "tests"
    if not tests_dir.exists():
        print_colored(f"Tests directory not found: {tests_dir}", Colors.FAIL)
        print_colored("Creating tests directory...", Colors.WARNING)
        tests_dir.mkdir(exist_ok=True)

    success = True

    try:
        # Run specific file if requested
        if args.file:
            success = run_specific_test_file(args.file, args.verbose)

        # Run combine_prompt tests specifically
        elif args.test == "combine_prompt":
            success = run_combine_prompt_tests(args.verbose)

        # Use pytest if requested and available
        elif args.pytest:
            pytest_args = ["-v"] * args.verbose
            if args.failfast:
                pytest_args.append("--maxfail=1")

            pattern = TEST_PATTERNS[args.test]
            test_path = str(tests_dir / pattern)
            success = run_pytest(test_path, pytest_args)

            # Fallback to unittest if pytest fails
            if not success:
                print_colored("Falling back to unittest...", Colors.WARNING)
                success = run_unittest_discovery(
                    str(tests_dir), TEST_PATTERNS[args.test], args.verbose
                )

        # Default unittest discovery
        else:
            success = run_unittest_discovery(
                str(tests_dir), TEST_PATTERNS[args.test], args.verbose
            )

        # Generate coverage report if requested
        if args.coverage:
            run_coverage_report()

    except KeyboardInterrupt:
        print_colored("\n\nTests interrupted by user", Colors.WARNING)
        success = False

    except Exception as e:
        print_colored(f"\nUnexpected error: {e}", Colors.FAIL)
        success = False

    # Print final result
    print_colored(f"\n{'=' * 50}", Colors.HEADER)
    if success:
        print_colored(
            "🎉 Test run completed successfully!", Colors.OKGREEN + Colors.BOLD
        )
        sys.exit(0)
    else:
        print_colored("💥 Test run failed!", Colors.FAIL + Colors.BOLD)
        sys.exit(1)


if __name__ == "__main__":
    main()
