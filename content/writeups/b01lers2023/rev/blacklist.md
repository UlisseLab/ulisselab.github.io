---
title: Blacklist
author: Lombax
description: "Writeup of the Blacklist challenge from B01lers CTF 2023"
date: "2023-03-20"
tags: ["misc", "python"]
---

#### Challenge description

> you can run anything on this! please dont hack me

#### Source code

```python
blacklist = "._0x/|?*[]{}<>\"'=()\\\t "
blacklist2 = ['eval', 'exec', 'compile', 'import', 'os', 'sys', 'cat', 'ls', 'exit', 'list', 'max', 'min', 'set', 'tuple']

def validate(code):
    for char in blacklist:
        if char in str(code):
            return False
    for word in blacklist2:
        if word in str(code):
            return False
    return True

if __name__ == '__main__':
    print("------------------------------")
    print("Welcome to my very cool python interpreter! \nI hope I blacklisted enough... \nYou can never be too careful with these things...")
    print("Send an empty line to run!")
    print("------------------------------")
    safe_code = ""
    while (True):
        unsafe_code = input(">>> ")
        if (unsafe_code == ""):
            try:
                exec(safe_code)
            except:
                print("Error executing!")
            break
        unsafe_code = unsafe_code.replace("open", "")
        unsafe_code = unsafe_code.replace("print", "")
        if (not validate(unsafe_code)):
            print("Invalid code!")
            continue
        safe_code += str(unsafe_code)+ "\n"
```

#### First analysis

In this challenge we had to read the `flag.txt` file. The script let us upload python code trough the while loop, blacklisting a number of characters. Most notably:

- dots and underscore (so no \_\_builtins\_\_)
- any kind of parenthesis (so no functions, at least in the canonical sense, see later...)
- and no space (wtf man, even the spaces?)

Note that `open` and `print` are not blacklisted, they just get replaced with an empty string.

#### Resolution

First rule don't panic, what can we use? `open` and `print` can actually be used, we just need to send something like `oopenpen` that get sanitized to `open` so that's good, but how do we call a function without parenthesis?
Let's introduce python decorators!

```python
@print
@input
class A:pass
```

We create a class that does nothing and invoke the function input with the class name as parameter and then the function print on the result of input.
This is the same as running

```python
print(input(...))
```

We don't care about the argument of the `input`, as it gets stringified and then used as the string printed before the prompt.

Since `@` are not blacklisted we are golden. What we can do then is something similar to:

```python
@pprintrint
@sorted
@oopenpen
@input
class A:pass
```

and give as input: `flag.txt` to print it.
`@sorted` is necessary because open returns a file object and not the file content itself, other alternatives would have been **list, next** or similar.

But we need **the space** between `class` and `A` and there is nothing much we can do about it.
We need to input a separator that is ignored by the blacklist. We have 2 options:

- we encode the payload so that there aren't blacklisted chars included the space
- we use a different separator that doesn't make our payload explode within the exec

Since exec doesn't seem to respect different encoding even when the \#coding:blabla header is defined we went for the second options.
After many test the only character we found was **Form feed** (ASCII `0x0c`)

#### Final Payload

```python
@pprintrint
@sorted
@oopenpen
@input
class<\x0c>A:pass
```

We then proceed to use `pwntools` to send the payload in bytes (so that we can handle for the the special character correctly) and it's done!
