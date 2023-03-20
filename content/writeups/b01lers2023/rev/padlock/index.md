---
title: Padlock
date: 2023-03-20
author: VaiTon
---

### Challenge description

> Mindblown by ioccc? How can someone write programs like this... Anyway, try open this padlock :)
>
> Author: bronson113

### Source file

[quine.c](./quine.c)

### First analysis

The source code is a C program that prints itself.
It's a quine, a program that prints its own source code.

If we compile the program and run it, we are welcomed by a

```
zsh: segmentation fault  ./quine
```

Maybe it needs some arguments? Let's try with `./quine 1`:

```
//X
...
```

I won't repeat the program source code here, but keep in mind that when I put ... it means that the source code of the program is repeated.

Let's try with a bigger number, like `./quine 1000`:

```
//XXXX
...
```

So the program does print a variable number of Xs somewhat depending on the argument.
Let's try with `./quine abcd`:

```
//XXXX
...
```

The output is the same, so the number of Xs depends only on the length of the argument.

With the help of a little python, we can find that sometimes, instead of an `X`, the program prints an `O`.
For example, with `./quine b`:

```
// O
```

The first idea was to bruteforce the flag, but as the number of Xs and Os could be > 10, it could take a long time.
So I decided to try to find a pattern in the output.

### Finding the pattern

I wrote a python script that prints the output of the program for strings of N chars made of the same char, for every char.

```
$ ./quine aaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
//XXXXXXXXXXXXXXXXXXOXXXXXXXXXXX
...
```

```
$ ./quine bbbbbbbbbbbbbbbbbbbbbbbbbbbbbb
//OXXXXXXXXXXXXXXXXXXOXXXXXXXXXX
...
```

The pattern starts to emerge. We get an O when the char is the same as the flag char on that position. We get an X when the char is different from the flag char on that position.

### Finding the flag

Now that we know the pattern, we can find the flag. We just need to bruteforce every letter and keep the one in the positions where we get an O.

```python
import subprocess
import string

CHAR_N = 70
flag = [""] * CHAR_N

for ch in string.printable:
    proc = subprocess.Popen(
        ["./quine", ch * CHAR_N], stdin=subprocess.PIPE, stdout=subprocess.PIPE
    )
    (stdout, stderr) = proc.communicate()

    line = stdout.decode().split("\n")[0][2:]
    print(line)

    for i, x in enumerate(line):
        if x == "O":
            flag[i] = ch

flag = "".join(flag)
print(flag)
```

and we get the flag:
`bctf{qu1n3_1s_4ll_ab0ut_r3p371t10n_4nD_m4n1pul4710n_OwO_OuO_UwU}`
