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


def write_asm_file(filename, data):
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
    """ takes two hex bytes e.g. a8, ff and returns their int address e.g. 4096"""
    return (int(hh, 16) << 8) + int(ll, 16)


def print_bytes_as_hex(bytes):
    for byte in bytes:
        print(number_to_hex_byte(byte), end=" ")
    print()


def print_bytes_array(bytes_table):
    for byte in bytes_table:
        print(byte)


def addr_in_program(addr, startaddr, endaddr):
    return True if addr >= startaddr and addr <= startaddr + endaddr else False


def remove_unused_labels(asm):
    """
    goes through the code and checks which relative labels are
    in use, then adds a "show_label" key to each address that
    is a branching destination
    """

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


def save_program(byte_array, opcodes, outputfile):
    """formats the assembly code so it can be saved as a program"""

    program = "; converted with pydisass6502 by awsm of mayday!"
    program += "\n\n* = $" + number_to_hex_word(byte_array[0]["addr"]) + "\n\n"

    end = len(byte_array)
    startaddr = byte_array[0]["addr"]
    endaddr = startaddr + end

    i = 0
    while i < end:
        label = ""
        byte = byte_array[i]["byte"]

        if byte_array[i]["dest"]:
            label = "l" + number_to_hex_word(byte_array[i]["addr"])

        if byte_array[i]["data"]:
            ins = "!byte $"+byte

        if byte_array[i]["code"]:
            opcode = opcodes[byte]
            ins = opcode["ins"]
            length = get_instruction_length(ins)

            if length == 1:
                i += 1
                high_byte = byte_array[i]["byte"]
                ins = ins.replace("hh", high_byte)

            if length == 2:
                i += 1
                low_byte = byte_array[i]["byte"]
                i += 1
                high_byte = byte_array[i]["byte"]
                ins = ins.replace("hh", high_byte)
                ins = ins.replace("ll", low_byte)

        if label:
            program += "\n" + label + "\n"
        program += ins + "\n"
        i += 1

    write_asm_file(outputfile, program)


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


def check_abs_jumps():
    pass


def analyze(startaddr, bytes, opcodes):

    bytes_table = generate_byte_array(startaddr, bytes)
    branch_mnemonics = ["4c"]
    abs_address_mnemonics = ["ad", "8d"]

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
            instruction_length = get_instruction_length(opcode["ins"])

            # set code
            bytes_table[i]["code"] = 1

            if byte in branch_mnemonics:

                # we have a branching/jumping instruction, so we can't be sure anymore
                # about the following bytes being code
                is_code = 0

                destination_address = bytes_to_addr(
                    bytes_table[i+2]["byte"], bytes_table[i+1]["byte"])

                if addr_in_program(destination_address, startaddr, startaddr + end):
                    # the hhll address must be code, so we mark that entry in the array
                    table_pos = destination_address - startaddr
                    bytes_table[table_pos]["code"] = 1
                    bytes_table[table_pos]["dest"] = 1

            if byte in abs_address_mnemonics:
                destination_address = bytes_to_addr(
                    bytes_table[i+2]["byte"], bytes_table[i+1]["byte"])

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
save_program(byte_array, opcodes, args.outputfile)


"""
pseudo


einstiegspunkt definieren

alles code bis zu einem JMP oder RTS oder RTI
alle absoluten adressen (JMP, LDA, STA) sammeln
  code bis zum nächsten JMP oder RTS oder RTI muss wieder code sein


bytes mit weight:

"6a": {
  "data": 0,
  "code": 1,
}



ad 17 08 4c 18 08 10 8d 21 d0 60

jump = 0

ad - muss code
  -> normal umwandeln in code
  17 -> code
  08 -> code

ad - ist absolute, d.h. hhll muss Daten sein
  -> $hhdd als data setzen

4c - muss code (jmp)
  -> umwandeln in code
  18 -> code
  08 -> code
  $hhll (0818) muss code sein

10 - bereits als data gesetzt

8d -> muss code sein weil vorher beim jump definiert
  21 d0 -> ist adresse

60  - muss code sein
"""
