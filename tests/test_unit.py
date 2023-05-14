import os
import random
import sys
import json

import pytest

# Makes it easier to run in students' Windows's laptops
sys.path.append(os.path.dirname(os.path.abspath(__name__)))
import main


def test_lower_ABCD():
    r = main.lower("ABCD")
    j = json.loads(r.body)
    assert r.status_code == 200
    assert j["res"] == "abcd"


@pytest.mark.parametrize(
    "test,expected",
    [
        ("a", "A"),
        ("aaaaaaaaaaaaaaaa", "AAAAAAAAAAAAAAAA"),
        ("Lorem ipsum dolor sit amet", "LOREM IPSUM DOLOR SIT AMET"),
        ("3", "3"),
    ],
)
def test_upper_many(test, expected):
    r = main.upper(test)
    j = json.loads(r.body)
    assert r.status_code == 200
    assert j["res"] == expected


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
    r = main.rand_str(4)
    j = json.loads(r.body)
    assert r.status_code == 200
    assert j["res"] == "tttt"
