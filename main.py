""" All the t-tweak functions. Called "main" to fit most uvicorn's server standard tutorials."""

import os
import datetime
from typing import List

from fastapi import FastAPI, Path, Query, HTTPException, status as http_status, Request
from fastapi.responses import Response, JSONResponse, FileResponse
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

count_file = "logs/count.cnt"
hist_file = "logs/history.txt"
log_file = "logs/log.log"


def count(increment=None):
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


def history(new_string=None):
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


def log(msg):
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
def status():
    """Provides status of the t-tweak service.

    Return Type: str"""
    log("root")

    return JSONResponse(content={"res": "Operational"})


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
    """Provides the total count of text tweaks serviced by t-tweak.

    Return Type: int
    """
    log(f"count all")

    return JSONResponse(content={"res": count()})


@app.get("/history", response_model=ListStringOut)
def get_history():
    """Retrieves the entire history of text tweaks serviced by t-tweak.

    Return Type: str
    """
    log("get_history")

    return JSONResponse(content=history())


@app.get("/length/{text}", response_model=IntOut)
def length(text: str = Path(..., description="Text to be measured", max_length=20)):
    """Calculates the length of a text provided.

    Return Type: int
    """
    log_count_history(l=True, h=True, c=True, msg=f"length {text}", inc=1)

    return JSONResponse(content={"res": len(text)})


@app.get("/reverse/{text}", response_model=StringOut)
def reverse(text: str = Path(..., description="Text to be reversed", max_length=20)):
    """Reverses the text provided.

    Return Type: str
    """
    log_count_history(l=True, h=True, c=True, msg=f"reverse {text}", inc=1)

    return JSONResponse(content={"res": text[::-1]})


@app.get("/upper/{text}", response_model=StringOut)
def upper(
    text: str = Path(..., description="Text to convert to upper case", max_length=20)
):
    """Converts a text to all-uppercase.

    Non-alphabetic characters are left untouched.

    Return Type: str
    """
    log_count_history(l=True, h=True, c=True, msg=f"upper {text}", inc=1)

    return JSONResponse(content={"res": text.upper()})


@app.get("/lower/{text}", response_model=StringOut)
def lower(
    text: str = Path(..., description="Text to convert to lower case", max_length=20)
):
    """Converts a text to all lowercase.

    Non-alphabetic characters are left untouched.

    Return Type: str
    """
    log_count_history(l=True, h=True, c=True, msg=f"lower {text}", inc=1)

    return JSONResponse(content={"res": text.lower()})


@app.get("/mix_case/{text}", response_model=StringOut)
def mix_case(
    text: str = Path(..., description="Text to alternate cases", max_length=20)
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
        description="Larger string to serve as source for the search",
        max_length=20,
    ),
    sub: str = Path(
        ...,
        description="Smaller string to find within the larger string",
        max_length=20,
    ),
):
    """Finds strings inside strings.

    Returns the locations of the substrings within said string (index starts at 0).

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
        409: {"model": Message, "description": "Conflict (incompatible start and end)"}
    },
)
def substring(
    string: str = Path(
        ...,
        description="A string to extract a slice from.",
        max_length=20,
    ),
    start: int = Path(..., description="Where to start the extraction", ge=1, le=20),
    end: int = Path(..., description="Where to end the extraction", ge=1, le=20),
):
    """Extracts a substring from a larger string.

    Returns the resulting string based on the start and end positions (index starts at 0).

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

    # The definition of start/end in the function signature should prevent them from indexing
    #   outside the array. This protection keeps the function robust in different scenarios.
    start = max(start, 1)
    end = max(end, 1)

    return JSONResponse(content={"res": string[start - 1 : end]})


@app.get("/password/{password}", response_model=IntOut)
def password_strength(
    password: str = Path(
        ...,
        description="Your password. *Do not use a real one*, it gets logged and is publicly visible.",
        max_length=20,
    )
):
    """A strength score for passwords between 0 and 10. Is your password strong enough?.

    0 is a weak password, 10 is a strong password.

    Rules:
    * A password should be longer than 12 characters. Score is reduced by the distance from the password length to 12.
    * A password should include at least one upper case letter, one lower case letter, and one number. Score is reduced
    *   by 2 for every infraction.
    * A password shouldn't be the words “password”, "admin" or "root". Violating this rule results in a score of 0.
    * A password shouldn't be the same letter or number repeated for its entire length. This deducts 7 points.

    Return Type: int
    """
    log_count_history(l=True, h=True, c=True, msg=f"password {password}", inc=1)

    score = 10

    # A password should be larger than 12
    if len(password) < 12:
        distance = 12 - len(password)
        score = score - distance

    # A password should NOT be the same letter or number repeated
    if len(set(password)) <= 1:
        score -= 7

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

    return JSONResponse(content={"res": min(max(score, 0), 10)})


