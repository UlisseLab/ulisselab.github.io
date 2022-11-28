#!/usr/bin/env python3

def combine(ao, bo, co, do):
    return (ao*bo) ^ (bo*co) ^ (bo*do) ^ co ^ do

a = [0, 1]
b = [0, 1]
c = [0, 1]
d = [0, 1]
stat = {}
stat.setdefault('i', 0)
stat.setdefault('j', 0)
stat.setdefault('k', 0)
stat.setdefault('z', 0)
print("a  b  c  d | o")
for i in range(0, 2):
    for j in range(0, 2):
        for k in range(0, 2):
            for z in range(0, 2):
                res = combine(i, j, k, z)
                if res == i:
                    stat['i'] += 1
                if res == j:
                    stat['j'] += 1
                if res == k:
                    stat['k'] += 1
                if res == z:
                    stat['z'] += 1
                print("%d  %d  %d  %d | %d " %(i, j, k, z, res))
