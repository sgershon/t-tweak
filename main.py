import fcntl
import datetime

from fastapi import FastAPI, Path
from fastapi.responses import Response, JSONResponse, FileResponse


def count(increment=None):
    with open("count.cnt", "r") as c:
        cnt = int(c.read())
    if type(increment) is int:
        with open("count.cnt", "w+") as c:
            fcntl.flock(c, fcntl.LOCK_EX)
            c.write(str(cnt + 1))
            fcntl.flock(c, fcntl.LOCK_UN)
    return cnt


def history(new_string=None):
    with open("history.txt", "r") as h:
        hist = h.readlines()
    if new_string:
        hist.append(f"{new_string}\n")
        with open("history.txt", "w") as h:
            fcntl.flock(h, fcntl.LOCK_EX)
            h.writelines(hist[-50:])
            fcntl.flock(h, fcntl.LOCK_UN)

    return hist


def log(msg):
    with open("log.log", "a") as l:
        l.write(f"{datetime.datetime.now().strftime('%c')} {str(msg)}\n")


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


log("Starting T-Tweak")


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
)

log("T-Tweak Started")


@app.get("/")
def root():
    """Provides status of the t-tweak service.

    Return Type: str"""
    log("root")

    return JSONResponse(content={"Status": "Operational"})


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


@app.get("/count/all")
def count_all():
    """Provides the total count of text tweaks serviced by t-tweak.

    Return Type: int
    """
    log(f"count all")

    return JSONResponse(content={"res": count()})


@app.get("/history")
def get_history():
    """Retrieves the entire history of text tweaks serviced by t-tweak.

    Return Type: str
    """
    log("get_history")
    return JSONResponse(content=history())


@app.get("/length/{text}")
def length(text: str = Path(..., description="Text to be measured", max_length=100)):
    """Calculates the length of a text provided.

    Return Type: int
    """
    log_count_history(l=True, h=True, c=True, msg=f"length {text}", inc=1)

    return JSONResponse(content={"res": str(len(text))})


@app.get("/reverse/{text}")
def reverse(text: str = Path(..., description="Text to be reversed", max_length=100)):
    """Reverses the text provided.

    Return Type: str
    """
    log_count_history(l=True, h=True, c=True, msg=f"reverse {text}", inc=1)

    return JSONResponse(content={"res": text[::-1]})


@app.get("/upper/{text}")
def upper(
    text: str = Path(..., description="Text to convert to upper case", max_length=100)
):
    """Converts a text to all-uppercase.

    Non-alphabetic characters are left untouched.

    Return Type: str
    """
    log_count_history(l=True, h=True, c=True, msg=f"upper {text}", inc=1)

    return JSONResponse(content={"res": text.upper()})


@app.get("/lower/{text}")
def lower(
    text: str = Path(..., description="Text to convert to lower case", max_length=100)
):
    """Converts a text to all lowercase.

    Non-alphabetic characters are left untouched.

    Return Type: str
    """
    log_count_history(l=True, h=True, c=True, msg=f"lower {text}", inc=1)

    return JSONResponse(content={"res": text.lower()})


@app.get("/mix_case/{text}")
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


@app.get("/finds/{string}/{sub}")
def find(
    string: str = Path(
        ...,
        description="Larger string to serve as source for the search",
        max_length=100,
    ),
    sub: str = Path(..., description="Smaller string to find within the larger string"),
    max_length=100,
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


@app.get("/password/{password}")
def password_strength(
    password: str = Path(
        ...,
        description="Your password. *Do not use a real one*, it gets logged and is publicly visible.",
        max_length=100,
    )
):
    """A strenght score for passwords between 0 and 10. Is your password strong enough?.

    0 is a weak password, 10 is a strong password.

    Rules:
    * A password should be longer than 12 characters. Score is reduced by the distance from the actual length and 12.
    * A password should include at least one upper case letter, one lower case letter, and one number. Score is reduced by 2 for every infraction.
    * A password shouldn't contain any consecutive letters or numbers. 1 is deducted from score for every infraction.
    * A password shouldn't be the words “password”, "admin" or "root". Violating this rule results in a score of 0.
    * A password shouldn't be the same letter or number repeated for its entire length. This deducts 7 points.

    Return Type: int
    """
    log_count_history(l=False, h=True, c=True, msg=f"password {password}", inc=1)

    score = 10

    # A password should be larger than 12
    score = len(password) - 2

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

    # A password shouldn’t be the words “password”, "admin" or "root"
    if password in ["password", "admin", "root"]:
        score = 0

    # A password shouldn’t be the same letter or number repeated
    if len(set(password)) <= 1:
        score -= 7

    log(f"password {password} {score}")

    return JSONResponse(content={"res": min(max(score, 0), 10)})


@app.get("/counterstring/{length}/{char}")
def counterstring(
    length: int = Path(
        ..., description="Size of the desired counterstring", gt=0, le=150
    ),
    char: str = Path(
        ...,
        description="Character to use as the counterstring measure mark",
        max_length=100,
    ),
):
    """Generates a counterstring, a string that measures itself, and helps you measure software.

    Learn more about counterstrings here: https://www.satisfice.com/blog/archives/22

    Return Type: str
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


@app.get("/anagrams/{text}")
def anagrams(
    text: str = Path(..., description="Text to find anagrams for. Fun!", max_length=100)
):
    """Finds anagrams for the text provided.

    If more than one anagram is found, all of the anagrams are returned within a list.

    Return Type: Union[list[str], str, NoneType]
    """
    log_count_history(l=True, h=True, c=True, msg=f"anagrams {text}", inc=1)

    import words

    all_words = words.words.copy()

    key = "".join(sorted(text))
    anagrams = all_words.get(key, [None]).copy()

    if text in anagrams:
        anagrams.remove(text)

    # Extract element if list contains only it, None if list is empty, list otherwise
    res = anagrams if len(anagrams) > 1 else None if len(anagrams) == 0 else anagrams[0]

    return JSONResponse(content={"res": res})


# @app.get("/count/mine")
# def count_mine(session_count: Union[str, None] = Cookie(default=0)):
#     response = Response()
#     response.set_cookie(key="localcount", value=f"{int(session_count) + 1}")
#     return {"res": str(session_count)}


if __name__ == "__main__":
    pass