@app.get("/counterstring/{cs_length}/{char}", response_model=StringOut)
def counterstring(
    cs_length: int = Path(
        ..., description="Size of the desired counterstring", ge=0, le=150
    ),
    char: str = Path(
        ...,
        description="Character to use as the counterstring measure mark",
        max_length=20,
    ),
):
    """Generates a counterstring, a string that measures itself, and helps you measure software.

    Learn more about counterstrings here: https://www.satisfice.com/blog/archives/22

    Return Type: str
    """
    log_count_history(
        l=True, h=True, c=True, msg=f"counterstring {cs_length} {char}", inc=1
    )

    # Discussion on counterstring algorithms available at https://www.eviltester.com/2018/05/counterstring-algorithms.html
    # This implementation is copied from https://github.com/deefex/pyclip/blob/master/pyclip/counterstring.py
    the_counterstring = ""

    while cs_length > 0:
        next_count = char + str(cs_length)[::-1]
        if len(next_count) > cs_length:
            next_count = next_count[:cs_length]
        the_counterstring = the_counterstring + next_count
        cs_length -= len(next_count)

    the_counterstring = the_counterstring[::-1]

    return JSONResponse(content={"res": the_counterstring})


@app.get("/random", response_model=StringOut)
def rand_str(
    length: int = Query(
        ..., description="Size of the desired random string", ge=0, le=20
    )
):
    """Generates a random string of desired size.

    Return Type: str
    """
    log_count_history(l=False, h=True, c=True, msg=f"random {length}", inc=1)

    random_string = "".join([extra.get_rand_char() for i in range(length)])

    log(f"random {length} {random_string}")

    return JSONResponse(content={"res": random_string})


@app.get("/anagrams/{text}", response_model=ListStringOut)
def anagrams(
    text: str = Path(..., description="Text to find anagrams for. Fun!", max_length=30)
):
    """Finds anagrams for the text provided.

    If more than one anagram is found, all the anagrams are returned within a list.

    Return Type: list[str]
    """
    log_count_history(l=True, h=True, c=True, msg=f"anagrams {text}", inc=1)

    import words

    all_words = words.words.copy()

    text = text.lower()
    text = text.strip()
    text = text.replace(" ", "")
    key = "".join(sorted(text))
    anagrams_found = all_words.get(key, []).copy()

    # A word is always an anagram of itself, so it doesn't count
    if text in anagrams_found:
        anagrams_found.remove(text)

    return JSONResponse(content={"res": anagrams_found})


@app.get(
    "/time",
    responses={203: {"model": Message, "description": "Non Authoritative Information"}},
    response_model=Message,
)
def server_time():
    """Retrieves the server time. For debug purposes (actually, for didactic ones).

    Return Type: str
    """
    log_count_history(l=True, h=True, c=True, msg=f"server_time", inc=1)

    net_time = extra.get_network_time()

    raise HTTPException(
        status_code=http_status.HTTP_203_NON_AUTHORITATIVE_INFORMATION,
        detail=f"{net_time.strftime('%c')}",
    )


