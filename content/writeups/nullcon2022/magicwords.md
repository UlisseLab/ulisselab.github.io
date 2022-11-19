---
title: Magic Words
---

> Give me a sign for the magic words and the flag is yours.

### What's going on?

This service is using [gmp](https://gmplib.org/), a library for arbitrary precision arithmetic in C.

A brief code explanation:

1. The _target_ string is created by appending _magic words_ in a random order.
2. We're told that string and asked for its signature.
3. A simple modular exponentiation is performed ($m \equiv sig^3 \pmod n$)
4. _m_ is converted to a string and compared against our previous _target_ string using strcmp. If 0 is returned we get the flag.

Aside from the main, there's just a single function that converts an integer to a string (a sequence of bytes to be honest).
If you're familiar with PyCyptodome, it works like [Crypto.Util.number.long_to_bytes](https://pycryptodome.readthedocs.io/en/latest/src/util/util.html#Crypto.Util.number.long_to_bytes).

```c
char* int_to_str(mpz_t n) {
	int len = (int)mpz_sizeinbase(n, 256);
	char* res = malloc(len + 1);
	mpz_export(res, NULL, 1, 1, 0, 0, n);
	return res;
}
```

In plain python it would be something along the lines of

```python
def int_to_str(n: int) -> str:
	s = ''
	while n > 0:
		s = chr(n & 0xFF) + s
		n = n >> 8
	return s
```

### The solution

Obviously the first idea that came to my mind was to find a number _sig_ such that $sig^3 \pmod{n} \equiv$ `str_to_int(target)`, but I'm not a math guy, so I don't know if there's an algorithm for the modular cube root or something + if there is one I guess it would be computationally hard.

Then I noticed that _n_ was really big (4096 bits), especially when compared to the _target_ (whose max size could be 96 bytes so 768 bits). If the _target_ happened to be a perfect cube, I could've just computed it's _normal_ cube root but there were $12^{12}$ possible combinations and in my tests it never happened.

Then I found out that `strcmp("owo\0asd", "owo")` returns 0 (which really makes sense...) which made me think that I could try finding a perfect cube whose string representation was in the form `target + \0 + random bytes`.

This is the script I came up with:

```python
from Crypto.Util.number import long_to_bytes, bytes_to_long
from sage.all_cmdline import *

target = b'ham wuap pteng holy ham spam mene ene ene pteng egg moo egg -- give me the flag!'
target += b'\x00'

for i in range(200):
    near_perfect_cube = bytes_to_long(target + b'\x00'*i)
    root = RealNumber(near_perfect_cube).nth_root(3).round()
    perfect_cube = pow(root, 3)
    if long_to_bytes(perfect_cube).startswith(target):
        print(root)
        break

```

I'm essentially trying to "handcraft" a large enough number (whose associated string starts with `target + \0`) so that a _small_ change in it's least significant bits (the cube root -> rounding -> cube process) only affects the string to the right of the null byte.

Original writeup (https://wiki.fuo.fi/en/CTFs/nullcon-2022/magic-words).
