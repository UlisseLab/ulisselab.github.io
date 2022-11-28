#!/usr/bin/env python3
import Crypto
from Crypto.PublicKey import RSA
import sys
from pwn import *



def h2i(h):
	try:
		return int(h,16)
	except Exception:
	#	print("Couldn't hex decode",flush=True)
		sys.exit()





r = remote("3.93.128.89",1219)
r.recvuntil("-----BEGIN PUBLIC KEY-----")
raw_key = b"-----BEGIN PUBLIC KEY-----" + r.recvuntil("-----END PUBLIC KEY-----")
pubkey = RSA.importKey(raw_key)
#this code is bad, but works, so is good for me
start="aa"
s=h2i(start)
#must run on python3, python2 doesn't like it and I don't know why
#if your pwntools don't works on py3, just copy paste the message and the sign, it works
m=hex(pubkey.encrypt(s,123)[0])
r.sendline(m)
r.sendline(s)
print(m)
start="ab"
s=h2i(start)
m=hex(pubkey.encrypt(s,123)[0])
r.sendline(m)
r.sendline(s)

print(m)


start="ac"
s=h2i(start)
m=hex(pubkey.encrypt(s,123)[0])
r.sendline(m)
r.sendline(s)
print(m)


r.interactive()