@app.get("/reset_server", response_model=StringOut)
def server_reset(
    request: Request,
):
    """Resets the server: reinitializes history and count.

    Return Type: str
    """

    # We reset history and count, but leave the log intact

    with open(count_file, "w") as c:
        fcntl.flock(c, fcntl.LOCK_EX)
        c.write("0\n")
        fcntl.flock(c, fcntl.LOCK_UN)

    with open(hist_file, "w") as h:
        fcntl.flock(h, fcntl.LOCK_EX)
        h.write("")
        fcntl.flock(h, fcntl.LOCK_UN)

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
        self.state = "StandBy"

        machine = self.session.get(ttweak_key)
        if not machine:
            machine = self.session[ttweak_key] = {"state": "StandBy", "strings": []}
        self.machine = machine

    def __str__(self) -> str:
        return f"State: {self.get_state()}, Strings: {', '.join(self.get_strings())}"

    def move_state(self, new_state):
        self.state = new_state
        if "StandBy" == self.state:
            self.clear_strings()
        self.machine["state"] = self.state

    def get_state(self):
        return self.machine["state"]

    def add_string(self, string):
        extra.update_db(self.machine["strings"], string)

    def get_strings(self):
        return extra.read_db(self.machine["strings"])

    def clear_strings(self):
        extra.update_db(self.machine["strings"], None)

    def act(self, command, string="", index=None):
        """
        @startuml
        left to right direction

        StandBy : No strings.
        StandBy : Waiting for commands.
        Input : String reception mode.
        Query : Returns string per index
        Error : Exception state:
        Error : Invalid index.

        [*] --> StandBy
        StandBy --> Input : Command\n"add"
        StandBy --> Input : Command\n"add" + string

        Input --> StandBy : Command\n"stop"
        Input --> Input : Command "add" + string\n&& #strings < 5
        Input --> Input : Command "clear"\n/ Clears strings
        Input --> Query : Command "add" + string\n&& #strings = 5

        Query --> StandBy : Command\n"stop"
        Query --> Input : Command\n"clear"
        Query --> Query : Command "query"\n&& index valid
        Query --> Error : Command "query"\n&& index invalid
        Query --> Error : Command "add"

        Error --> StandBy : Command\n"stop"
        Error --> Input : Command\n"clear"
        Error --> Query : Command\n"sorry"
        @enduml
        """

        current_state = self.get_state()
        if "StandBy" == current_state:
            if "add" == command:
                self.move_state("Input")
                if string:
                    self.add_string(string)
        elif "Input" == current_state:
            if "stop" == command:
                self.move_state("StandBy")
            if "clear" == command:
                self.clear_strings()
            if "add" == command:
                if string:
                    self.add_string(string)
                if len(self.get_strings()) >= 5:
                    self.move_state("Query")
        elif "Query" == current_state:
            if "stop" == command:
                self.move_state("StandBy")
            if "clear" == command:
                self.clear_strings()
                self.move_state("Input")
            if "add" == command:
                self.move_state("Error")
            if "query" == command:
                if index:
                    if type(index) == int or index.isnumeric():
                        index = int(index)
                        if 1 <= index <= (len(self.get_strings())):
                            return self.get_strings()[index - 1]
                    self.move_state("Error")
        elif "Error" == current_state:
            if "stop" == command:
                self.move_state("StandBy")
            if "clear" == command:
                self.clear_strings()
                self.move_state("Input")
            if "sorry" == command:
                self.move_state("Query")

        if "Error" == self.get_state():
            return "Error"
        return "Ok"
        # return self.machine


@app.get("/storage/{command}", response_model=StringOut)
def storage(
    request: Request,
    command: str = Path(
        ..., description="Command for the string storage engine.", max_length=20
    ),
    index: int = None,
    string: str = "",
):
    """Temporary storage for strings. Can store and retrieve up to 5 strings!

    The storage accepts 5 path commands:
    - stop
        - Resets the machine. All strings are deleted.
    - clear
        - Clears strings stored in memory.
    - add
        - Accepts a query parameter "string" for word to add. Words are truncated to 20 chars. Up to 5 words accepted.
    - query
        - Retrieves stored strings. The query parameter "index" determines the string to return (index accepts an int).
    - sorry
        - On errors, restores the ability to query.
    - state
        - Returns information about the state of the storage system

    Examples flow:
    1. http://t-tweak.gershon.info/storage/add
    1. http://t-tweak.gershon.info/storage/add?string=1st_string
    1. ... (more words)
    1. http://t-tweak.gershon.info/storage/add?string=5st_string
    1. http://t-tweak.gershon.info/storage/query?index=0
    1. http://t-tweak.gershon.info/storage/query?index=9
    1. http://t-tweak.gershon.info/storage/sorry
    1. http://t-tweak.gershon.info/storage/query?index=0
    1. http://t-tweak.gershon.info/storage/stop

    Return type: str
    """

    log_count_history(l=True, h=True, c=True, msg=f"storage {command}", inc=1)

    machine = StateMachine(request)

    if "state" == command:
        return JSONResponse(content={"res": str(machine)})

    res = machine.act(command, string=string[:20], index=index)
    return JSONResponse(content={"res": res})


app.add_middleware(SessionMiddleware, secret_key=ttweak_key)
log("T-Tweak Started")


if __name__ == "__main__":
    pass
