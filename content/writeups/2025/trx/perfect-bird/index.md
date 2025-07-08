+++
title  = "Perfect Bird"
author = "VaiTon"
date   = "2025-02-22"
tags   = ["GulfOfMexico", "DreamBerd", "language"]

[cover]
image = "cover.jpg"
caption = "[Asian pied starlings (Gracupica contra)](https://commons.wikimedia.org/wiki/File:Asian_pied_starlings_(Gracupica_contra).jpg) - CC-BY-SA 4.0"
+++

## Challenge description

As a _bird_ soaring through the sky, you seek the _perfect language_, and then... you find this

### Files

- [chall.db3](chall.db3)

## Writeup

Opening the `chall.db3` file, I come across a weird programming language that looks kind of like JavaScript. The code is full of strange symbols and conventions, and without a guide, it’s pretty hard to figure out what it does.

My go-to move is always to check the challenge description for hints. Here, the words _bird_ and _perfect language_ are italicized, which seems important. So, I search for "bird perfect language programming" online.

The first result is [a video by the streamer ThePrimeTime][video], where he talks about this exact programming language.

[video]: https://www.youtube.com/watch?v=tDexugp8EmM

![A Google search for "bird perfect language programming"](search.png)

From the video's description, I find my way back to the GitHub repository that explains this language: <https://github.com/TodePond/GulfOfMexico>.

It looks like it was originally called "DreamBerd," but now it goes by "GulfOfMexico."

## DreamBerd - A Perfect Language

> Be bold! End every statement with an exclamation mark!
>
> ```js
> print("Hello world")!
> ```

I start thinking about ways to decipher the code and come up with the idea of writing a script to rewrite it into an existing language (one with an existing interpreter!).

At first, I consider converting it to Python, but then I realize JavaScript would be a better choice since it’s closer to the original language.

So, I write a Python script to convert the code to JavaScript and run it to see the output.

### Converting DreamBerd to JavaScript

The key here is that we don’t need a _perfect_ (pun intended) conversion—just something accurate enough to run the challenge code.
It doesn’t have to handle every possible DreamBerd program, just this one.

The first thing we need to do is to fix the lifetimes in the code.

> Gulf of Mexico has a built-in garbage collector that will automatically clean
> up unused variables. However, if you want to be extra careful, you can specify a
> lifetime for a variable, with a variety of units.

In particular, the one bit we cannot tollerate are negative lifetimes:

> Variable hoisting can be achieved with this neat trick. Specify a negative
> lifetime to make a variable exist before its creation, and disappear after its
> creation.
>
> ```js
> print(name)! //Luke
> const const name<-1> = "Luke"!
> ```

```python
#!/bin/env python3
import sys
import re

def fix_lifetimes(lines):
    new_lines = []

    for i, line in enumerate(lines):
        match = re.match(r".+<(.+)>.+", line)
        if not match:
            new_lines.append(line)
            continue

        lifetime = match.group(1)

        if lifetime == "Infinity":
            new_lines.append(line)
            continue

        lifetime = int(lifetime)

        if lifetime >= 0:
            line = line.replace(f"<{lifetime}>", "")
            new_lines.append(line)
            continue

        new_pos = max(len(new_lines) + lifetime, 0)

        # remove the invalid lifetime
        line = line.replace(f"<{lifetime}>", "")
        new_lines.insert(new_pos, line)

        print(f"Moved line {i + 1} -> {new_pos + 1}", file=sys.stderr)

    return new_lines

lines = sys.stdin.readlines()
program = fix_lifetimes(lines)
program = "".join(program)

```

Then we need to replace each "strange lang" construct with the corresponding JavaScript construct.

- `!` -> nothing

  ```python
  program = re.sub(r"!+", "", program)
  ```

- `;` -> `!`

  ```python
  for i in range(1, 100):
      program = re.sub(r";([\w|!|(|)]+)", r"!(\1)", program)
  ```

- Every kind of variable declaration is replaced with `let`.

  ```python
  program = program.replace("const const const", "let")
  program = program.replace("const const", "let")
  program = program.replace("const var", "let")
  program = program.replace("var var", "let")
  ```

- The variable `42` (which is an invalid identifier in JavaScript) is replaced with `var_42`.

  ```python
  program = re.sub(r"let (\d+)", r"let var_\1", program)
  ```

- Every usage of `42` is replaced with `var_42`.

  ```python
  program = program.replace("42 +=", "var*42 +=")
  program = program.replace("42 -=", "var_42 -=")
  program = program.replace("42 *=", "var*42 *=")
  program = program.replace("42 ^ ", "var*42 ^ ")
  program = program.replace("42 = ", "var_42 = ")
  program = program.replace("42 * ", "var*42 * ")
  program = program.replace("42 / ", "var_42 / ")
  program = program.replace("42 % ", "var_42 % ")
  program = program.replace("42 + ", "var_42 + ")
  program = program.replace("42 - ", "var_42 - ")
  program = program.replace("!42", "!var_42")
  ```

- Remove `Infinity` lifetimes.

  ```python
  program = re.sub("<Infinity>", "", program)
  ```

- Replace `functi` with `function`.

  ```python
  program = re.sub(r"functi (.+?) \(\) =>", r"function \1()", program)
  ```

- Replace `print` with `console.log`.

  ```python
  program = re.sub(r"print", "console.log", program)
  ```

- Fix array starting convention, as in DreamBerd arrays start at -1 (oh, the horror).

  ```python
  # arrays start at -1 ...
  program = re.sub(r"(\w+)\[(.+)\]", r"\1[\2 + 1]", program)
  ```

Finally, we print the program.

```python
print(program)
```

Then we use the script to convert the code to JavaScript.

```shell
cat chall.db3 | python3 invertlines.py > chall_ok.js
```

And we then run the code with Node.js.

```shell
$ node chall_ok.js
[
    84, 82, 88, 123, 116, 72, 105, 53, 95,
    73, 53, 95, 116, 104, 51, 95, 80, 51,
    114, 102, 51, 99, 116, 95, 108, 52, 110,
    71, 85, 52, 103, 51, 33, 33, 33, 33,
    33, 33, 125
]

```

The result we get is an array of integers.
We can convert it to ASCII to get the flag.

```python
#!/bin/env python3
m=[
   84,  82,  88, 123, 116, 72, 105, 53,  95,
   73,  53,  95, 116, 104, 51,  95, 80,  51,
  114, 102,  51,  99, 116, 95, 108, 52, 110,
   71,  85,  52, 103,  51, 33,  33, 33,  33,
   33,  33, 125
]

for i in range(0, len(m)):
    print(chr(m[i]), end="")
```

```shell
$ python3 decode.py
TRX{tHi5_I5_th3_P3rf3ct_l4nGU4g3!!!!!!}
```

Full script: [perfect_bird.py](perfect_bird.py)
