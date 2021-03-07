import json


def load_json(filename):
    with open(filename) as f:
        data = json.load(f)
    return data


def load_file(filename):
    bytecode = []
    with open(filename, "rb") as f:
        byte = f.read(1)
        while byte:
            byte = f.read(1)
            i = int.from_bytes(byte, byteorder='big')
            bytecode.append(i)
    bytecode = bytecode[1:]  # remove first 2 bytes
    bytecode = bytecode[:-1]  # remove last byte
    return(bytecode)


def display_full_assembly(assembly):
    program = ""
    for command in assembly:

        # display the sequence of byte for an instruction
        byte_sequence = ""
        for byte in command["b"]:
            byte_sequence = byte_sequence + number_to_hex(byte) + " "

        # put address, bytes and instruction together in one line
        program = program + "\n" + \
            command["a"] + " | " + command["l"] + "    " + \
            byte_sequence + "       " + command["i"]
    print(program)


def create_program(assembly):
    program = ""
    for command in assembly:
        # put address, bytes and instruction together in one line
        program = program + "\n" + \
            command["l"] + "    " + \
            command["i"]
    return(program)


def write_asm_file(filename, data):
    f = open(filename, "w")
    f.write(data)
    f.close()


def number_to_hex(number):
    val = hex(number)[2:]
    if len(val) == 1:
        val = "0" + val
    return val


def bytes_to_asm(bytes, startaddr, opcodes):
    asm = []
    sp = 0
    end = len(bytes)
    label_prefix = ".l"

    while sp < end:
        byte = bytes[sp]
        instruction = opcodes[number_to_hex(byte)]
        opcode = instruction["o"]
        instruction_length = instruction["l"]

        memorylocation = str(hex(startaddr + sp)[2:])
        label = label_prefix+memorylocation

        byte_sequence = []
        byte_sequence.append(byte)

        if instruction_length == 1:
            sp += 1
            high_byte = bytes[sp]
            opcode = opcode.replace("hh", number_to_hex(high_byte))
            byte_sequence.append(high_byte)
        if instruction_length == 2:
            sp += 1
            low_byte = bytes[sp]
            sp += 1
            high_byte = bytes[sp]
            opcode = opcode.replace("hh", number_to_hex(high_byte))
            opcode = opcode.replace("ll", number_to_hex(low_byte))
            byte_sequence.append(low_byte)
            byte_sequence.append(high_byte)

        sp = sp+1

        line = {
            "a": memorylocation,
            "l": label,
            "b": byte_sequence,
            "i": opcode
        }
        asm.append(line)

    return asm


opcodes = load_json("opcodes.json")
