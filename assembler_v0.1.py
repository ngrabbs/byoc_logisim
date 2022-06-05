import sys
import re

labels = {}
data = {}

instruction_types = {
    "MVI": "000",
    "DCR": "100",
    "ANI": "001",
    "BNZ": "101",
    "JMP": "111",
    "CALL": "110",
    "RET": "110",
    "MOV": "010",
    "LRAM": "011",
    "LROM": "011",
    "PUSH": "100",
    "POP": "100",
    "OR": "100",
    "BZ": "101",
    "ADD": "100",
    "CPI": "001",
    "BC": "101",
    "INC": "100",
    "INP": "100",
    "OUT": "100",
    "INZ": "100",
    "ADI": "001",
    "SUB": "100",
    "SBB": "100",
    "BNC": "101",
    "ADC": "100",
    "CMP": "100"
}

registers = {
    "B": "000",
    "C": "001",
    "D": "010",
    "E": "011",
    "H": "100",
    "L": "101",
    "M": "110",
    "A": "111"
}

assembly = ''


def print_data(input):
    print(str(format(count, "04x")) + " " + format(int(input, 2), "05x") + " " + input + " " + line)
    return format(int(input, 2), "05x") + ' '


def calculate_jump(dest, current):
    if (dest == current):
        return (0 << 9)
    elif (dest < current):
        return ((1 << 9) - (current - dest))
    else:
        return ((0 << 9) + (dest - current))


def generate_labels(f):
    labels = {}
    count = 0
    for line in f:
        if (not re.search("^;", line)) and (line.strip()):
            tok = re.split(r'\t+', line)

            if tok[0]:
                tok0arg = re.split(r'[:]', tok[0])
                labels[tok0arg[0].strip(":")] = count
            count += 1
    return labels


def generate_data(f):
    data = { "drom": []}
    count = 0
    in_data = 0
    for line in f:
        if (not re.search("^;", line)) and (line.strip()):
            if line.strip() == "data" and in_data == 0:
                in_data = 1
            elif line.strip() == "end" and in_data == 1:
                return data
            elif in_data == 1 and "equ" in line:
                temp = re.split(r'\t+', line)
                data[temp[0]] = temp[2]
            elif in_data == 1 and not "equ" in line and ":" in line:
                # its a address
                temp = re.split(r'\t+', line)
                data[temp[0].strip(":")] = format(len(data["drom"]), "04x")
                byte_by_byte = list(temp[1] + '\0')
                for x in byte_by_byte:
                    data["drom"].append(x.encode('utf-8').hex())

if len(sys.argv) != 2:
    print("Usage: " + sys.argv[0] + " <file.asm>")
    sys.exit()

