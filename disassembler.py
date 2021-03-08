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
            byte_sequence = byte_sequence + number_to_hex_byte(byte) + " "

        if command["show_label"]:
            label_info = "-"
        else:
            label_info = ""

         # put address, bytes and instruction together in one line
        program = program + "\n" + \
            command["a"] + " | " + command["l"] + label_info + "    " + \
            byte_sequence + "       " + command["i"]
    print(program)


def remove_unused_labels(asm):
    # goes through the code and checks which relative labels are
    # in use, then adds a "show_label" key to each address that
    # is a branching destination

    # step 1: collect all relative branches in code
    labels_used = []

    for line in asm:
        if "rel" in line:
            labels_used.append(line["rel"])

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
    tabs = 4     # number of spaces for each "tab"

    program = "; converted with pydisass6502 by awsm of mayday!"
    program += "\n\n* = $" + assembly[0]["a"]

    for command in assembly:
        # put address, bytes and instruction together in one line
        if command["show_label"]:
            label = "\n" + command["l"] + "\n"
        else:
            label = ""

        program += "\n" + \
            label + (tabs * 3 * " ") + \
            command["i"]

        # when an illegal command is processed we add the byte
        # sequence as a comment, it's likely data
        if "ill" in command:
            comment_bytes = ""

            for byte in command["b"]:
                comment_bytes = comment_bytes + \
                    "$" + number_to_hex_byte(byte) + ", "
            comment_bytes = comment_bytes[:-2]

            program += (tabs * 6 -
                        int(len(command["i"]))) * " " + "; " + comment_bytes

        # add an extra line break after these instructions
        if "rts" in command["i"] or "jmp" in command["i"] or "rti" in command["i"]:
            program += "\n"
    return(program)


def write_asm_file(filename, data):
    f = open(filename, "w")
    f.write(data)
    f.close()


def number_to_hex_byte(number):
    return ("0" + hex(number)[2:])[-2:]


def number_to_hex_word(number):
    return ("0" + hex(number)[2:])[-4:]


# inspects byte for byte and converts them into
# instructions based on the opcode json
# returns an array with objects for each code line
def bytes_to_asm(bytes, startaddr, opcodes):
    asm = []
    pc = 0
    end = len(bytes)
    label_prefix = "l"

    while pc < end:
        byte = bytes[pc]
        opcode = opcodes[number_to_hex_byte(byte)]
        instruction = opcode["ins"]

        # check for the key "rel" in the opcode json
        # which stands for "relative addressing"
        # it is needed e.g. for branching like BNE, BCS etc.
        if "rel" in opcode:
            is_relative = True
        else:
            is_relative = False

        memory_location_hex = number_to_hex_word(startaddr + pc)
        label = label_prefix + memory_location_hex

        byte_sequence = []
        byte_sequence.append(byte)

        instruction_length = 0
        if "hh" in instruction:
            instruction_length += 1
        if "ll" in instruction:
            instruction_length += 1

        if instruction_length == 1:
            pc += 1
            high_byte = bytes[pc]

            # if a relative instruction like BCC or BNE occurs
            if is_relative:
                if high_byte > 127:
                    # substract (255 - highbyte) from current address
                    address = number_to_hex_word(
                        startaddr + pc - (255 - high_byte))
                else:
                    # add highbyte to current address
                    address = number_to_hex_word(
                        startaddr + pc + high_byte + 1)
                instruction = instruction.replace(
                    "$hh", label_prefix + address)
            else:
                instruction = instruction.replace(
                    "hh", number_to_hex_byte(high_byte))

            byte_sequence.append(high_byte)

        if instruction_length == 2:
            pc += 1
            low_byte = bytes[pc]
            pc += 1
            high_byte = bytes[pc]

            # replace with new word
            instruction = instruction.replace(
                "hh", number_to_hex_byte(high_byte))
            instruction = instruction.replace(
                "ll", number_to_hex_byte(low_byte))

            # is the memory address within our own code?
            # then we should replace it with a label to that address
            absolute_address = (high_byte << 8) + low_byte
            if (absolute_address >= startaddr) & (absolute_address <= startaddr+end):
                instruction = instruction.replace("$", label_prefix)
                is_relative = True
                address = number_to_hex_word((high_byte << 8) + low_byte)

            # store the bytes - we might need them later
            byte_sequence.append(low_byte)
            byte_sequence.append(high_byte)

        line = {
            "a": memory_location_hex,
            "l": label,
            "b": byte_sequence,
            "i": instruction
        }

        # all relative/label data should get a new key so we can identify them
        # we need this when we cleanup unneeded labels
        if is_relative:
            line["rel"] = label_prefix + address

        if "ill" in opcode:
            line["ill"] = 1

        asm.append(line)
        pc = pc+1

    asm = remove_unused_labels(asm)
    return asm


opcodes = load_json("opcodes.json")
