#!/usr/local/bin/python3

#
#   PyDisAss6502 by Ingo Hinterding 2021
#   A disassembler for converting 6502 machine code binaries into assembly code
#
#   https://github.com/Esshahn/pydisass64
#

import json
import argparse
import os
import string


def load_json(filename):
    with open(filename) as f:
        data = json.load(f)
    return data


def load_file(filename, start=None):
    """
    input: filename
    returns: startaddress (int), bytes
    """

    bytecode = []

    file = open(filename, "rb")
    byte = file.read(1)
    while byte:
        i = int.from_bytes(byte, byteorder='big')
        byte = file.read(1)
        bytecode.append(i)
    file.close()

    if start is None:
        startaddress = (bytecode[1] << 8) + bytecode[0]
        bytecode = bytecode[2:]  # remove first 2 bytes
    else:
        startaddress = start
    print("loading: " + filename)
    return (startaddress, bytecode)


def save_file(filename, data):
    f = open(filename, "w")
    f.write(data)
    f.close()
    print("saving: " + filename)


def number_to_hex_byte(number):
    return ("0" + hex(number)[2:])[-2:]


def hex_to_number(hex):
    return int(hex, 16)


def number_to_hex_word(number):
    return ("0" + hex(number)[2:])[-4:]


def bytes_to_addr(hh, ll):
    """ takes two hex bytes e.g. d0, 20 and returns their int address e.g. 53280"""
    return (int(hh, 16) << 8) + int(ll, 16)


def print_bytes_as_hex(bytes):
    for byte in bytes:
        print(number_to_hex_byte(byte), end=" ")
    print()


def print_bytes_array(bytes_table):
    for byte in bytes_table:
        print(byte)


def addr_in_program(addr, startaddr, endaddr):
    return True if addr >= startaddr and addr < endaddr else False


def get_abs_from_relative(byte, addr):
    """ 
    expects a byte and an absolute address and returns
    the absolute address for a relative branching
    e.g. for a BNE command
    """
    int_byte = hex_to_number(byte)

    if int_byte > 127:
        # substract (255 - highbyte) from current address
        address = addr - (255 - int_byte)
    else:
        # add highbyte to current address
        address = addr + int_byte + 1
    return address


