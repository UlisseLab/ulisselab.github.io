---
title: Genetic Mutation
author: ossigeno
---

### Files

- [change_perms.c](./change_perms.c)
- [4bytes.py](./4bytes.py)

### Challenge

We have to change 4 bytes and we can give our name as input, so we can put something on the stack of the length that we want.
Of course we want to put a shellcode on the stack, and use the 4 bytes to jump on it.

The first problem is that NX was enabled, so we have to use 1 byte to disable it in the header.
To be honest I didn't know how to do it, well, I knew how to change it, but I didn't know of any software that could give me the address. So i asked one of my teammate, and he game the C script file in this directory. I could use a diff between a modified elf and the starting one, but hey, I ain't the smartest one.

After that i just used 2 bytes to jump on the shellcode: the string is loaded naturally into RDX, at main+113.
So is enought to select an address after that point, but the string still has to be in that register, use 1 byte to modify one opcode to 'push rdx' and another byte to create the 'ret' opcode, so we can jump on our shellcode and have a shell!

![](bytes.png)
