""" All the t-tweak functions. Called "main" to fit most uvicorn's server standard tutorials."""

import os
import string
import random
import datetime
from typing import List

from fastapi import FastAPI, Path, Query, HTTPException, status as http_status, Request
from fastapi.responses import Response, JSONResponse, FileResponse, PlainTextResponse
from starlette.middleware.sessions import SessionMiddleware
from pydantic import BaseModel

# The "extra" module is for external functions that are considered out of the programmer's control.
import extra

# "fcntl" is a linux module, important to control file access in a multi-client web server.
#   In Windows it doesn't exist, and for students to run locally we invented a mock for
#   the module. Adds but a tiny risk of concomitant write to logs, a non issue.
try:
    import fcntl
except ModuleNotFoundError:
    import win_fctl as fcntl

description = """
T-Tweak helps you tweak text! 🖉

### All functions log their usage, so don't write anything secret!
"""
app = FastAPI(
    title="T-Tweak API",
    description=description,
    version="0.0.1",
    contact={
        "name": "67778 Course",
    },
    swagger_ui_parameters={"defaultModelsExpandDepth": -1},
)
ttweak_key = "course67778isthebestinhuji"

random_seed = 5
extra.reset_random(random_seed)


# ## ### ### ### ###
# Classes used to model de data structures for the REST responses.


class StringOut(BaseModel):
    res: str


class ListStringOut(BaseModel):
    res: List[str]


class IntOut(BaseModel):
    res: int


class ListIntOut(BaseModel):
    res: List[int]


class Message(BaseModel):
    detail: str


# ## ### ### ### ###
# Logging files and the functions that fill them

# Use /tmp for serverless environments like Vercel (filesystem is read-only except /tmp)
count_file = "/tmp/count.cnt" if os.environ.get("VERCEL") else "logs/count.cnt"
hist_file = "/tmp/history.txt" if os.environ.get("VERCEL") else "logs/history.txt"
log_file = "/tmp/log.log" if os.environ.get("VERCEL") else "logs/log.log"


def count(increment=None):
    try:
        cnt = 0
        if os.path.isfile(count_file):
            with open(count_file, "r") as c:
                r = c.read()
                cnt = int(r) if r.isnumeric() else 0
        if type(increment) is int:
            with open(count_file, "w+") as c:
                fcntl.flock(c, fcntl.LOCK_EX)
                c.write(str(cnt + 1))
                fcntl.flock(c, fcntl.LOCK_UN)
        return cnt
    except Exception:
        # Silently fail in serverless environments where filesystem may be restricted
        return 0


def history(new_string=None):
    try:
        hist = []
        if os.path.isfile(hist_file):
            with open(hist_file, "r") as h:
                hist = h.readlines()
        if new_string:
            hist.append(f"{new_string}\n")
            with open(hist_file, "w") as h:
                fcntl.flock(h, fcntl.LOCK_EX)
                h.writelines(hist[-50:])
                fcntl.flock(h, fcntl.LOCK_UN)

        return [h.strip() for h in hist]
    except Exception:
        # Silently fail in serverless environments where filesystem may be restricted
        return []


def log(msg):
    try:
        items = []
        if os.path.isfile(log_file):
            with open(log_file, "r") as l:
                items = l.readlines()
        if msg:
            items.append(f"{datetime.datetime.now().strftime('%c')} {str(msg)}\n")
            with open(log_file, "w") as l:
                fcntl.flock(l, fcntl.LOCK_EX)
                l.writelines(items[-250:])
                fcntl.flock(l, fcntl.LOCK_UN)
    except Exception:
        # Silently fail in serverless environments where filesystem may be restricted
        pass

log("Starting T-Tweak")


def log_count_history(l=True, h=True, c=True, **kwargs):
    msg = kwargs.get("msg", None)
    if msg:
        if l:
            log(msg)
        if h:
            history(msg)
    inc = kwargs.get("inc", None)
    if c:
        count(inc)


# ## ### ### ### ###
# REST Functions and their responses

log("Starting T-Tweak")


@app.get("/", response_model=StringOut)
def root():
    """Provides status of the t-tweak service.

    Return Type: str"""
    log("root")

    return JSONResponse(content={"Status": "Operational (review)"})


