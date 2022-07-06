from sys import stdin

commandlist = []

for line in stdin:
    if line == '':
        break
    if line == '\n':
        continue
    commandlist.append(line)

for i in range(len(commandlist)) :
    commandlist[i] = commandlist[i].replace("\t"," ")
    commandlist[i] = commandlist[i].strip("\n")
    commandlist[i] = commandlist[i].strip(' ')
    commandlist[i] = list(commandlist[i].split(" "))

for i in commandlist:
    if '' in i:
        xxx = i.count('')
        for j in range(xxx):
            i.remove('')

for i in range(len(commandlist)):
    commandlist[i].append(i+1)

totalCommands = len(commandlist)
variables = []
variableAddress = {}

for i in range(totalCommands):
    if commandlist[i][0] == 'var':
        dum = commandlist[i][1]
        variables.append(dum)

varnum = len(variables)

for i in range(totalCommands):
    if commandlist[i][0] == 'var':
        dum = commandlist[i][1]
        variableAddress[dum] = format( totalCommands+i-varnum , '08b')

labels = []
labelAddress = {}

for i in commandlist:
    if i[0][-1] == ':':
        dum = i[0][:-1]
        labels.append(dum)
        labelAddress[dum] = format( i[-1]-1-varnum , '08b')
    else:
        i.insert(0,'def:')

instructions = ['add','sub','mov','ld','st','mul','div','rs','ls','xor','or','and','not','cmp','jmp','jlt','jgt','je','hlt','var']

opcodes = { 'add' : '10000' , 'sub' : '10001' , 'movimm' : '10010' ,
            'movreg' : '10011' , 'ld' : '10100' , 'st' : '10101' ,
            'mul' : '10110' , 'div' : '10111' , 'rs' : '11000' ,
            'ls' : '11001' , 'xor' : '11010' , 'or' : '11011' ,
            'and' : '11100' , 'not' : '11101' , 'cmp' : '11110' ,
            'jmp' : '11111' , 'jlt' : '01100' , 'jgt' : '01101' ,
            'je' : '01111' , 'hlt' : '01010' }

type = { 'add' : 'A' , 'sub' : 'A' , 'movimm' : 'B' ,
            'movreg' : 'C' , 'ld' : 'D' , 'st' : 'D' ,
            'mul' : 'A' , 'div' : 'C' , 'rs' : 'B' ,
            'ls' : 'B' , 'xor' : 'A' , 'or' : 'A' ,
            'and' : 'A' , 'not' : 'C' , 'cmp' : 'C' ,
            'jmp' : 'E' , 'jlt' : 'E' , 'jgt' : 'E' ,
            'je' : 'E' , 'hlt' : 'F' }

registerAddress = {'R0' : '000','R1' : '001','R2' : '010','R3' : '011','R4' : '100','R5' : '101','R6' : '110','FLAGS' : '111'}

registers = ['R0' , 'R1' , 'R2' , 'R3', 'R4', 'R5', 'R6', 'FLAGS']

def representsInteger(str):
    try:
        int(str)
        return True
    except ValueError :
        return False

