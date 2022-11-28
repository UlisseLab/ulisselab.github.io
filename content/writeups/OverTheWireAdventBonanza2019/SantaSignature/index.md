---
title: Santa's Signature
tags:
  - crypto
---

The challenge use a classic RSA sign and verify, without anything strange.

So, differently from the others, I abused the fact that we can give both the Sign and the plaintext as inputs.
Is enought to switch S with M when given as input, where S is calculated encrypting M with the public key that is given.
Since

```python
verify(m,s):
	return m==encrypt(s,publickey)
```

If we give

```python
verify(encrypt("AAAA",publicKey),"AAAA") # encrypt("AAAA",publickey)==encrypt("AAAA",publickey)
```

we will pass the test.
We just have to do this for 3 times!
![](./santa.png)

After reading the explanation by the OverTheWire team, I don't think this was intended, but hey, a flag is a flag.