@app.get("/robots.txt", include_in_schema=False)
def robots():
    """Returns the robots.txt file."""
    robs = """User-agent: *
Disallow: /
"""
    return Response(content=robs, media_type="text/plain")


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("favicon.ico")


@app.get("/count/all", response_model=IntOut)
def count_all():
    """Provides the count of text tweaks serviced by t-tweak.

    Return Type: int
    """
    log(f"count all")

    return JSONResponse(content={"res": count()})


@app.get("/history", response_model=ListStringOut)
def get_history():
    """The history of text tweaks serviced by t-tweak is returned by this function.

    Return Type: str
    """
    log("get_history")

    return JSONResponse(content=history())


@app.get("/length/{text}", response_model=IntOut)
def get_length(text: str = Path(..., description="Text to be measured", max_length=100)):
    """Calculates the length of a text provided.

    Return Type: str
    """
    log_count_history(l=True, h=True, c=True, msg=f"length {text}", inc=1)

    return JSONResponse(content={"res": str(len(text))})


@app.get("/reverse/{text}", response_model=StringOut)
def reverse(text: str = Path(..., description="Text to be reversed", max_length=100)):
    """Calculates the length of a text provided. 

    Return Type: str
    """
    log_count_history(l=True, h=True, c=True, msg=f"reverse {text}", inc=1)

    return JSONResponse(content={"res": text[::-1]})


@app.get("/upper/{text}", response_model=StringOut)
def upper(
    text: str = Path(..., description="Text to convert to upper case")
):
    """Converts a text to all-uppercase.

    Return Type: str
    """
    log_count_history(l=True, h=True, c=True, msg=f"upper {text}", inc=1)

    return JSONResponse(content={"res": text.upper()})


@app.get("/tolower/{text}", response_model=StringOut)
def tolower(
    text: str = Path(..., description="Text to convert to lower case", max_length=100)
):
    """Converts a text to all lowercase.

    Return Type: int
    """
    log_count_history(l=True, h=True, c=True, msg=f"lower {text}", inc=1)

    return JSONResponse(content={"res": text.lower()})


@app.get("/mix_case/{text}", response_model=StringOut)
def mix_case(
    text: str = Path(..., description="Text to alternate cases", max_length=100)
):
    """Text will have the case of its letters alternate between lower and upper case.

    Non-alphabetic characters are left untouched.

    Return Type: str
    """
    log_count_history(l=True, h=True, c=True, msg=f"mix_case {text}", inc=1)

    res = "".join([l.upper() if i % 2 else l.lower() for i, l in enumerate(text)])

    return JSONResponse(content={"res": res})


@app.get("/find/{string}/{sub}", response_model=ListIntOut)
def find(
    string: str = Path(
        ...,
        description="String A",
        max_length=8,
    ),
    sub: str = Path(
        ...,
        description="String B",
        max_length=10,
    ),
):
    """Finds strings inside strings.

    Returns the locations of one string within the other

    Return Type: list[int]
    """
    log_count_history(l=True, h=True, c=True, msg=f"find {string}, {sub}", inc=1)

    here = 0
    res = []
    while True:
        here = string.find(sub, here)
        if here == -1:
            break
        res.append(here)
        here += 1

    return JSONResponse(content={"res": res})


@app.get(
    "/substring/{string}/{start}/{end}",
    response_model=StringOut,
    responses={
        409: {"model": Message, "description": "Conflict (incompatible start and end)"},
    },
)
def substring(
    string: str = Path(
        ...,
        description="A string to extract a slice from.",
        max_length=100,
    ),
    start: int = Path(..., description="Where to end the extraction", ge=0, le=100),
    end: int = Path(..., description="Where to start the extraction", ge=0, le=100),
):
    """Extracts a substring from a larger string.

    Returns the resultign string based on the start and end positions (index starts at 0).

    Return Type: str
    """
    log_count_history(
        l=True, h=True, c=True, msg=f"substring {string}, {start}:{end}", inc=1
    )

    if end < start:
        raise HTTPException(
            status_code=http_status.HTTP_409_CONFLICT,
            detail=f"Conflict (incompatible start and end)",
        )

    return JSONResponse(content={"res": string[start:end]})


