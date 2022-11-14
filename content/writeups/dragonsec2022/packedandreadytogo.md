---
title: Packed and ready to go
author: Fuo
---

The writeup will be relatively short as the challenge was quite easy to solve!

### Files
[ready.exe](https://wiki-ulisse.fuo.fi/ctf/dragonsec-2022/packed-and-ready-to-go/ready.exe)

### Solution:

Analyzing the binary with [DIE](https://github.com/horsicq/DIE-engine) yielded a UPX 3.96 packed binary. 
![photo_2022-04-16_20-19-21.jpg](https://wiki-ulisse.fuo.fi/ctf/dragonsec-2022/packed-and-ready-to-go/photo_2022-04-16_20-19-21.jpg)


So the first thing I did was `upx -d ready.exe`, which *would have been correct* if it weren't for the author confirming it themselves that the unpacking broke the binary (I discovered this only after the CTF ended)
During the CTF I noticed that the binary broke, and I did not trust the static analysis of it apart from some more info on symbols, albeit being broken.

I had no other choice to stuck with running the _packed_ binary, which was a pain in the butt since I had no helpful script as the UPX version used was literally the latest one available at the time of writing this :(

I stuck with x64dbg instead of ida since ida's debugger did not like imports changing at runtime (it did not detect them at all by default and I did not want to search for a fix for that as x64dgb worked well enough)

I noticed that the binary complained about a missing `DCTF.dll` when run. I supposed this was just to annoy me so I copied the `ready.exe` binary and renamed to `DCTF.dll` hoping there were no particular checks if it were actually a valid dll (and I was right)

Passed that and running it again, the program wrote on the console that I "was close" and then stopped itself. Obviously the first thing I did was to put a breakpoint in the `wsprintfw` symbol, which is the "print" function used in order to check what was actually making it print that (and eventually reverse it why if it were an if clause)

![photo_2022-04-16_20-15-53.jpg](https://wiki-ulisse.fuo.fi/ctf/dragonsec-2022/packed-and-ready-to-go/photo_2022-04-16_20-15-53.jpg)

Ironically that was enough to solve the challenge as the flag was unpacked from the program itself and put in the memory at that breakpoint time :D (I confirmed with the author that is indeed the intended solution, but statically reversing it was also possibile since the non-null values were just XORred with a key)

![photo_2022-04-16_20-15-24.jpg](https://wiki-ulisse.fuo.fi/ctf/dragonsec-2022/packed-and-ready-to-go/photo_2022-04-16_20-15-24.jpg)