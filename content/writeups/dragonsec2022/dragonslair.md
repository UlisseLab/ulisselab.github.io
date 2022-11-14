---
title: Dragon's Lair
author: Fuo
ShowToc: true
---

In this challenge we were given a python jail (with source code) where all `__builtins__` were removed apart from print, exec, int, type, *insert missing* and the code was executed in an `exec` with a modified context.

There was also a filter on `'`, `"`, `+` and all `__xxx__` apart from `__closure__`,`__code__`,`__doc__` and *insert missing*

In order to create strings we abused already existing strings taken from the `__doc__` of accessibile builtins such as `int.to_bytes.__doc__` in order to create needed strings. Since we did not have access to `+` we used casting from `int` to `bytes` and then calling the `decode()` method in order to create strings.

We also abused the `__closure__` function call by forcing a custom `context` with the `PERCEPTION_CHECK` and `DRAGON_IQ` variables set in order for the checks in the code to pass, we then called the function (see the solution below for better understanding of how it was done)


# Solution:

```python
big = int.to_bytes.__doc__[275:278]
PERCEPTION_CHECK=int(106698176633358138605712019737935168331).to_bytes(16, big).decode()
DRAGON_IQ = int(1260305694002788649297).to_bytes(9, big).decode()
FLAG = int(1179402567).to_bytes(9, big).decode()
ctx = {PERCEPTION_CHECK:200, DRAGON_IQ:0}
print(explore.__closure__)
c = explore.__closure__
b =(c[0],c[1],c[2],c[0],c[1])(type(explore)(explore.__code__.co_consts[4], ctx, None, None, b))()
explore()
```