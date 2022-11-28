from cont import a, b, c, d, flag
print(flag)

print( "De1CTF{" + ''.join([hex(i)[2:] for i in [a, b, c, d]]) + "}")
# assert flag == "De1CTF{" + ''.join([hex(i)[2:] for i in [a, b, c, d]]) + "}"
print([len(bin(i)[2:]) for i in [a, b, c, d]]) 
# assert [len(bin(i)[2:]) for i in [a, b, c, d]] == [19, 19, 13, 6]

ma, mb, mc, md = 0x505a1, 0x40f3f, 0x1f02, 0x31
print(bin(ma))
print(bin(mb))
print(bin(mb))
print(bin(mc))


def lfsr(r, m): return ((r << 1) & 0xffffff) ^ (bin(r & m).count('1') % 2)


def combine():
    global a, b, c, d
    print("-.-.-.-.-.-.-.-.-.-.--.")
#    print(bin((a << 1) & 0xffffff))
    print(bin(a), bin(b))
#    print(bin(a))
#    print(bin( a & ma))
    print(bin( a & ma).count('1') % 2)
#    print(((a << 1) & 0xffffff) ^ (bin(a & ma).count('1') % 2))

    a = lfsr(a, ma)
    b = lfsr(b, mb)
    c = lfsr(c, mc)
    d = lfsr(d, md)
    [ao, bo, co, do] = [i & 1 for i in [a, b, c, d]]
    print(ao, bo)
    # prende last bit
    return (ao*bo) ^ (bo*co) ^ (bo*do) ^ co ^ do


def genkey(nb):
    s = ''
    for i in range(nb*8):
        re= str(combine())
        s+=re
        if i == 9:
            exit()
    open("data2", "w+").write(s)
    print(len(s))


genkey(128*1024)

def retrievekey(nb):
    r = open("data2", "r").read()