def ErrorGenerator():
    hflag = 0
    for i in commandlist:
        command = i[1]
        if command not in instructions:
            print(f'Error in line {i[-1]} : Typo in instruction name')
            exit()
        if command == 'var' :
            if i[-1]>len(variables):
                print(f'Error in line {i[-1]} : Variables not declared at the beginning')
                exit()
            else:
                continue
        if command == 'mov':
            if i[-2][0] == '$':
                command = 'movimm'
            else:
                command = 'movreg'
        instype = type[command]
        if instype == 'A':
            if len(i)!=6:
                print(f'Error in line {i[-1]} : General Syntax Error')
                exit()
            range = [-2,-3,-4]
            for j in range:
                r1 = i[j]
                if r1 not in registers:
                    print(f'Error in line {i[-1]} : Typo in register name')
                    exit()
                if r1 == 'FLAGS':
                    print(f'Error in line {i[-1]} : Illegal use of FLAGS register')
                    exit()
        elif instype == 'B':
            if len(i)!=5:
                print(f'Error in line {i[-1]} : General Syntax Error')
                exit()
            x = 0
            if representsInteger(i[-2][1:]):
                x = int(i[-2][1:])
            else:
                print(f'Error in line {i[-1]} : Immediate Value is not int')
                exit()
            if x > 255 or x<0 :
                print(f'Error in line {i[-1]} : Illegal Immediate value (more than 8 bits)')
                exit()
            r1 = i[-3]
            if r1 not in registers:
                print(f'Error in line {i[-1]} : Typo in register name')
                exit()
            if r1 == 'FLAGS':
                print(f'Error in line {i[-1]} : Illegal use of FLAGS register')
                exit()
        elif instype == 'C':
            if len(i)!=5:
                print(f'Error in line {i[-1]} : General Syntax Error')
                exit()
            r1 = i[-3]
            if r1 not in registers:
                print(f'Error in line {i[-1]} : Typo in register name')
                exit()
            if command != 'movreg':
                if r1 == 'FLAGS':
                    print(f'Error in line {i[-1]} : Illegal use of FLAGS register')
                    exit()
            r1 = i[-2]
            if r1 not in registers:
                print(f'Error in line {i[-1]} : Typo in register name')
                exit()
            if r1 == 'FLAGS':
                print(f'Error in line {i[-1]} : Illegal use of FLAGS register')
                exit()
        elif instype == 'D':
            if len(i)!=5:
                print(f'Error in line {i[-1]} : General Syntax Error')
                exit()
            v1 = i[-2]
            if v1 in labels:
                print(f'Error in line {i[-1]} : Misuse of label as variable')
                exit()
            if v1 not in variables:
                print(f'Error in line {i[-1]} : Use of undefined variable')
                exit()
            r1 = i[-3]
            if r1 not in registers:
                print(f'Error in line {i[-1]} : Typo in register name')
                exit()
            if r1 == 'FLAGS':
                print(f'Error in line {i[-1]} : Illegal use of FLAGS register')
                exit()
        elif instype == 'E':
            if len(i)!=4:
                print(f'Error in line {i[-1]} : General Syntax Error')
                exit()
            l1 = i[-2]
            if l1 in variables:
                print(f'Error in line {i[-1]} : Misuse of variable as label')
                exit()
            if l1 not in labels:
                print(f'Error in line {i[-1]} : Use of undefined label')
                exit()
        elif instype == 'F':
            hflag = 1
            if len(i)!=3:
                print(f'Error in line {i[-1]} : General Syntax Error')
                exit()
            if i[-1] != len(commandlist):
                print(f'Error in line {i[-1]} : hlt not being used as last instruction')
                exit()
    if hflag == 0:
        print(f'Error in line {i[-1]} : Missing hlt instructions')
        exit()

ErrorGenerator()

def UltimateBinaryGenerator():
    for i in commandlist:
        command = i[1]
        if command == 'var' :
            continue
        if command == 'mov':
            if i[-2][0] == '$':
                command = 'movimm'
            else:
                command = 'movreg'
        instype = type[command]
        s = opcodes.get(command)
        if instype == 'A':
            s += '00'
            r1 = i[2]
            r2 = i[3]
            r3 = i[4]
            s += registerAddress.get(r1) + registerAddress.get(r2) + registerAddress.get(r3)
        elif instype == 'B':
            r1 = i[2]
            x = int(i[-2][1:])
            s += registerAddress.get(r1) + format(x,'08b')
        elif instype == 'C':
            s += '00000'
            r1 = i[2]
            r2 = i[3]
            s += registerAddress.get(r1) + registerAddress.get(r2)
        elif instype == 'D':
            r1 = i[2]
            v1 = i[3]
            s += registerAddress.get(r1) + variableAddress.get(v1)
        elif instype == 'E':
            s += '000'
            l1 = i[2]
            s += labelAddress.get(l1)
        elif instype == 'F':
            s += '0'*11
        print(s)

UltimateBinaryGenerator()
