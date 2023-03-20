---
title: chicago
author: VaiTon
date: 2023-03-20
tags: [rust, keygen]
---

### Challenge description

> Keygenme...sort of
>
> Author: `akhbaar`

### The keygen

As usual, we start by trying to run the executable.

```shell
./chicago
```

but unfortunately, we get

```shell
... Bad lenght! ...
```

Opening the file with ghidra, we see that the file is a rust compiled executable, with **A TON** of functions (I suppose from the rust standard library). After some time we find the `main`, with an interesting portion of code:

```c
if (local_1a8 < 10) {
    FUN_00107480("Bad length ...
```

So the length of the input must be at least 10.
Also, after some analysis and variable renaming, we find that

```c
actual_num = input[i] - 0x30; // 0x30 is the ascii code for '0'
```

So every character of the input must be a digit.

```c
if (((i & 1) != 0) && (actual_num = actual_num * 2, L'4' < (uint)input[i])) {
    actual_num = (uint)(byte)((char)(actual_num & 0xff) + (char)((actual_num & 0xff) / 10) * -9);
}
```

So if the index of the character is odd, we multiply it by 2.
Also, if the original number is greater than 4, we replace it with $x + x / 10 * -9$, where $x$ is the original number.

Then, at least that's what I thought, it gets compared to the first character of the input, and if it's equal we get the flag.

### The real keygen

After spending much more time than I should have, and after writing a python script to bruteforce the flag, I was so surprised when the first number it tried checked all the conditions.

As you could have guessed, the first and most obvious string that my script tried was `0000000000`, and it worked 😭.

To get the flag, I then just had to run the program with `./chicago 0000000000`.
