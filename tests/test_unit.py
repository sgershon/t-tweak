import os
import sys
import json

import requests
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
        ("2q4q6q8q11q14q17q20q", "2Q4Q6Q8Q11Q14Q17Q20Q"),
        ("q3q5q7q10q13q16q19q22q25q", "Q3Q5Q7Q10Q13Q16Q19Q22Q25Q"),
        ("3", "3"),
        ("", ""),
    ],
    ids=["single letter", "20 chars", "long string", "digit", "empty"],
)
def test_upper_many(test, expected):
    r = main.upper(test)
    j = json.loads(r.body)
    assert r.status_code == 200
    assert j["res"] == expected


def test_upper_rest_within_bv():
    r = requests.get("http://t-tweak.gershon.info/upper/word")
    assert 200 == r.status_code
    assert "WORD" == r.json()["res"]


def test_upper_rest_outside_bv():
    r = requests.get("http://t-tweak.gershon.info/upper")
    assert 404 == r.status_code
    r = requests.get("http://t-tweak.gershon.info/upper/-3-5-7-9-12-15-18-21-")
    assert 422 == r.status_code


def test_random(monkeypatch):
    monkeypatch.setattr(main, "get_rand_char", lambda: "t")
    r = main.rand_str(4)
    j = json.loads(r.body)
    assert r.status_code == 200
    assert j["res"] == "tttt"
