from hashlib import md5
from base64 import b64decode
from base64 import b64encode
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from random import randrange
import string

alphabet = string.ascii_lowercase + string.ascii_uppercase + string.digits
iv = md5(b"ignis").digest()

flag = "ijctf{i am not the real flag :)}"
message = b"Its dangerous to solve alone, take this" + b"\x00"*9 

keys = []
for i in range(4):
    key = alphabet[randrange(0,len(alphabet))] + alphabet[randrange(0,len(alphabet))]
    keys.append(key.encode() + b'\x00'*14)

for key in keys:
    cipher = AES.new(key, AES.MODE_CBC, IV=iv)
    flag = cipher.encrypt(flag)
    
for key in keys:
    cipher = AES.new(key, AES.MODE_CBC, IV=iv)
    message = cipher.encrypt(message)

print(f"flag= {b64encode(flag)}")
print(f"message= {b64encode(message)}")