@app.get("/password/{password}", response_model=IntOut)
def password_strength(
    password: str = Path(
        ...,
        description="Your password. *Do not use a real one*, it gets logged and is publicly visible.",
        max_length=100, min_length=6,
    )
):
    """A strength score for passwords between 0 and 10. Is your password strong enough?.

    0 is a weak password, 10 is a strong password.

    Return Type: int
    """
    log_count_history(l=True, h=True, c=True, msg=f"password {password}", inc=1)

    score = 10

    if len(password) > 20:
        return JSONResponse(content={"res": -1})

    if len(password) == 0:
        return JSONResponse(content={"res": -2})


    # A password should be larger than 12
    if len(password) < 12:
        distance = 12 - len(password)
        score = score - distance

    # A password should NOT be the same letter or number repeated
    if len(set(password)) <= 1:
        score -= 7
        return JSONResponse(content={"res": min(max(score, 0), 10)})

    # A password should NOT be the words “password”, "admin" or "root"
    if password in ["password", "admin", "root"]:
        score = 0

    # A password should include upper case letter(s), lower case letter(s), and number(s).
    if not [ord(i) for i in password if 65 <= ord(i) <= 90]:
        score -= 2
    if not [ord(i) for i in password if 97 <= ord(i) <= 122]:
        score -= 2
    if not [ord(i) for i in password if 48 <= ord(i) <= 57]:
        score -= 2

    # A password shouldn’t contain any consecutive letters or numbers.
    for i, l in enumerate(password):
        # BUG: this will reduce score for consecutive ordinal values that cross char groups
        if i + 1 < len(password):
            if ord(l) + 1 == ord(password[i + 1]):
                score -= 1

    log(f"password {password} {score}")

    return JSONResponse(content={"res": min(max(score, 0), 10)})


@app.get("/counterstring/{length}/{char}", response_model=StringOut)
def counterstring(
    length: int = Path(
        ..., description="Size of a string to generate with the length of it being the given length and the separation string, which can be any character, is marking the location whose number is to the left of it in the string ", ge=0, le=150
    ),
    char: str = Path(
        ...,
        description="Character to use as the counterstring measure mark",
        max_length=100,
    ),
):
    """Generates a counterstring, a string that measures itself, and helps you measure software.

    Learn more about counterstrings here: https://www.satisfice.com/blog/archives/45

    Return Type: counterstring
    """
    log_count_history(
        l=True, h=True, c=True, msg=f"counterstring {length} {char}", inc=1
    )

    # A discussion on counterstring algorithms is available at https://www.eviltester.com/2018/05/counterstring-algorithms.html
    # This implementation is copied from https://github.com/deefex/pyclip/blob/master/pyclip/counterstring.py
    counterstring = ""

    while length > 0:
        next_count = char + str(length)[::-1]
        if len(next_count) > length:
            next_count = next_count[:length]
        counterstring = counterstring + next_count
        length -= len(next_count)

    counterstring = counterstring[::-1]

    return JSONResponse(content={"res": counterstring})


def reset_random(seed):
    log(f"Setting seed {seed}")
    random.seed(seed)


random_seed = 5
reset_random(random_seed)


@app.get("/random", response_model=StringOut)
def rand_str(
    length: int = Query(
        ..., description="Size of the desired random string", ge=0, le=150
    )
):
    """Generates a random string of desired size.

    Return Type: str
    """
    log_count_history(l=False, h=True, c=True, msg=f"random {length}", inc=1)

    random_string = "".join(
        random.choices(string.ascii_letters + string.digits, k=length)
    )

    # with open("random.txt", "r") as r:
    #     rnd = r.read()

    # prefix = []
    # for letter in rnd:
    #     ordinal = ord(letter) + 1
    #     if ord(letter) == 122:
    #         ordinal = 97
    #     if ord(letter) == 90:
    #         ordinal = 65
    #     if ord(letter) == 57:
    #         ordinal = 48
    #     prefix.append(chr(ordinal))
       
    # prefix = "".join(prefix)[:length]

    # final_random = prefix + random_string[len(rnd) :]

    # with open("random.txt", "w+") as r:
    #     fcntl.flock(r, fcntl.LOCK_EX)
    #     r.write(final_random)
    #     fcntl.flock(r, fcntl.LOCK_UN)

    log(f"random {length} {random_string}")

    return JSONResponse(content={"res": random_string})


