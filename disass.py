#
#   PyDisAss6502 by Ingo Hinterding 2021
#   A Disassembler for 6502 machine code language into mnemonics
#
#   usage:
#   python disass.py inputfile outputfile
#   inputfile: the binary to disassemble, e.g. game.prg
#   outputfile: the filename for the exported source code, e.g. source.asm
#
#   example:
#   python3 disass.py game.prg source.asm
#

import json
import argparse
import os
import sys


def load_json(filename):
    with open(filename) as f:
        data = json.load(f)
    return data


def load_file(filename):
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

    startaddress = (bytecode[1] << 8) + bytecode[0]
    bytecode = bytecode[2:]  # remove first 2 bytes
    return(startaddress, bytecode)


def save_file(filename, data):
    f = open(filename, "w")
    f.write(data)
    f.close()


def number_to_hex_byte(number):
    return ("0" + hex(number)[2:])[-2:]


def hex_to_number(hex):
    return (int(hex, 16))


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
    return True if addr >= startaddr and addr <= endaddr else False


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


def convert_to_program(byte_array, opcodes, outputfile):
    """formats the assembly code so it can be saved as a program"""

    program = "; converted with pydisass6502 by awsm of mayday!"
    program += "\n\n* = $" + number_to_hex_word(byte_array[0]["addr"]) + "\n\n"
    label_prefix = "l"
    end = len(byte_array)
    startaddr = byte_array[0]["addr"]
    endaddr = startaddr + end
    previous_was_data = False           # used to collect data bytes in one line

    i = 0
    while i < end:
        # set defaults
        label = ""
        line_break = "\n"
        spaces = 12 * " "

        byte = byte_array[i]["byte"]

        if byte_array[i]["dest"]:
            label = label_prefix + number_to_hex_word(byte_array[i]["addr"])

        # mark everything as data that is not explicity set as code
        if not byte_array[i]["code"] or byte_array[i]["data"]:
            line_break = ""
            spaces = ""
            if not previous_was_data:
                ins = "!byte $"+byte
                previous_was_data = True
            else:
                ins = ", $"+byte

        if byte_array[i]["code"]:
            previous_was_data = False
            opcode = opcodes[byte]
            ins = opcode["ins"]
            length = get_instruction_length(ins)

            if length == 1:
                i += 1
                high_byte = byte_array[i]["byte"]
                int_byte = hex_to_number(high_byte)

                # if a relative instruction like BCC or BNE occurs
                if "rel" in opcode:
                    address = number_to_hex_word(
                        get_abs_from_relative(high_byte, startaddr+i))
                    ins = ins.replace("$hh", label_prefix + address)
                else:
                    ins = ins.replace("hh", number_to_hex_byte(int_byte))

            if length == 2:
                i += 1
                low_byte = byte_array[i]["byte"]
                i += 1
                high_byte = byte_array[i]["byte"]
                ins = ins.replace("hh", high_byte)
                ins = ins.replace("ll", low_byte)
                addr = bytes_to_addr(high_byte, low_byte)
                # turn absolute address into label if it is within the program code
                if addr_in_program(addr, startaddr, endaddr):
                    ins = ins.replace("$", label_prefix)

        if label:
            program += "\n\n" + label + "\n"
        program += spaces + ins + line_break
        i += 1

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
                "dest": 0,                 # is it the destination of a jump or branch instruction
                "code": 0,                  # is it marked as code?
                "data": 0                   # is it marked as data?
            }
        )
        pc += 1
    return bytes_table


def analyze(startaddr, bytes, opcodes):

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
        "99", "9d,",
        "ac", "ad", "ae",
        "b9", "bc", "bd", "be",
        "cc", "cd", "ce",
        "d9", "dd", "de",
        "ec", "ee", "ed",
        "f9", "fd", "fe"
    ]

    # our entrypoint is assumed to be code
    is_code = 1
    is_data = 0

    i = 0
    end = len(bytes_table)

    while i < end:
        byte = bytes_table[i]["byte"]
        opcode = opcodes[byte]

        if bytes_table[i]["data"]:
            is_data = 1

        if bytes_table[i]["code"]:
            is_code = 1

        if is_code:
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
                    bytes_table[i+1]["byte"], startaddr+i+1)

            if instruction_length == 2:
                # this is the absolute address
                destination_address = bytes_to_addr(
                    bytes_table[i+2]["byte"], bytes_table[i+1]["byte"])

            if byte in abs_branch_mnemonics or "rel" in opcode:
                if addr_in_program(destination_address, startaddr, startaddr + end):
                    # the hhll address must be code, so we mark that entry in the array
                    table_pos = destination_address - startaddr

                    bytes_table[table_pos]["code"] = 1
                    bytes_table[table_pos]["dest"] = 1

            if byte in abs_address_mnemonics:
                if addr_in_program(destination_address, startaddr, startaddr + end):
                    # the hhll address must be data, so we mark that entry in the array
                    table_pos = destination_address - startaddr
                    bytes_table[table_pos]["data"] = 1
                    bytes_table[table_pos]["dest"] = 1

            i += instruction_length

        i += 1

    print_bytes_array(bytes_table)
    return bytes_table

#
#
#   command line interface
#
#


# Create the parser
my_parser = argparse.ArgumentParser(
    description='disassembles a 6502 machine code binary file into assembly source.',
    epilog='Example: disass.py game.prg game.asm')

# Add the arguments
my_parser.add_argument('inputfile',
                       help='name of the input binary, e.g. game.prg'
                       )
my_parser.add_argument('outputfile',
                       help='name of the generated assembly file, e.g. game.asm.')

# Execute the parse_args() method
args = my_parser.parse_args()


#
#
#   file conversion
#
#

# load the opcodes list
opcodes = load_json("lib/opcodes.json")

# load prg
startaddress, bytes = load_file(args.inputfile)

print("\x1b[33;21m")
print_bytes_as_hex(bytes)


# turn bytes into asm code
byte_array = analyze(startaddress, bytes, opcodes)

# convert it into a readable format
convert_to_program(byte_array, opcodes, args.outputfile)
