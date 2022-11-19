---
title: Texnology
---

> Online LaTeX editors are quite famous now, but are the associated risks as well?
> Hint: The flag is at `/FLAG.`

### What's going on?

We have this website, which compiles LaTeX code from the text area and executes it on a remote server. If the syntax is valid, a link with the compiled PDF appears on the website.

### The solution

We googled _LaTeX command injection_ and we found out [this interesting website](https://0day.work/hacking-with-latex/), which shows some ways to do command injection. We also discovered LaTeX is a Turing complete programming language and it allows us to perform operations, e.g. File I/O. Some operations were blacklisted (e.g. `\immediate`), but we tried other operations, like this one, which worked:

```tex
\newread\file
\openin\file=/FLAG
\read\file to\line
\text{\line}
\closein\file
```

Original writeup (https://wiki.fuo.fi/en/CTFs/nullcon-2022/Texnology).