@app.get("/anagrams/{text}", response_model=ListStringOut)
def anagrams(

):
    """Finds anagrams for the text provided.

    If more than one anagram is found, all of the anagrams are returned within a list.

    Return Type: list[str]
    """
    log_count_history(l=True, h=True, c=True, msg=f"anagrams {text}", inc=1)

    import words

    all_words = words.words.copy()

    text = text.lower()
    key = "".join(sorted(text))
    anagrams = all_words.get(key, []).copy()

    if text in anagrams:
        anagrams.remove(text)

    return JSONResponse(content={"res": anagrams})


@app.get(
    "/time",
    responses={500: {"model": Message, "description": "Non Authoritative Information"}},
    response_model=Message,
)
def server_time():
    """Retrieves the server time. For debug purposes.

    Return Type: str
    """
    log_count_history(l=True, h=True, c=True, msg=f"server_time", inc=1)

    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=f"{datetime.datetime.now().strftime('%c')}",
    )

    return JSONResponse(content={"res": f"{datetime.datetime.now().strftime('%c')}"})


@app.get("/reset_server", response_model=StringOut)
def server_reset():
    """Resets the server: reinitializes history and count.

    Return Type: str
    """

    # We reset history and count, but leave the log intact

    try:
        with open(count_file, "w") as c:
            fcntl.flock(c, fcntl.LOCK_EX)
            c.write("0\n")
            fcntl.flock(c, fcntl.LOCK_UN)

        with open(hist_file, "w") as h:
            fcntl.flock(h, fcntl.LOCK_EX)
            h.write("")
            fcntl.flock(h, fcntl.LOCK_UN)
    except Exception:
        # Silently fail in serverless environments where filesystem may be restricted
        pass

    # Reset also the random seed (results should repeat) and
    extra.reset_random(random_seed)
    log(f"Setting seed {random_seed}")

    # Reset and clear the storage
    machine = StateMachine(request)
    machine.act(command="stop")

    log_count_history(l=True, h=True, c=True, msg=f"reset_server", inc=1)

    return JSONResponse(content={"res": f"Server reset"})


class StateMachine:
    def __init__(self, request) -> None:
        self.session = request.session
        self.state = "not set"

        machine = self.session.get(ttweak_key)
        if not machine:
            machine = self.session[ttweak_key] = {"state": "start", "strings": []}
        self.machine = machine

    # start -add-> adding
    # adding -+string-> adding
    # adding -+string-> full

    def move_state(self, new_state):
        self.state = new_state
        self.machine["state"] = self.state

    def get_state(self):
        return self.machine["state"]

    def add_string(self, string):
        self.machine["strings"].append(string)

    def get_strings(self):
        return self.machine["strings"]

    def clear_strings(self):
        self.machine["strings"] = []

    def act(self, command, index=None):
        current_state = self.get_state()
        if "stop" == command or "clear" == command:
            self.clear_strings()
            self.move_state("start")
        if "start" == current_state:
            if "add" == command:
                self.move_state("adding")
        elif "adding" == current_state:
            self.add_string(command)
            if len(self.get_strings()) >= 5:
                self.move_state("full")
        elif "full" == current_state:
            if "query" == command:
                if index is not None:
                    if 0 <= index <= (len(self.get_strings()) - 1):
                        return self.get_strings()[index]
                    else:
                        # TODO: Return Error!
                        pass
                else:
                    # TODO: Return Error!
                    pass
        else:
            # TODO: Return Error!
            pass

        return self.machine
        # return "Ok"


@app.get("/storage/{command}", response_model=StringOut)
def storage(
    request: Request,
    command: str = Path(
        ..., description="Command for the string storage engine.", max_length=100
    ),
    index: int = None
    # Query(
    #     ...,
    #     default=None,
    #     description="Index of word to retrieve from the 5 collected (0-4)",
    #     ge=0,
    #     le=4,
    # ),
):
    log_count_history(l=True, h=True, c=True, msg=f"storage {command}", inc=1)

    machine = StateMachine(request)
    return JSONResponse(content={"res": machine.act(command, index)})


app.add_middleware(SessionMiddleware, secret_key=ttweak_key)
log("T-Tweak Started")


if __name__ == "__main__":
    pass