with open(sys.argv[1]) as f:
    labels = generate_labels(f)
    f.seek(0)
    data = generate_data(f)
    count = 0
    f.seek(0)
    reached_data = 0
    for line in f:
        if (not re.search("^;", line)) and (line.strip() and (not reached_data)):

            line = line.replace('\n', '').replace('\r', '')

            # here we need to loop through the data and replace
            for element in data.keys():
                if element in line:
                    line = line.replace(element, data[element])

            tok = re.split(r'\t+', line)

            if '' in tok:
                tok.remove('')

            if 'data' in tok[0]:
                reached_data = 1
                break

            if ':' in tok[0]:
                # dump labels
                tok.pop(0)

            if tok[0] == "mvi":
                tok1arg = re.split(r'[,]', tok[1])
                if "hi(" in line or "lo(" in line:
                    m = re.compile("(hi|lo)\((.*)\)").search(tok1arg[1])
                    if m:
                        if "hi" in m.group(1):
                            bits = format(int(m.group(2)[:2], 16), "08b")
                        else:
                            bits = format(int(m.group(2)[2:], 16), "08b")
                elif 'b' in tok1arg[1]:
                    bits = tok1arg[1].strip("b")
                else:
                    bits = format(int(tok1arg[1]), "08b")

                assembly += print_data(
                    instruction_types[tok[0].upper()] +
                    registers[tok1arg[0].upper()] +
                    "000000" + bits)

            elif tok[0] == "dcr":
                assembly += print_data(
                    instruction_types[tok[0].upper()] +
                    registers[tok[1].upper()] +
                    "01000100000000")

            elif tok[0] == "ani":
                tok1arg = re.split(r'[,]', tok[1])
                if 'b' in tok1arg[1]:
                    bits = tok1arg[1].strip("b")
                else:
                    bits = format(int(tok1arg[1]), "08b")
                assembly += print_data(instruction_types[tok[0].upper(
                )] + registers[tok1arg[0].upper()] + "011000" + bits)

            elif tok[0] == "bnz":
                distance = calculate_jump(labels[tok[1]], count)
                assembly += print_data(
                    instruction_types[tok[0].upper()] + "00010000" + format(distance, "09b"))

            elif tok[0] == "jmp":
                assembly += print_data(
                    instruction_types[tok[0].upper()] + "1" + format(labels[tok[1]], "016b"))

            elif tok[0] == "call":
                # this is a forward address jump 16 bits wide
                assembly += print_data(
                    instruction_types[tok[0].upper()] + "1" + format(labels[tok[1]], "016b"))

            elif tok[0] == "ret":
                assembly += print_data(
                    instruction_types[tok[0].upper()] + "00000000000000000")

            elif tok[0] == "mov":
                tok1arg = re.split(r'[,]', tok[1])
                assembly += print_data(instruction_types[tok[0].upper()] + registers[tok1arg[0].upper(
                )] + "000000" + registers[tok1arg[1].upper()] + "00000")

            elif tok[0] == "lrom":
                assembly += print_data(instruction_types[tok[0].upper(
                )] + registers[tok[1].upper()] + "00000000000000")

            elif tok[0] == "lram":
                assembly += print_data(instruction_types[tok[0].upper(
                )] + registers[tok[1].upper()] + "10000000000000")

            elif tok[0] == "push":
                assembly += print_data(instruction_types[tok[0].upper(
                )] + registers[tok[1].upper()] + "110000" + "00000000")

            elif tok[0] == "pop":
                assembly += print_data(instruction_types[tok[0].upper(
                )] + registers[tok[1].upper()] + "111000" + "00000000")

            elif tok[0] == "or":
                tok1arg = re.split(r'[,]', tok[1])
                assembly += print_data(instruction_types[tok[0].upper()] + registers[tok1arg[0].upper(
                )] + "011001" + registers[tok1arg[1].upper()] + "00000")

            elif tok[0] == "bz":
                distance = calculate_jump(labels[tok[1]], count)
                assembly += print_data(
                    instruction_types[tok[0].upper()] + "00000000" + format(distance, "09b"))

            elif tok[0] == "add":
                tok1arg = re.split(r'[,]', tok[1])
                assembly += print_data(instruction_types[tok[0].upper()] + registers[tok1arg[0].upper(
                )] + "000000" + registers[tok1arg[1].upper()] + "00000")

            elif tok[0] == "cpi":
                tok1arg = re.split(r'[,]', tok[1])
                assembly += print_data(instruction_types[tok[0].upper(
                )] + registers[tok1arg[0].upper()] + "000100" + format(int(tok1arg[1]), "08b"))

            elif tok[0] == "bc":
                distance = calculate_jump(labels[tok[1]], count)
                assembly += print_data(
                    instruction_types[tok[0].upper()] + "00100000" + format(distance, "09b"))

            elif tok[0] == "inc":
                assembly += print_data(instruction_types[tok[0].upper(
                )] + registers[tok[1].upper()] + "010000" + "00000000")

            elif tok[0] == "inp":
                tok1arg = re.split(r'[,]', tok[1])
                assembly += print_data(instruction_types[tok[0].upper()] + registers[tok1arg[0].upper(
                )] + "111001" + "000" + format(int(tok1arg[1]), "05b"))

            elif tok[0] == "out":
                tok1arg = re.split(r'[,]', tok[1])
                assembly += print_data(instruction_types[tok[0].upper(
                )] + registers[tok1arg[1].upper()] + "110001" + format(int(tok1arg[0]), "08b"))
            
            elif tok[0] == "inz":
                assembly += print_data(instruction_types[tok[0].upper()] + registers[tok[1].upper()] 
                + "010010" + "00000000")
            
            elif tok[0] == "adi":
                tok1arg = re.split(r'[,]', tok[1])
                assembly += print_data(instruction_types[tok[0].upper()] + 
                registers[tok1arg[0].upper()] + "000000" + format(int(tok1arg[1]), "08b"))
            
            elif tok[0] == "sub":
                tok1arg = re.split(r'[,]', tok[1])
                assembly += print_data(instruction_types[tok[0].upper()] + 
                registers[tok1arg[0].upper()] + "000010" +
                registers[tok1arg[1].upper()] + "00000") 

            elif tok[0] == "sbb":
                tok1arg = re.split(r'[,]', tok[1])
                assembly += print_data(instruction_types[tok[0].upper()] + 
                registers[tok1arg[0].upper()] + "000011" +
                registers[tok1arg[1].upper()] + "00000") 

            elif tok[0] == "bnc":
                distance = calculate_jump(labels[tok[1]], count)
                assembly += print_data(instruction_types[tok[0].upper()] +
                "00110000" + format(distance, "09b"))
            
            elif tok[0] == "adc":
                tok1arg = re.split(r'[,]', tok[1])
                assembly += print_data(instruction_types[tok[0].upper()] +
                registers[tok1arg[0].upper()] + "000001" +
                registers[tok1arg[1].upper()] + "00000") 

            elif tok[0] == "cmp":
                tok1arg = re.split(r'[,]', tok[1])
                assembly += print_data(instruction_types[tok[0].upper()] +
                registers[tok1arg[0].upper()] + "000100" +
                registers[tok1arg[1].upper()] + "00000") 

            else:
                print("\ntoken: " + tok[0] +
                      " unknown, if it isnt a typo then add it\n")

            count += 1


print("")
print("ROM(" + str(len(assembly)) + "): " + assembly)
print("DROM(" + str(len(data["drom"])) + "): " + ' '.join(data["drom"]))
