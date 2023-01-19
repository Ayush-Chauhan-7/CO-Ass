from sys import stdin
from matplotlib import pyplot as plt
import math

mem = []

for line in stdin:
    if line == '':
        break
    if line=='\n':
        continue
    line = line.strip()
    mem.append(line)

size = len(mem)

for i in range(256 - size):
    mem.append("0"*16)

def decimalToBinary(n):
    return format(n,'016b')

def binaryToDecimal(b) :
    return int(b,2)

def floattoBinary(n):
    res = ''
    if n - int(n) == 0:
        n = int(n)
        res = bin(n)[2:]
    else:
        whole , dec = str(n).split(".")
        whole = int(whole)
        x = len(dec)
        dec = int(dec)
        y = math.ceil(math.log(dec,10))
        dec = dec/(10**(x - y + math.ceil(math.log(dec,10))))
        res += bin(whole)[2:]+'.'
        i = 0
        while i<5 and dec!=0:
            dec *= 2
            i += 1
            if dec>=1:
                res += '1'
                dec %= 1
            else:
                res += '0'
        if dec!= 0.0:
            raise TypeError
    exp = int(math.log(n,2))
    if exp>7 or exp<0:
        raise TypeError
    res = res.replace('.','')
    mantissa = ''
    if len(res)>=6:
        xx = res[6:]
        if xx.count('1')!=0:
            raise TypeError
        mantissa = res[1:6]
    else:
        mantissa = res[1:]
        mantissa += '0'*(5-len(mantissa))
    return format(exp,'03b') + mantissa

def binarytoFloat(exp, mantissa):
    flt = (2**exp)*( 1 + int(mantissa[0])*(2**(-1)) + int(mantissa[1])*(2**(-2)) + int(mantissa[2])*(2**(-3)) + int(mantissa[3])*(2**(-4)) + int(mantissa[4])*(2**(-5)))
    return flt

registers = {'000' : '0000000000000000' , '001' : '0000000000000000' , '010' : '0000000000000000' ,
             '011' : '0000000000000000' , '100' : '0000000000000000' , '101' : '0000000000000000' , 
             '110' : '0000000000000000' , '111' : '0000000000000000'}

type = { '10000' : 'A' , '10001' : 'A' , '10010' : 'B' ,
         '10011' : 'C' , '10100' : 'D' , '10101' : 'D' ,
         '10110' : 'A' , '10111' : 'C' , '11000' : 'B' ,
         '11001' : 'B' , '11010' : 'A' , '11011' : 'A' ,
         '11100' : 'A' , '11101' : 'C' , '11110' : 'C' ,
         '11111' : 'E' , '01100' : 'E' , '01101' : 'E' ,
         '01111' : 'E' , '01010' : 'F' , '00000' : 'H' ,
         '00001' : 'H' , '00010' : 'H'}

def typeA(instruction):
    opcode = instruction[:5]
    r1 = instruction[13:]
    int1 = 0
    int2 = binaryToDecimal(registers.get(instruction[7:10]))
    int3 = binaryToDecimal(registers.get(instruction[10:13]))
    val1 = ''
    if opcode == '10000':
        int1 = int2 + int3
        val1 = decimalToBinary(int1)
        registers['111'] = '0000000000000000'
        if int1 > 65535 :
            registers['111'] = '0000000000001000'
            val1 = val1[-16:]
    elif opcode == '10001':
        int1 = int2 - int3
        if int1 < 0 :
            registers['111'] = '0000000000001000'
            val1 = '0000000000000000'
        else :
            registers['111'] = '0000000000000000'
            val1 = decimalToBinary(int1)
    elif opcode == '10110':
        int1 = int2 * int3
        val1 = decimalToBinary(int1)
        registers['111'] = '0000000000000000'
        if int1 > 65535 :
            registers['111'] = '0000000000001000'
            val1 = val1[-16:]
    else:
        if opcode == '11010':
            int1 = int2 ^ int3
        elif opcode == '11011':
            int1 = int2 | int3
        elif opcode == '11100':
            int1 = int2 & int3
        val1 = decimalToBinary(int1)
        registers['111'] = '0000000000000000'
    registers[r1] = val1

def typeB(instruction):
    opcode = instruction[:5]
    r1 = instruction[5:8]
    immval = instruction[8:]
    if opcode == '10010':
        registers[r1] = "0"*8 + immval
    else:
        shift = binaryToDecimal(immval)
        intval = binaryToDecimal(registers.get(r1))
        if opcode == '11000':
            intval >>= shift
        elif opcode == '11001':
            intval <<= shift
        registers[r1] = decimalToBinary(intval)[-16:]
    registers['111'] = '0000000000000000'

