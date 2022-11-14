---
title: Euler's License
author: VaiTon
tags: [forensics, powershell, python, pe]
ShowToc: true
date: 2022-04-18
---

> Someone who doesn't care about bandwidth usage decided to package both the server and client binaries in a single file... The server of course is meant to run on linux, and the client on Windows.

We get a PowerShell file [`eulers_license.ps1`](/eulers_license.ps1) that contains:

- a `binary_linux` var containing the server code encoded in base64.
- a `binary_win` var containing the client code also encoded in base64.

## The linux binary

The linux binary is very easy to reverse. In fact by decoding it we get a python server which has a huge SQLi vuln:

```python
lice = request.args.get("license_key")
query = "SELECT * FROM license_keys WHERE license_key = '" + lice + "';"
```

we can proceed with a basic SQLi like `' OR 1=1 -- ` and get the first part of the flag (which is the second one really):

> `_python_is_easy_to_reverse}`

## The windows binary

The windows exe is a little bit harder to reverse. By looking at it with ghidra we understand that it must be:

- a 10 digits number
- a prime number
- it has something to do with Euler

By a combination of chance and testing we come across the number [`2147483647`](https://en.wikipedia.org/wiki/2,147,483,647) which is a prime number discovered by Euler.

Providing this input to the client gives us the output:

```
Enter eulers license key: 2147483647
dctf{2147483647
Failed to contact euler.dragonsec.si for license confirmation...
```

> `dctf{2147483647_python_is_easy_to_reverse}`
