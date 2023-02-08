import fcntl
from typing import Union

from fastapi import FastAPI, Query, Cookie, Response


def count(increment=None):
    with open('count.cnt', 'r') as c:
        cnt = int(c.read())
    if type(increment) is int:
        with open('count.cnt', 'w+') as c:
            fcntl.flock(c, fcntl.LOCK_EX)
            c.write(str(cnt + 1))
            fcntl.flock(c, fcntl.LOCK_UN)
    return cnt

def log(msg):
  with open('log.log', 'a') as l:
    l.write(str(msg) + "\n")

log("Starting T-Tweak")

app = FastAPI()

log("T-Tweak Started")

@app.get("/")
def read_root():
    log("read_root called")
    count(1)
    return {"Status": "Operational"}

@app.get("/reverse/{string}")
def reverse(string: str):
    """ Reverses a string."""
    log(f"reverse called with: {string}")
    count(1)
    return {"res": string[::-1]}

@app.get("/upper/{string}")
def upper(string: str):
    log(f"upper called with: {string}")
    count(1)
    return {"res": string.upper()}

@app.get("/lenght/{string}")
def lenght(string: str):
    log(f"lenght called with: {string}")
    count(1)
    return {"res": str(len(string))}

@app.get("/substrings/{string}")
def substring(string:str, sub: str):
    log(f"substring called with: {string}, {sub}")
    here = 0
    res = []
    while(True):
        here = string.find(sub, here)
        if here == -1:
            break
        res.append(here)
        here += 1

    return {"res": str(res)}

@app.get("/password_strenght/{password}")
def password(password: str):
# A password should be larger than 12
# A password should include a combination of letters, numbers, and special characters.
# A password shouldn’t contain any consecutive letters or numbers.
# A password shouldn’t be the words “password”, "admin" or "root"
# A password shouldn’t be the same letter or number repeated

    score = 10
    score = len(password) - 2

    if not (sorted([ord(i) for i in password if 65 <= ord(i) <= 90])):
        score -= 2
    if not (sorted([ord(i) for i in password if 97 <= ord(i) <= 122])):
        score -= 2
    if not (sorted([ord(i) for i in password if 48 <= ord(i) <= 57])):
        score -= 2

    for i, l in enumerate(password):
        print(len(password), i, l)
        if i + 1 < len(password):
            print(l, password[i+1])
            if ord(l) + 1 == ord(password[i+1]):
                score -= 1
                print(score)
    if password in ["password", "admin", "root"]:
        score -= 7
    if len(set(password)) <= 1:
        score -= 2

    return min(max(score, 0), 10)



@app.get("/count/all")
def count_all():
    log(f"count all called")
    return {"res": str(count())}

# @app.get("/count/mine")
# def count_mine(session_count: Union[str, None] = Cookie(default=0)):
#     response = Response()
#     response.set_cookie(key="localcount", value=f"{int(session_count) + 1}")
#     return {"res": str(session_count)}



# print(
#     read_root(),
#     reverse('1234'),
#     upper('1234'),
#     lenght('1234'),
#     count_all(),
#     substring('12323232', '232'),
#     count_mine(),
# )