def typeC(instruction):
    opcode = instruction[:5]
    r1 = instruction[13:]
    r2 = instruction[10:13]
    int1 = binaryToDecimal(registers.get(r1))
    int2 = binaryToDecimal(registers.get(r2))
    if opcode == '10011':
        registers[r1] = registers.get(r2)
        registers['111'] = '0000000000000000'
    elif opcode == '10111':
        x , y = divmod(int2, int1)
        registers['000'] = decimalToBinary(x)
        registers['001'] = decimalToBinary(y)
        registers['111'] = '0000000000000000'
    elif opcode == '11101':
        val = registers.get(r2)
        notval = "".join(["0" if c == "1" else "1" for c in val])
        registers[r1] = notval
        registers['111'] = '0000000000000000'
    elif opcode == '11110':
        if int1 < int2 :
            registers['111'] = '0000000000000010'
        elif int1 == int2 :
            registers['111'] = '0000000000000001'
        else :
            registers['111'] = '0000000000000100'

def typeD(instruction):
    opcode = instruction[:5]
    r1 = instruction[5:8]
    address = instruction[8:]
    index = binaryToDecimal(address)
    if opcode == '10100':
        registers[r1] = mem[index]
    elif opcode == '10101':
        mem[index] = registers.get(r1)
    registers['111'] = '0000000000000000'
    return address

def typeE(instruction):
    opcode = instruction[:5]
    address = instruction[8:]
    if opcode == '11111':
        registers['111'] = '0000000000000000'
        return address
    elif opcode == '01100':
        if registers['111'] == '0000000000000100' :
            registers['111'] = '0000000000000000'
            return address
    elif opcode == '01101':
        if registers['111'] == '0000000000000010' :
            registers['111'] = '0000000000000000'
            return address
    elif opcode == '01111':
        if registers['111'] == '0000000000000001' :
            registers['111'] = '0000000000000000'
            return address
    registers['111'] = '0000000000000000'
    return '12345678'

def typeH(instruction):
    opcode = instruction[:5]
    if opcode == '00000':
        r1 = instruction[13:]
        f1 = registers.get(instruction[7:10])[8:]
        f2 = registers.get(instruction[10:13])[8:]
        exp1 = int(f1[:3],2)
        exp2 = int(f2[:3],2)
        x1 = binarytoFloat(exp1,f1[3:])
        x2 = binarytoFloat(exp2,f2[3:])
        x3 = x1 + x2
        if x3>252.0:
            registers['111'] = '0000000000001000'
            registers[r1] = '0'*8 + '1'*8
        else:
            try:
                s1 = floattoBinary(x3)
                registers[r1] = '0'*8 + s1
                registers['111'] = '0000000000000000'
            except:
                registers['111'] = '0000000000001000'
                registers[r1] = '0'*16
    elif opcode == '00001':
        r1 = instruction[13:]
        f1 = registers.get(instruction[7:10])[8:]
        f2 = registers.get(instruction[10:13])[8:]
        exp1 = int(f1[:3],2)
        exp2 = int(f2[:3],2)
        x1 = binarytoFloat(exp1,f1[3:])
        x2 = binarytoFloat(exp2,f2[3:])
        x3 = x1 - x2
        try:
            s1 = floattoBinary(x3)
            registers[r1] = '0'*8 + s1
            registers['111'] = '0000000000000000'
        except:
            registers['111'] = '0000000000001000'
            registers[r1] = '0'*16
    elif opcode == '00010':
        r1 = instruction[5:8]
        immval = instruction[8:]
        registers[r1] = '0'*8 + immval
        registers['111'] = '0000000000000000'
        

def nextpc(pc):
    xx = binaryToDecimal(pc) + 1
    return format(xx,'08b')

def UltimateSimulator(pc):
    index = binaryToDecimal(pc)
    instruction = mem[index]
    newpc = ''
    halted = False
    instype = type.get(instruction[:5])
    if instype == 'A':
        typeA(instruction)
        newpc = nextpc(pc)
    elif instype == 'B':
        typeB(instruction)
        newpc = nextpc(pc)
    elif instype == 'C':
        typeC(instruction)
        newpc = nextpc(pc)
    elif instype == 'D':
        y = typeD(instruction)
        index = binaryToDecimal(y)
        newpc = nextpc(pc)
    elif instype == 'E':
        newpc = nextpc(pc)
        x = typeE(instruction)
        if x!='12345678':
            newpc = x  
    elif instype == 'H':
        typeH(instruction)
        newpc = nextpc(pc)
    else:
        halted = True
        registers['111'] = '0000000000000000'
    print(pc,end=' ')
    for i in registers.values() :
        print(i,end=' ')
    print()
    return newpc,halted,index

halted = False
pc = "0"*8
cycle = 0
xl = []
yl = []

while not halted:
    newpc , halted,memo = UltimateSimulator(pc)
    pc = newpc
    xl.append(cycle)
    yl.append(memo)
    cycle += 1

for i in mem:
    print(i)

plt.scatter(xl,yl)
plt.title('Memory Accesses v/s Cycles')
plt.xlabel('Cycle')
plt.ylabel('Address')
plt.tight_layout()
plt.savefig('plot.png')