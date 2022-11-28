---
title: IJCTF 2020 - Space!
---

## Description

```
Damn this weird boss. He doesn't let me use keys longer than 2 characters?
How am i supposed to make anything secure with 2 byte keys?
I know i know, i'll just encrypt everything 4 times with different keys, so its 8 characters! Im a genius!

Here is your message: NeNpX4+pu2elWP+R2VK78Dp0gbCZPeROsfsuWY1Knm85/4BPwpBNmClPjc3xA284
And here is your flag: N2YxBndWO0qd8EwVeZYDVNYTaCzcI7jq7Zc3wRzrlyUdBEzbAx997zAOZi/bLinVj3bKfOniRzmjPgLsygzVzA==
```

Author: `Ignis`

In this crypto challenge, we were given a [python script](./spacechallenge.py) containing an AES CBC implementation that used only 2 bytes of security for each key.

The keys were generated in the format:

```
2 random lower/upper case letters or numbers + 14 null bytes
```

For example:

```python
\x34\x67\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00
```

<br>

In the python script, there was the corresponding plaintext of the encrypted message that we were given in the challenge description.

Message:

```python
b"Its dangerous to solve alone, take this" + b"\x00"*9
```

Ciphertext:

```
NeNpX4+pu2elWP+R2VK78Dp0gbCZPeROsfsuWY1Knm85/4BPwpBNmClPjc3xA284
```

## Working

`Message` :arrow_right: AES Encrypt (key1) :arrow_right: AES Encrypt (key2) :arrow_right: AES Encrypt (key3) :arrow_right: AES Encrypt (key4) :arrow_right: `Ciphertext`

## Encryption used

The keys' two random bytes were picked using this alphabet.

```python
>>> alphabet = string.ascii_lowercase + string.ascii_uppercase + string.digits
>>> len(alphabet)
62
```

Bruteforcing a single key meant trying <img src="https://render.githubusercontent.com/render/math?math=\large 62^{2} = 3844"> different combinations.

So normally bruteforcing all the 4 keys would have taken <img src="https://render.githubusercontent.com/render/math?math=\large 3844^{4} = 218340105584896"> tries.

## Solution

Instead of normally bruteforcing the keys we can bruteforce all the first two encryptions combinations and then all the last two decryptions combinations. <br>
By doing this we drastically reduce the computational difficulty of the problem from <img src="https://render.githubusercontent.com/render/math?math=\large 3844^{4}"> to <img src="https://render.githubusercontent.com/render/math?math=\large 3844^{2} * 2 = 29552672"> combinations to try.

After writing this [python script](./expl.py), we generated all the possible keys and calculated all the possible first two encryptions on the plain message:

`Message`:arrow_right: AES Encrypt (key1) :arrow_right: AES Encrypt (key2) :arrow_right: `sometext`

And all the possible last two decryptions on the ciphertext:

`Ciphertext`:arrow_right: AES Decrypt (key4) :arrow_right: AES Decrypt (key3) :arrow_right: `sometext`

After finding a corresponding texts pair, we have successfully found the keys used to encrypt the original message.

After using the 4 recovered keys to decrypt the flag we get:

`ijctf{sp4ce_T1me_Tr4d3off_is_c00l_but_crYpt0_1s_c00l3r_abcdefgh}`

## Participants

| ![image](https://github.com/Bonfee.png?size=200) | <img src="https://github.com/timmykill.png" height=200 width=200> |              |
| ------------------------------------------------ | ----------------------------------------------------------------- | ------------ |
| [@bonfee](https://github.com/Bonfee)             | [@timmykill](https://github.com/timmykill)                        | @Centottanta |
