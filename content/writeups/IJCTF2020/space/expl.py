#!/usr/bin/python3

from hashlib import md5
from base64 import b64decode
from base64 import b64encode
from Crypto.Cipher import AES
import string

alphabet = string.ascii_lowercase + string.ascii_uppercase + string.digits
iv = md5(b"ignis").digest()

message = b"Its dangerous to solve alone, take this" + b"\x00"*9
message_enc = b64decode(b"NeNpX4+pu2elWP+R2VK78Dp0gbCZPeROsfsuWY1Knm85/4BPwpBNmClPjc3xA284")

flag = b64decode(b"N2YxBndWO0qd8EwVeZYDVNYTaCzcI7jq7Zc3wRzrlyUdBEzbAx997zAOZi/bLinVj3bKfOniRzmjPgLsygzVzA==")

# Arrays to store encrypted/decrypted texts - keys
encryptions_key = []
decryptions_key = []

# Arrays to store encrypted and decrypted texts
encryptions = []
decryptions = []

# Generate all keys combinations
keys = []
for c1 in alphabet:
	for c2 in alphabet:
		keys.append((c1+c2).encode() + b'\x00'*14)

# Bruteforce first 2 encrypts
i = 0
for key1 in keys:
	for key2 in keys:
		cipher1 = AES.new(key1, AES.MODE_CBC, IV=iv)
		cipher2 = AES.new(key2, AES.MODE_CBC, IV=iv)
		encrypted = cipher2.encrypt( cipher1.encrypt(message) )
		encryptions.append( encrypted )
		encryptions_key.append([encrypted, key1, key2])
	i+=1
	print(str(i*100/3844) + '%')

# Bruteforce last 2 decrypts
i = 0
for key4 in keys:
	for key3 in keys:
		cipher4 = AES.new(key4, AES.MODE_CBC, IV=iv)
		cipher3 = AES.new(key3, AES.MODE_CBC, IV=iv)
		decrypted = cipher3.decrypt( cipher4.decrypt(message_enc) )
		decryptions.append( decrypted )
		decryptions_key.append([decrypted, key3, key4])
	i+=1
	print(str(i*100/3844) + '%')

# Find the double encrypted message that matches with double decrypted ciphertext
inters = list(set(encryptions).intersection(decryptions))

# Retrieve the keys corresponding to the encrypt - decrypt match
keys_found = []

for l in encryptions_key:
        if l[0] == inters[0]:
                keys_found.append(l[1])
                keys_found.append(l[2])

for l in decryptions_key:
	if l[0] == inters[0]:
		keys_found.append(l[1])
		keys_found.append(l[2])

# Decrypt four times the encrypted flag with the recovered key
for k in keys_found[::-1]:
	cipher = AES.new(k, AES.MODE_CBC, IV=iv)
	flag = cipher.decrypt(flag)


print(flag)
# ijctf{sp4ce_T1me_Tr4d3off_is_c00l_but_crYpt0_1s_c00l3r_abcdefgh}
