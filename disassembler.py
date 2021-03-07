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


# prints out the converted assembly program
# including memory address, bytes and instructions
# useful for debugging
def display_full_assembly(assembly):

    program = ""
    for command in assembly:

        # display the sequence of byte for an instruction
        byte_sequence = ""
        for byte in command["b"]:
            byte_sequence = byte_sequence + number_to_hex(byte) + " "

        if command["show_label"]:
            label_info = "-"
        else:
            label_info = ""

         # put address, bytes and instruction together in one line
        program = program + "\n" + \
            command["a"] + " | " + command["l"] + label_info + "    " + \
            byte_sequence + "       " + command["i"]
    print(program)


def reduce_labels(asm):
    # goes through the code and checks which relative labels are
    # in use, then adds a "show_label" key to each address that
    # is a branching destination

    # step 1: collect all relative branches in code
    labels_used = []

    for line in asm:
        if "rel_branch" in line:
            labels_used.append(line["rel_branch"])
    print(labels_used)

    # step 2: add key to each line to show the label if it was actually used
    length = len(asm)
    l = 0
    while l < length:
        if asm[l]["l"] in labels_used:
            asm[l]["show_label"] = True
        else:
            asm[l]["show_label"] = False
        l = l + 1
    return (asm)


# formats the assembly code so it can be saved as a program later
def create_program(assembly):

    program = ""
    for command in assembly:
        # put address, bytes and instruction together in one line
        if command["show_label"]:
            label = "\n" + command["l"] + "\n"
        else:
            label = ""

        program = program + "\n" + \
            label + "    " + \
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


# inspects byte for byte and converts them into
# instructions based on the opcode json
# returns an array with objects for each code line
def bytes_to_asm(bytes, startaddr, opcodes):
    asm = []
    pc = 0
    end = len(bytes)
    label_prefix = ".l"

    while pc < end:
        byte = bytes[pc]
        instruction = opcodes[number_to_hex(byte)]
        opcode = instruction["o"]

        # check for the key "r" in the opcode json
        # which stands for "relative addressing"
        # it is needed e.g. for branching like BNE, BCS etc.
        if "r" in instruction:
            is_relative = True
        else:
            is_relative = False

        instruction_length = instruction["l"]
        memory_location = str(hex(startaddr + pc)[2:])
        label = label_prefix+memory_location
        byte_sequence = []
        byte_sequence.append(byte)

        if instruction_length == 1:
            pc += 1
            high_byte = bytes[pc]

            # if a relative instruction like BCC or BNE occurs
            if is_relative:
                if high_byte > 127:
                    # substract (255 - highbyte) from current address
                    address = str(hex(startaddr + pc - (255 - high_byte))[2:])
                else:
                    # add highbyte to current address
                    address = str(hex(startaddr + pc + high_byte + 1)[2:])
                opcode = opcode.replace("$hh", label_prefix + address)
            else:
                opcode = opcode.replace("hh", number_to_hex(high_byte))

            byte_sequence.append(high_byte)

        if instruction_length == 2:
            pc += 1
            low_byte = bytes[pc]
            pc += 1
            high_byte = bytes[pc]
            opcode = opcode.replace("hh", number_to_hex(high_byte))
            opcode = opcode.replace("ll", number_to_hex(low_byte))
            byte_sequence.append(low_byte)
            byte_sequence.append(high_byte)

        pc = pc+1

        line = {
            "a": memory_location,
            "l": label,
            "b": byte_sequence,
            "i": opcode,
        }

        if is_relative:
            line["rel_branch"] = label_prefix+address
        asm.append(line)

    asm = reduce_labels(asm)
    return asm


opcodes = load_json("opcodes.json")
