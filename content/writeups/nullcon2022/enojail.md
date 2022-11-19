---
title: ENOJAIL
---

> We launched a new service today. It's called ENOJAIL™ and gives the user access to an unlimited IPython shell. Sadly, management decided we need to leave our valuable `flag.txt` on the server, so naturally, engineering had to lock it back down a bit. But we are sure you will still enjoy all of the possibilities, such as.. Calculating 5/5 fully interactively, evaluating '1', and so much more!

### What's going on?

It's all about a broken iPython Shell. We observed that some characters were not allowed.
So we tried to print'em all, and got the whitelisted characters:

```
0123456789abcdefghijklmABCDEFGHIJKLMNOP&'-./:;<=@_``
```

We also tried some bash commands, and we saw some of them worked (`cd`, `ll`).
`ll` showed us 2 files, `flag.txt` and `enojail.py`.
However, commands with blacklisted characters couldn't be valid.

### The solution

For this reason, we thought about commands with only allowed characters and we found out `head`, `diff` were perfect for printing the flag. Nonetheless, commands like `head` and `diff` didn't work alone. After a few attempts, we observed `ll;` was perfect for command injection:

```bash
`ll; head `diff ./ ../` -c 100000000000`
```

- `ll` is important, we can use it for command injection e.g. `head`
- `head -c 100000000000` shows the first 100000000000 bytes
- `diff` shows the differences between the current directory and the parent dir.
- `` head `diff ./ ../` -c 100000000000 `` shows the first 100000000000 byte difference between the parent dir and the current dir, exposing `flag.txt` from the current dir.

Voilà, the flag.

### An interesting script

_We love this pyfuck variant_, so here's the `enojail.py` source code leaked from the challenge.

```python
#!/usr/bin/env python3
"""
ENOJAIL
"""
import re, sys, signal, datetime
from subprocess import Popen, PIPE
from functools import partial
from socketserver import ForkingTCPServer, BaseRequestHandler

PORT = 5656
REGEX = r"p*[^ &\--=@-P'_-m]*,*"

class RequestHandler(BaseRequestHandler):
    def handle(self):
        print(
            "{}: session for {} started".format(
                datetime.datetime.now(), self.client_address[0]
            )
        )
        fd = self.request.makefile("rwb", buffering=0)
        main(fd, fd, bytes=True)


def main(f_in=sys.stdin, f_out=sys.stdout, bytes=False):
    def enc(str):
        if bytes:
            return str.encode()
        return str

    def decode(b):
        if bytes:
            return b.decode()
        return b

    def alarm_handler(signum, frame):
        f_out.write(enc("\nThank you for your visit.\nPlease come back soon. :)\n"))
        print("{}: Another timeout reached.".format(datetime.datetime.now()))
        sys.exit(15)

    if "debug" not in sys.argv:
        signal.signal(signal.SIGALRM, alarm_handler)
        signal.alarm(15)

    f_out_no = f_out.fileno()

    r = REGEX
    cat_food = partial(re.compile(r).sub, "")
    proc = Popen(
        ["python3", "-u", "-m", "IPython", "--HistoryManager.enabled=False"],
        stdin=PIPE,
        stdout=f_out_no,
        stderr=f_out_no,
    )
    si = proc.stdin

    f_out.write(
        f"""Welcome to the ENOJAIL™ interactive IPython experience!
You can IPython all you want.
Just please don't look at ./flag.txt, thanks!

Oh, actually, we will filter out some characters before we eval them, just to be on the safe side.
Get started by tying '1' or 1 / 1.

Enjoy your stay! :)\n\n""".encode()
    )

    while True:
        userinput = cat_food(decode(f_in.readline())).strip()
        # forward "sanitized" input to IPython
        si.write("{}\n".format(userinput).encode())
        si.flush()


if __name__ == "__main__":
    print("Listening on port {}".format(PORT))
    ForkingTCPServer(("0.0.0.0", PORT), RequestHandler).serve_forever()

```

Original writeup (https://wiki.fuo.fi/en/CTFs/nullcon-2022/ENOJAIL).
