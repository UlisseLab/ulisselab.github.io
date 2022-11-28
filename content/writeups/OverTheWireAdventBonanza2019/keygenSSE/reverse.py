#!/bin/python
from cachetools import cached, LRUCache, TTLCache
import time
import numpy as np
import struct
from unicorn import *
from unicorn.x86_const import *

#def internalCycle():
#    #m6 = m4
#    #pcmpgtd xmm6, xmm3
#    #paddd xmm6, xmm5
#    #pmulld xmm6, xmm4
#    #psubd xmm3, xmm6
#    #movdqa xmm6, xmm4
#    #pcmpgtd xmm6, xmm2
#    #paddd xmm6, xmm5
#    #pmulld xmm6, xmm4
#    #psubd xmm2, xmm6
#    #movdqa xmm6, xmm4
#    #pcmpgtd xmm6, xmm1
#    #paddd xmm6, xmm5
#    #pmulld xmm6, xmm4
#    #psubd xmm1, xmm6
#    #movdqa xmm6, xmm4
#    #pcmpgtd xmm6, xmm0
#    #paddd xmm6, xmm5
#    #pmulld xmm6, xmm4
#    #psubd xmm0, xmm6
#    #add edx, 0xffffffff
#
@cached(cache={})
def pshufd(src,order):
    line=bin(src)[2:].rjust(128,"0")
    n=32
    src=[line[i:i+n] for i in range(0, len(line), n)][::-1]
    line=bin(order)[2:].rjust(8,"0")
    n=2
    order=[line[i:i+n] for i in range(0, len(line), n)]
    res=""
    for i in order:
        val=int(i,2)
        res+=src[val]
    return int(res,2)

@cached(cache={})
def pmulld(val1,val2):
    line=bin(val1)[2:]
    line=line.rjust(128,"0")
    n=32
    val1=[line[i:i+n] for i in range(0, len(line), n)]
    line=bin(val2)[2:].rjust(128,"0")
    val2=[line[i:i+n] for i in range(0, len(line), n)]
    res=""
    for i,j in zip(val1,val2):
        res+=str(int(i,2)*int(j,2)).rjust(32,"0")
    return int(res,16)

@cached(cache={})
def paddd(val1,val2):
    line=bin(val1)[2:]
    line=line.rjust(128,"0")
    n=32
    val1=[line[i:i+n] for i in range(0, len(line), n)]
    line=bin(val2)[2:].rjust(128,"0")
    val2=[line[i:i+n] for i in range(0, len(line), n)]
    res=""
    for i,j in zip(val1,val2):
        res+=str(int(i,2)+int(j,2)).rjust(32,"0")
    return int(res,16)


@cached(cache={})
def m_fun(s1, s2, s3):
    m = pmulld(s1, s2)
    m = paddd(m, s3)
    return m


@cached(cache={})
def fun(s1, s2, s3, s4):
    m = m_fun(s1, s2, s3)
    m = paddd(m, s4)
    return m


@cached(cache={})
def mainFake():
    start_time = time.time()
    data = open('reverse_data', 'rb').read()

    res = int.from_bytes(data[64:80], byteorder='little')
    i0 = pshufd(res, 0x15)
    i1 = pshufd(res, 0x45)
    i2 = pshufd(res, 0x51)
    i3 = pshufd(res, 0x54)
#    print(hex(i0),hex(i1),hex(i2),hex(i3))
# ----------------------------------
#    i = [
#            [1, 0, 0, 0],
#            [0, 1, 0, 0],
#            [0, 0, 1, 0],
#            [0, 0, 0, 1]
#        ]

    counter = 0x112210f47de98115
    rax = 0

#    d9 =  int.from_bytes(data[:16],   byteorder='little')
#    d10 = int.from_bytes(data[16:32], byteorder='little')
#    d13 = int.from_bytes(data[32:48], byteorder='little')
#    d15 = int.from_bytes(data[48:64], byteorder='little')
#
#    s00 = pshufd(d9,    0)
#    s01 = pshufd(d9,   0x55)
#    sss5= pshufd(d9,    0xaa)
#    s03 = pshufd(d9,    0xff)
#
#    s10 = pshufd(d10,   0)
#    s5 = pshufd(d10,   0x55)
#    s12 = pshufd(d10,   0xaa)
#    s13 = pshufd(d10,   0xff)
#
#    s20 = pshufd(d13,  0)
#    s21 = pshufd(d13,   0x55)
#    s22 = pshufd (d13, 0xaa)
#    s23 = pshufd(d13,  0xff)
#
#    s30 = pshufd(d15,  0)
#    s31 = pshufd(d15,   0x55)
#    s32 = pshufd(d15,  0xaa)
#    s33 = pshufd(d15,  0xff)
#
#    print(hex(s00 ), hex(s01), hex(sss5), hex(s03 ))
#    print(hex(s10 ), hex(s5 ), hex(s12), hex(s13 ))
#    print(hex(s20), hex(s21 ), hex(s22 ), hex(s23))
#    print(hex(s30), hex(s31 ), hex(s32 ), hex(s33))
#
#    #---------------------------------
    s00 = 1 ; s01 = 2 ; s02 = 3 ; s03 = 4 ;
    s10 = 5 ; s11 = 6 ; s12 = 7 ; s13 = 8 ;
    s20 = 9 ; s21 = 10; s22 = 11; s23 = 12;
    s30 = 13; s31 = 14; s32 = 15; s33 = 16;