def section_name(k):
    letters = []
    while True:
        letters.append(string.ascii_uppercase[k % 26])
        if k < 26:
            break
        k = (k // 26) - 1
    return ''.join(reversed(letters))


def convert_to_program(byte_array, opcodes, mapping, outputfile, hexdump=True):
    """formats the assembly code so it can be saved as a program"""

    program = "; converted with pydisass6502 by awsm of mayday!"
    program += "\n\n* = $" + number_to_hex_word(byte_array[0]["addr"]) + "\n\n"
    label_prefix = "s_"
    end = len(byte_array)
    startaddr = byte_array[0]["addr"]
    endaddr = startaddr + end

    # First generate a label for each dest
    if not byte_array[0]["dest"]:
        byte_array[0]["dest"] = "START"
    idx = -1
    for i in range(end):
        b = byte_array[i]
        if not b["dest"]:
            continue
        elif b["dest"] != -1:  # new section
            subidx = 0
            if not isinstance(b["dest"], str):
                idx += 1
                section = section_name(idx)
                b["dest"] = label_prefix + section
            else:
                section = b["dest"]
        else:
            subidx += 1
            b["dest"] = "_" + section + str(subidx)

    # Now generate logical lines of output
    i = 0
    while i < end:
        # start of line
        i0 = i
        comment = ""

        bi = byte_array[i]

        label = bi["dest"] or ""
        assert isinstance(label, str), f'dest not a string at i={i}, {bi[i]}'

        # mark everything as data that is not explicity set as code
        if not bi["code"] or bi["data"]:
            while True:
                i += 1
                if not (i < i0 + 16 and i < end):
                    break
                bi = byte_array[i]
                if bi["code"] or bi["dest"]:
                    break
            i -= 1
            ins = None
        else:
            opcode = opcodes[bi["byte"]]
            ins = opcode["ins"]
            length = get_instruction_length(ins)

            if length == 1:
                i += 1
                high_byte = byte_array[i]["byte"]
                int_byte = hex_to_number(high_byte)

                # if a relative instruction like BCC or BNE occurs
                if "rel" in opcode:
                    dest = byte_array[get_abs_from_relative(high_byte, i)]["dest"]
                    ins = ins.replace("$hh", dest)
                else:
                    ins = ins.replace("hh", number_to_hex_byte(int_byte))

            if length == 2:
                i += 1
                low_byte = byte_array[i]["byte"]
                i += 1
                high_byte = byte_array[i]["byte"]
                addr = bytes_to_addr(high_byte, low_byte)
                # turn absolute address into label if it is within the program code
                if addr_in_program(addr, startaddr, endaddr):
                    dest = byte_array[addr - startaddr]["dest"]
                    ins = ins.replace("$hhll", dest)
                else:
                    ins = ins.replace("hh", high_byte)
                    ins = ins.replace("ll", low_byte)

                if mapping:
                    # add comments from mapping file
                    for address in mapping["mapping"]:
                        if address["addr"] == number_to_hex_word(addr):
                            comment = address["comm"]

        i += 1
        bytes = [byte_array[j]['byte'] for j in range(i0, i)]
        if ins is None:  # data
            ins = "!byte " + ", ".join("$" + byte for byte in bytes)
        if hexdump:
            s = number_to_hex_word(i0 + startaddr) + "  " + "".join(bytes)
            comment = "{: <16s} {:s}".format(s + " ", comment)

        program += "{: <12s}{: <32s}; {:s}".format(label + " ", ins + " ", comment).rstrip(' ;') + "\n"

    save_file(outputfile, program)


def get_instruction_length(opcode):
    length = 0

    if "hh" in opcode:
        length += 1

    if "ll" in opcode:
        length += 1

    return length


def generate_byte_array(startaddr, bytes):
    """ generates an empty data array for later usage """
    bytes_table = []
    pc = 0
    end = len(bytes)

    # generate the object to host all analytics data
    while pc < end:
        byte = bytes[pc]
        bytes_table.append(
            {
                "addr": startaddr + pc,     # address of byte in memory
                "byte": number_to_hex_byte(byte),
                "dest": 0,                  # labeled symbol (str) or dest of jmp (+1) or rel branch (-1)
                "code": 0,                  # is it marked as code?
                "data": 0                   # is it marked as data?
            }
        )
        pc += 1
    return bytes_table


def analyze(startaddr, bytes, opcodes, entrypoints):

    bytes_table = generate_byte_array(startaddr, bytes)

    # JMP RTS RTI
    # used to default back to data for the following instructions
    default_to_data_after = ["4c", "60", "40"]

    # JMP JSR
    # used to identify code sections in the code
    abs_branch_mnemonics = ["4c", "20"]

    # LDA STA
    # used to identify data sections in the code
    abs_address_mnemonics = [
        "0d", "0e",
        "19", "1d", "1e",
        "2d", "2e",
        "39", "3d", "3e",
        "4d", "4e",
        "59", "5d", "5e",
        "6d", "6e",
        "79", "7d", "7e",
        "8c", "8d", "8e",
        "99", "9d",
        "ac", "ad", "ae",
        "b9", "bc", "bd", "be",
        "cc", "cd", "ce",
        "d9", "dd", "de",
        "ec", "ee", "ed",
        "f9", "fd", "fe"
    ]

    end = len(bytes_table)

    code_todo = set()
    code_done = set()

    if entrypoints:
        # add all override entry points from the json file before doing anything else
        for entrypoint in entrypoints["entrypoints"]:
            addr_int = hex_to_number(entrypoint["addr"])
            table_pos = addr_int - startaddr
            bytes_table[table_pos]["dest"] = entrypoint.get('label', 1)

            if entrypoint["mode"] == "code":
                bytes_table[table_pos]["code"] = 1
                bytes_table[table_pos]["data"] = 0
                code_todo.add(table_pos)

            if entrypoint["mode"] == "data":
                bytes_table[table_pos]["data"] = 1
                bytes_table[table_pos]["code"] = 0

    if not code_todo:
        bytes_table[0]["code"] = 1
        bytes_table[0]["data"] = 0
        code_todo.add(0)

    while code_todo:
        i = code_todo.pop()
        code_done.add(i)

        is_code = 1
        while i < end and is_code:
            byte = bytes_table[i]["byte"]
            opcode = opcodes[byte]

            # set code
            bytes_table[i]["code"] = 1

            instruction_length = get_instruction_length(opcode["ins"])

            if byte in default_to_data_after:
                # we have a branching/jumping instruction, so we can't be sure anymore
                # about the following bytes being code
                is_code = 0

            if "rel" in opcode:
                # if the instruction is relative, we have to calculate the
                # absolute branching address to add a label later below
                destination_address = get_abs_from_relative(
                    bytes_table[i + 1]["byte"], startaddr + i + 1)

            if instruction_length == 2:
                # this is the absolute address
                destination_address = bytes_to_addr(
                    bytes_table[i + 2]["byte"], bytes_table[i + 1]["byte"])

            if byte in abs_branch_mnemonics or "rel" in opcode:
                if addr_in_program(destination_address, startaddr, startaddr + end):
                    # the hhll address must be code, so we mark that entry in the array
                    table_pos = destination_address - startaddr
                    if table_pos not in code_done:
                        code_todo.add(table_pos)
                    bytes_table[table_pos]["dest"] = -1 if "rel" in opcode else 1

            if byte in abs_address_mnemonics:
                if addr_in_program(destination_address, startaddr, startaddr + end):
                    # the hhll address must be data, so we mark that entry in the array
                    table_pos = destination_address - startaddr
                    bytes_table[table_pos]["data"] = 1
                    bytes_table[table_pos]["dest"] = 1

            i += instruction_length

            i += 1

    return bytes_table

#
#
#   command line interface
#
#


# Create the parser
my_parser = argparse.ArgumentParser(
    description='disassembles a 6502 machine code binary file into assembly source.',
    epilog='Example: disass.py game.prg game.asm -e')

# Add the arguments
my_parser.add_argument('-i', '--input', required=True,
                       help='name of the input binary, e.g. game.prg')
my_parser.add_argument('-o', '--output',
                       help='name of the generated assembly file, e.g. game.asm.')
my_parser.add_argument('-s', '--startaddress', type=lambda x: int(x, 0), default=None,
                       help='starting offset, default to initial two bytes')
my_parser.add_argument('-nx', '--nohexdump', action='store_true',
                       help="Don't add PC/hex dump")
my_parser.add_argument('-e', '--entrypoints',
                       help="use entrypoints.json for code/data hints and labels")
my_parser.add_argument('-nc', '--nocomments', action='store_true',
                       help="do not add any comments to the output file")

# Execute the parse_args() method
args = my_parser.parse_args()


#
#
#   file conversion
#
#

dir_path = os.path.dirname(os.path.realpath(__file__))

print("\x1b[33;21m")

# load the opcodes list
opcodes = load_json(dir_path + "/lib/opcodes.json")

if args.output:
    output = args.output
else:
    output = str(args.input + ".asm")


if args.entrypoints:
    entrypoints = load_json(args.entrypoints)
    print("using entrypoints file: " + args.entrypoints)
else:
    entrypoints = {}

if args.nocomments:
    mapping = False
    print("omitting comments")
else:
    mapping = load_json(dir_path + "/lib/c64-mapping.json")
    print("using comments")


# load prg
startaddress = args.startaddress
if startaddress is None and 'startaddress' in entrypoints:
    startaddress = hex_to_number(entrypoints['startaddress'])
startaddress, bytes = load_file(args.input, startaddress)
# print_bytes_as_hex(bytes)

# turn bytes into asm code
byte_array = analyze(startaddress, bytes, opcodes, entrypoints)
# print_bytes_array(byte_array)


# convert it into a readable format
convert_to_program(byte_array, opcodes, mapping, output, hexdump=not args.nohexdump)
