import os
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


def test_random(monkeypatch):
    monkeypatch.setattr(main, "get_rand_char", lambda: "t")
    r = main.rand_str(4)
    j = json.loads(r.body)
    assert r.status_code == 200
    assert j["res"] == "tttt"
