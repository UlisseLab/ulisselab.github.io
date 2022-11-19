---
title: Swarm Mind
---

> My brother went to NullCon and all I got was this lousy number.
> He was supposed to bring me a picture of the flag. So let me shout out to the Swarm. Maybe they can help.

### The solution

Convert the number to binary, paste it in an editor with line-wrap enabled and play around with the window size until you see the flag show up.

- The first line of thought we followed for solving this challenge was that the number might be the raw binary data of a picture.
- We interpreted the number as raw bytes (we converted it to hex first, then we used [this website](https://tomeko.net/online_tools/hex_to_file.php?lang=en) to get back a file with the raw hex data in it). We analyzed the file using `file` and `binwalk` and we found out that it was of no known file format.
- We then used [CyberChef](https://gchq.github.io/CyberChef/) to check for the file entropy. We noticed that _the entropy was lower than what we would expect from a compressed image (such as a jpg or png image)_. This meant that either the data was of an uncompressed image, or it was something different.
- Here the name of the challenge threw us off: we thought that "swarm" might refer to a swarm of insects/birds in $2D$ / $3D$ space, and we tried interpreting each pair/triple of bytes as $x$, $y$ / $x$, $y$, $z$ coordinates. Sadly, we found out that _the number of bytes was odd and not divisible by three_. We figured out this was a dead end.
- Since the number of bytes was not divisible by three, we assumed that the file did not contain data in `rgb` triples. We then made the assumption that _each byte represented the brightness of a pixel in the final image_.
- From this point on, we went back to working with the number converted in hex form. The reasoning behind this was that if our assumption were correct, we should have been able to see some recognizable patterns in the hex data.
- We pasted the hex number in a text editor with line wraps enabled, and we actually did notice some patterns form:

![](https://wiki.fuo.fi/ctf/nullcon-2022/swarm-mind/img_1.png)

- There was a suspicious amount of `0xff` groups in the hex number, and they appeared to arrange in columns. We played a lot with the window size and aspect ratio, but we couldn't read any clear text, even though we observed some artifacts that looked _very similar_ to actual letters.
- In the end, we thought that maybe the brightness of each pixel was not in the range $[0, 255]$, but rather either $1$ or $0$. We then converted the number to binary, played around with the line length, and we finally got the image we sought:

![](https://wiki.fuo.fi/ctf/nullcon-2022/swarm-mind/img_2.png)

> Also, please note that we used a _vertical, ultrawide 4k monitor_ to display the flag correctly.

Original writeup (https://wiki.fuo.fi/en/CTFs/nullcon-2022/Swarm-mind).