#    s = [
#            [1 , 2, 3, 4],
#            [5 , 6, 7, 8],
#            [9 ,10,11,12],
#            [13,14,15,16]
#        ]


    while(rax != counter):
        # prima colonna
        m6  = pmulld(s00, i3)
        m8  = pmulld(s10, i3)
        m11 = pmulld(s20, i3)
        m14 = pmulld(s30, i3)

        #--------------------
        m12 = m_fun(s01, i2, m6) #xmm12s * xmm2 * xmm6 = xmm12
        m5 = pmulld(s11,  i1) #xmm5s *xmm1 = xmm5
        i3 = fun(s03, i0, m5, m12)

        mm5 = m_fun(s11, i2, m8)
        m7 = m_fun(s21, i2, s20)
        mm6 = pmulld(s12, i1)       #64c
        i2 = fun(s13, i0, mm6, mm5) #662

        mmm5 = pmulld(s22, i1)
        mmm6 = pmulld(s32, i1)      #680
        i1 = fun(s23, i0, mmm5, m7)

        m4 = m_fun(s31, i2, m14)
        i0 = fun(s33, i0, mmm6, m4)

        #var ciclo interno
#        m4 = pshufd(sres, 0xaa)
#        m5 = pshufd(i0, 0)
#        edx = 0x3e8
#        internalCycle()

        rax += 1
        if rax % 10000000 == 0:
            print(time.time()-start_time)


def emulation(matrix):
    BASE    = 0x400000
    STACK   = 0x7ffcaf000000
    FLAG    = 0x00600000

    mu = Uc(UC_ARCH_X86, UC_MODE_64)
    mu.mem_map(BASE, 1024*4)
    mu.mem_map(STACK, 1024*4)
    mu.mem_map(FLAG, 1024*1024)

    code = struct.pack ("69B", *[
        0x66,0x0f,0x7f,0x1c,0x24,0x66,0x0f,0x7f,0x54,0x24,0x10,
        0x66,0x0f,0x7f,0x4c,0x24,0x20,0x66,0x0f,0x7f,0x44,0x24,
        0x30,0x31,0xc0,0x66,0x2e,0x0f,0x1f,0x84,0x00,0x00,0x00,
        0x00,0x00,0x0f,0x1f,0x00,0x0f,0xb6,0x0c,0x44,0x30,0x88,
        0x90,0x10,0x60,0x00,0x0f,0xb6,0x4c,0x44,0x01,0x30,0x88,
        0x91,0x10,0x60,0x00,0x48,0x83,0xc0,0x02,0x48,0x83,0xf8,
        0x20,0x75,0xe1])
    flag = struct.pack ("40B", *[
        0xfc,0x14,0xeb,0x09,0xbc,0xae,0xe7,0x47,0x4f,0xe3,0x7c,
        0xc1,0x52,0xa5,0x02,0x8e,0x89,0x71,0xc8,0x8d,0x96,0x23,
        0x01,0x6d,0x71,0x40,0x5a,0xea,0xfd,0x46,0x1d,0x23,0x00,
        0x00,0x00,0x00,0x00,0x00,0x00,0x00])

    mu.reg_write(UC_X86_REG_RSP, STACK)
    #print((matrix[0][0]<<96) + (matrix[0][1]<<64) + (matrix[0][2]<<32) + (matrix[0][3]))
    #print((matrix[1][0]<<96) + (matrix[1][1]<<64) + (matrix[1][2]<<32) + (matrix[1][3]))
    #print((matrix[2][0]<<96) + (matrix[2][1]<<64) + (matrix[2][2]<<32) + (matrix[2][3]))
    #print((matrix[3][0]<<96) + (matrix[3][1]<<64) + (matrix[3][2]<<32) + (matrix[3][3]))
    mu.reg_write(UC_X86_REG_XMM0, (matrix[0][0]<<96) + (matrix[0][1]<<64) + (matrix[0][2]<<32) + (matrix[0][3]))
    mu.reg_write(UC_X86_REG_XMM1, (matrix[1][0]<<96) + (matrix[1][1]<<64) + (matrix[1][2]<<32) + (matrix[1][3]))
    mu.reg_write(UC_X86_REG_XMM2, (matrix[2][0]<<96) + (matrix[2][1]<<64) + (matrix[2][2]<<32) + (matrix[2][3]))
    mu.reg_write(UC_X86_REG_XMM3, (matrix[3][0]<<96) + (matrix[3][1]<<64) + (matrix[3][2]<<32) + (matrix[3][3]))

    mu.mem_write(FLAG+0x1090, flag)

    mu.mem_write(BASE, code)
    mu.emu_start(BASE, BASE + len(code), 2 * UC_SECOND_SCALE)
    print(mu.mem_read(FLAG+0x1090, 0x20))


def moltiplication(exponent):
    a = np.array([          \
            [16,15,14,13],  \
            [12,11,10, 9],  \
            [8 , 7, 6, 5],  \
            [4 , 3, 2, 1]   \
        ], dtype=object)
    for i in range(exponent):
        np.dot(a,a,a)
        a = overflow(a)
    return a

def overflow(a):
    sres = int.from_bytes(data[72:76], byteorder='little')
    for x in range(4):
        for y in range(4):
            while a[x][y] > sres:
                a[x][y] %= sres
    return a

def calculate_exponents():
    res = []
    s = 1234567890123456789
    i=0
    while(s>0):
        if 2**i > s:
            res.append(i-1)
            s -= 2**(i-1)
            i=0
        else:
            i+=1
    return res

def main():
    matrix = np.array([\
        [1,0,0,0],  \
        [0,1,0,0],  \
        [0,0,1,0],  \
        [0,0,0,1]   \
    ], dtype=object)
    x = calculate_exponents()
    print("lista: ", x)
    for a in x:
        np.dot(matrix, moltiplicazione(a), matrix)
        overflow(matrix)
    print("matrix: ", matrix)

    emulation(matrix)

main()
