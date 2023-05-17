""" Example functions for Unit Test Class"""

import os
import sys
import json

import fastapi.exceptions
import pytest
from fastapi.testclient import TestClient

# Makes it easier to run in students' Windows's laptops, with no need to set path vars
sys.path.append(os.path.dirname(os.path.abspath(__name__)))
import main

# Client that gives us access to a dummy server for HTTP tests
client = None

# ---------------------------------------------------------------------------
# Setup and Teardown functions.
# These are examples of the functions used by pytest to prepare and dismantle
#   the entire test suite, or to prepare and dismantle each one of the tests.
#   You can, for example, setup services, states, or other operating environments.
# Advanced usage: You can also have setup/teardown functions for specific tests,
#   or for specific groups of tests.
#
# To see the output of the setup/teardown functions, run pytest with the argument:
#   --capture=no (as in pytest -v --capture=no)
# ---------------------------------------------------------------------------
def setup_module(module):
    print('\n==> THIS WILL HAPPEN *before all* THE TESTS BEGIN')
    # For example, copy test data into the test suite
    # For example, set a dummy server running (like the TestClient)
    print('==> START!')

    global client
    client = TestClient(main.app)

def teardown_module(module):
    print('\n==> THIS WILL HAPPEN *after all* THE TESTS END')
    # For example, delete test files and output files
    print('==> FINISH!')

    global client
    client = None


def setup_function():
    print('\n--> This will happen BEFORE each one of the tests begin')
    # For example, cleanup temp files
    # For example, get information on resources available


def teardown_function():
    print('\n--> This will happen AFTER each one of the tests ends')
    # For example, release handles


# ---------------------------------------------------------------------------
# TEST 1: Transform a text to lowercase. Simple!
# Amounts to 1 test in the total unit tests
# ---------------------------------------------------------------------------
def test_lower_ABCD():
    r = main.lower("ABCD")
    j = json.loads(r.body)
    assert r.status_code == 200
    assert j["res"] == "abcd"


# ---------------------------------------------------------------------------
# TEST 2: Transform to uppercase a number of strings. Still simple, notice how
#   the framework allows to perform one test on multiple variables without
#   repeating the test.
# Amounts to 7 tests in the total unit tests
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "test,expected",
    [
        ("", ""),
        ("a", "A"),
        ("q3q5q7q10", "Q3Q5Q7Q10"),
        ("2q4q6q8q11q14q17q20q", "2Q4Q6Q8Q11Q14Q17Q20Q"),
        ("q3q5q7q10q13q16q19q22q25q", "Q3Q5Q7Q10Q13Q16Q19Q22Q25Q"),
        ("3", "3"),
        ("abc#$%def", "ABC#$%DEF"),
    ],
    ids=["empty", "single letter", "10 chars", "20 chars", "long string", "digit", "special chars"],
)
def test_upper_many(test, expected):
    r = main.upper(test)
    j = json.loads(r.body)
    assert r.status_code == 200
    assert j["res"] == expected


# ---------------------------------------------------------------------------
# TEST 3: T-Tweak has our tweak functions (units) running on top of a web server
#   that has specific configurations to deal with the user input (so it's another unit).
#   Luckily fastapi let's us separate that unit as well with a dummy server.
# Amounts to 1 test in the total unit tests
# ---------------------------------------------------------------------------
def test_upper_rest_within_bv():
    r = client.get("upper/word")
    assert 200 == r.status_code
    assert "WORD" == r.json()["res"]


# ---------------------------------------------------------------------------
# TEST 4: Using the dummy server, for negative tests.
# Amounts to 1 test in the total unit tests
# ---------------------------------------------------------------------------
def test_upper_rest_outside_bv():
    r = client.get("upper")
    assert 404 == r.status_code
    r = client.get("upper/-3-5-7-9-12-15-18-21-")
    assert 422 == r.status_code


# ---------------------------------------------------------------------------
# TEST 6: Functions with complex dependencies may require us to work around the
#   complexity by controlling some of the environment.
#   This is not always possible and not always effective.
# Amounts to 1 tests in the total unit tests
# ---------------------------------------------------------------------------
def test_random_naive():
    main.reset_random(0)
    r = main.rand_str(4)
    j = json.loads(r.body)

    assert r.status_code == 200
    assert j["res"] == "2yW4"

    r = main.rand_str(15)
    j = json.loads(r.body)

    assert r.status_code == 200
    assert j["res"] == "Acq9GFz6Y1t9EwL"

# ---------------------------------------------------------------------------
# TEST 6: For functions with complex dependencies.
#   We can create a stub of the dependencies, replacing it with a fake function
#       of our own. Then we have full control.
# Amounts to 1 tests in the total unit tests
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "length",
    [1, 10, 20, 50],
)
def test_random_unit(monkeypatch, length):
def test_password_length_score():
    password = "".join(random.choices("abcXYZ123!@#", k=20))

    while len(password) >= 1:
        r_large = main.password_strength(password)
        j_large = json.loads(r_large.body)

        password = password[:-1]
        r_small = main.password_strength(password)
        j_small = json.loads(r_small.body)

        assert 200 == r_large.status_code
        assert 200 == r_small.status_code
        assert j_large["res"] >= j_small["res"]


def test_random(monkeypatch):
    monkeypatch.setattr(main, "get_rand_char", lambda: "t")
    r = main.rand_str(length)
    j = json.loads(r.body)
    assert r.status_code == 200
    assert j["res"] == "t"*length


# ---------------------------------------------------------------------------
# TEST 6: T-Tweak functions also throw exceptions when something is not right
#   (for example, when we need to send a different HTTP status). We have to
#   test that too! Unit Test frameworks allow the test to expect a specific
#   Exception. Useful, uh?
# Amounts to 1 test in the total unit tests
# ---------------------------------------------------------------------------
def test_with_exception():
    # 'raises' checks that the exception is raised
    with pytest.raises(fastapi.exceptions.HTTPException):
        main.substring("course 67778", 3, 2)


# ---------------------------------------------------------------------------
# TEST 7: Unit test frameworks allow setting conditions to skip tests.
#   Sometimes a test may be suitable for a platform but not another, for a version
#   but not another, etc.
# Amounts to 1 test in the total unit tests
# ---------------------------------------------------------------------------
@pytest.mark.skipif(fastapi.__version__ > "0.95", reason="requires fastapi <= 0.95")
def test_root_status():
    r = client.get("/")
    assert "Operational" == r.json()["res"]
