import os
import sys
import json

# Makes it easier to run in students' Windows's laptops
sys.path.append(os.path.dirname(os.path.abspath(__name__)))
import main

def parse_json(json_str):
    j = json.loads(json_str)
    return j


def test_lower():
    r = main.lower("ABCD")
    j = json.loads(r.body)
    assert r.status_code == 200
    assert j["res"] == "abcd"
