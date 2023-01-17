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
from dataclasses import dataclass, asdict
from typing import Optional, Any


@dataclass(frozen=True)
class Opcode:
    op: str         # hex code, e.g. "6a"
    ins: str        # code template, "lda $hhll"
    arglen: int     # number of arg bytes, 0, 1 or 2
    mode: str       # addressing mode, "imm", "ind", "abs", "rel" or "impl"
    target: str     # target address implies "code", "data" or None (n/a)
    nofollow: bool  # following bytes not reached as code, e.g. "jmp", "rts", "rti"
    illegal: bool   # unsupported 6502 opcode, see https://www.masswerk.at/6502/6502_instruction_set.html


@dataclass
class ByteInfo:
    addr: int       # int address of byte in memory
    byte: str       # string byte, e.g. "6a"
    dest: Any = 0   # truthy means labelled with str (symbol), +1 if abs dest, or -1 if rel dest
    code: int = 0   # flag if marked as code
    data: int = 0   # flag if marked as data


@dataclass
class Symbol:
    addr: str
    symbol: Optional[str] = None
    mode: str = "data"
    loc: str = "external"
    count: int = 0
    comm: str = ""
    length: int = 0

    def __post_init__(self):
        try:
            self.addr and int(self.addr, 16)
        except ValueError:
            raise TypeError("Symbol 'addr' must be a hexadecimal address in", asdict(self))

    def asdict(self):
        return asdict(self)

    @classmethod
    def fromdict(kls, d):
        if isinstance(d.get("length"), str):
            d["length"] = int(d["length"], 16)
        return kls(**d)


def load_json(filename):
    with open(filename) as f:
        data = json.load(f)
    return data


def load_opcodes(filename):
    data = load_json(filename)
    opcodes = {}
    for op, (ins, *flags) in data.items():
        if op[1] == "0" and (int(op[0], 16) & 0x1):
            mode = "rel"
        elif "#" in ins:
            mode = "imm"
        elif '(' in ins:
            mode = "ind"
        elif 'hh' in ins:
            mode = "abs"
        else:
            mode = "impl"

        if "hhll" in ins:
            arglen = 2
        elif "hh" in ins:
            arglen = 1
        else:
            arglen = 0

        if "codeaddr" in flags or mode == "rel":
            target = "code"
        elif mode in ["ind", "abs"]:
            target = "data"
        else:
            target = None

        opcodes[op] = Opcode(
            op=op,
            ins=ins,
            arglen=arglen,
            mode=mode,
            nofollow="nofollow" in flags,
            illegal="!" in flags,
            target=target
        )

    return opcodes


def load_file(filename, start=None):
    """
    input: filename, optional start address
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
        # assume first two bytes encode start address, read and discard them
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


def hex_to_chr(hex, enc='ascii7', nonprintable='.'):
    """Convert a hex byte to a printable character, based on end scheme"""
    #TODO could be system-depednent like atascii, petscii, c64 screen codes etc
    x = hex_to_number(hex)
    if enc == 'ascii7':
        x &= 0x7f
    return chr(x) if 0x20 <= x < 0x7f else '.'


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


def find_dupes(xs):
    seen = set()
    dupes = set()
    for x in xs:
        dupes.add(x) if x in seen else seen.add(x)
    return dupes


def section_name(k):
    """map integer k=0, ... to Excel-style base26 A, B, ... AA, AB, ..."""
    letters = []
    while True:
        letters.append(string.ascii_uppercase[k % 26])
        if k < 26:
            break
        k = (k // 26) - 1
    return ''.join(reversed(letters))


def dump_stats(symbols, flt=lambda sym: True):
    """return json-formatted records for a filtered set of symbols"""
    syms = sorted(
        [s for s in symbols if s.count > 0 and flt(s)],
        key=lambda s: (len(s.addr), s.addr, s.symbol)
    )
    ds = [{k: v for (k, v) in s.asdict().items() if k != "comm"} for s in syms]
    return "[\n    " + ",\n    ".join(json.dumps(d) for d in ds) + "\n]"


def add_symbols(byte_array, symtab):
    """
    Adds symbols to byte_array and extends symbol table {addr => symbol}
    Generate a sequential symbol for each dest that doesn't have a user-supplied symbol.
    Absolute dests get an auto-generated section label like  __A__, __B__, ..., __AA__, __AB__, ...
    Relative branch dests get a label like _A_1, _A_2, ... within sections
    """
    if not byte_array[0].dest:
        byte_array[0].dest = "START"      # make sure start is labelled

    idx = -1                    # section count
    for i, b in enumerate(byte_array):
        if not b.dest:
            continue
        elif b.dest != -1:   # new section, either user or generated
            subidx = 0          # reset subsection count

            if isinstance(b.dest, str):
                section = b.dest
                continue

            idx += 1            # inc section counter
            section = section_name(idx)
            b.dest = "__" + section + "__"
        else:   # subsection
            subidx += 1
            b.dest = "_" + section + "_" + str(subidx)

        word = number_to_hex_word(b.addr)
        comm = symtab[word].comm if word in symtab else ""
        symtab[word] = Symbol(
            addr=word,
            symbol=b.dest,
            loc="internal",
            mode="data" if not b.code else "code",
            comm=comm
        )


def convert_to_program(byte_array, opcodes, symtab, outputfile, statsfile=None, hexdump=True):
    """formats the assembly code so it can be saved as a program"""

    program = "; converted with pydisass6502 by awsm of mayday!\n\n"
    program += "* = $" + number_to_hex_word(byte_array[0].addr) + "\n"
    end = len(byte_array)

    # create a cross-ref indexed by symbol to track usage stats
    symxref = {s.symbol: s for s in symtab.values() if s.symbol}

    # Now generate logical lines of output
    i = 0
    was_data = None
    add_break = False
    while i < end:
        i0 = i
        b = byte_array[i]
        label = b.dest or ""
        pc = number_to_hex_word(b.addr)     # hex address of this line
        sym = symtab.get(pc)                    # symbol for this line?
        comment = sym.comm if sym else ""    # comment for this line?

        is_data = not b.code   # mark everything as data that is not explicity set as code

        if add_break or is_data != was_data:
            program += '\n'

        add_break = False
        was_data = is_data

        if is_data:
            # consume a block of data up to length or 16 bytes
            # then output in groups of up to 16 bytes

            n = sym.length if sym else 16
            xs = []
            while True:
                xs.append(b.byte)
                i += 1
                if (n and len(xs) == n) or i == end:
                    break
                b = byte_array[i]
                if b.code or b.dest:
                    break

            if label or comment:
                s = f"{label}:"
                if comment:
                    s += "  ; " + comment
                program += s + "\n"

            for j in range(0, len(xs), 16):
                chunk = xs[j: j + 16]
                pc = number_to_hex_word(byte_array[i0 + j].addr)
                bytelist = ",".join("$" + x for x in chunk)
                s = f"    !byte {bytelist: <64s}"
                if hexdump:
                    chrs = "".join(map(hex_to_chr, chunk))
                    s += f"  ; {pc} {chrs}"
                program += s + "\n"

            continue

        # otherwise build an instruction line
        opcode = opcodes[b.byte]
        ins = opcode.ins
        target = None   # track a target we want stats for

        if opcode.arglen == 1:
            i += 1
            high_byte = byte_array[i].byte
            # if a relative instruction like BCC or BNE occurs
            if opcode.mode == "rel":
                # don't track stats on relative dests
                dest = byte_array[get_abs_from_relative(high_byte, i)].dest
                ins = ins.replace("$hh", dest)
            else:
                imm = opcode.mode == "imm"
                if not imm and high_byte in symtab:
                    sym = symtab[high_byte]
                    target = sym.symbol
                    ins = ins.replace("$hh", target)
                    if not comment and sym.comm:
                        comment = '. ' + sym.comm
                else:
                    ins = ins.replace("hh", high_byte)
                    target = ("#" if imm else "") + "$" + high_byte

        if opcode.arglen == 2:
            i += 1
            low_byte = byte_array[i].byte
            i += 1
            high_byte = byte_array[i].byte
            hhll = high_byte + low_byte
            if hhll in symtab:
                sym = symtab[hhll]
                target = sym.symbol
                if not comment and sym.comm:
                    comment = '. ' + sym.comm
            else:
                target = "$" + hhll
            ins = ins.replace("$hhll", target)

        i += 1
        add_break = opcode.nofollow

        if target:
            if target not in symxref:
                symxref[target] = Symbol("" if target[0] == "#" else target[1:], target)
            symxref[target].count += 1

        if hexdump:
            bytes = "".join([byte_array[j].byte for j in range(i0, i)])
            comment = f"{pc} {bytes: <6s}  {comment}"

        if b.data:
            comment += " !! referenced as both code and data"

        if label:
            label += ':'
        s = f"{label: <11s} {ins: <32s}"
        if comment:
            s += " ; " + comment
        program += s + "\n"

        # check for labels pointing into instruction args
        for j in range(i0 + 1, i):
            b = byte_array[j]
            if b.dest:
                program += "{0} = ${1}  ; {2}\n".format(
                    b.dest,
                    number_to_hex_word(b.addr),
                    "misaligned code?" if b.code else 'self-modifying code?'
                )

    if statsfile:
        symbols = list(symxref.values())
        s = "Hex constants\n\n"
        s += dump_stats(symbols, lambda s: s.addr == "")
        s += "\n\nUnknown page zero entrypoints\n\n"
        s += dump_stats(symbols, lambda s: s.symbol.startswith('$') and len(s.addr) == 2)
        s += "\n\nUnknown page one+ entrypoints\n\n"
        s += dump_stats(symbols, lambda s: s.symbol.startswith('$') and len(s.addr) == 4)
        s += "\n\nInternal entrypoints\n\n"
        s += dump_stats(symbols, lambda s: s.symbol.startswith('_'))
        s += "\n\nKnown symbols\n\n"
        s += dump_stats(symbols, lambda s: s.symbol[0] not in "#$_")
        s += "\n"
        save_file(statsfile, s)

    save_file(outputfile, program)


def generate_byte_array(startaddr, bytes):
    """ generates an empty data array for later usage """
    bytes_table = []
    pc = 0
    end = len(bytes)

    # generate the object to host all analytics data
    while pc < end:
        byte = bytes[pc]
        bytes_table.append(ByteInfo(
            addr=startaddr + pc,
            byte=number_to_hex_byte(byte),
            dest=0,
            code=0,
            data=0
        ))
        pc += 1
    return bytes_table


def analyze(startaddr, bytes, opcodes, entries):

    bytes_table = generate_byte_array(startaddr, bytes)
    end = len(bytes_table)

    code_todo = set()
    code_done = set()

    # add all override entry points from the json file before doing anything else
    for sym in entries:
        table_pos = hex_to_number(sym.addr) - startaddr
        bytes_table[table_pos].dest = sym.symbol or 1  # either string or absolute flag

        if sym.mode == "code":
            bytes_table[table_pos].code = 1
            bytes_table[table_pos].data = 0
            code_todo.add(table_pos)

        if sym.mode == "data":
            bytes_table[table_pos].data = 1
            bytes_table[table_pos].code = 0

    if not code_todo:
        bytes_table[0].code = 1
        bytes_table[0].data = 0
        code_todo.add(0)

    while code_todo:
        i = code_todo.pop()
        code_done.add(i)

        is_code = 1
        while i < end and is_code:
            opcode = opcodes[bytes_table[i].byte]

            # set code
            bytes_table[i].code = 1

            if opcode.nofollow:
                # we have a branching/jumping instruction, so we can't be sure anymore
                # about the following bytes being code
                is_code = 0

            if opcode.mode == "rel":
                # if the instruction is relative, we have to calculate the
                # absolute branching address to add a label later below
                destination_address = get_abs_from_relative(
                    bytes_table[i + 1].byte, startaddr + i + 1)
            elif opcode.arglen == 1:
                # page zero abs address
                destination_address = hex_to_number(bytes_table[i+1].byte)
            elif opcode.arglen == 2:
                # this is the absolute address
                destination_address = bytes_to_addr(
                    bytes_table[i + 2].byte,
                    bytes_table[i + 1].byte
                )

            if opcode.target and addr_in_program(destination_address, startaddr, startaddr + end):
                table_pos = destination_address - startaddr
                b = bytes_table[table_pos]
                if not b.dest or b.dest == -1:
                    b.dest = -1 if opcode.mode == "rel" else 1
                if opcode.target == "code":
                    if table_pos not in code_done:
                        code_todo.add(table_pos)
                else:
                    b.data = 1

            i += opcode.arglen + 1

    return bytes_table


#
#
#   command line interface
#
#
if __name__ == '__main__':

    dir_path = os.path.dirname(os.path.realpath(__file__))

    # Create the parser
    my_parser = argparse.ArgumentParser(
        description='disassembles a 6502 machine code binary file into assembly source.',
        epilog='Example: disass.py game.prg game.asm -e')

    # Add the arguments
    my_parser.add_argument('-i', '--input', required=True,
                           help='name of the input binary, e.g. game.prg')
    my_parser.add_argument('-o', '--output',
                           help='name of the generated assembly file, e.g. game.asm')
    my_parser.add_argument('-c', '--counts', default=None,
                           help='filename to dump usage stats on external addressses and constants, e.g. game.stats')
    my_parser.add_argument('-s', '--startaddress', type=lambda x: int(x, 0), default=None,
                           help='starting offset, default to initial two bytes')
    my_parser.add_argument('-nx', '--nohexdump', action='store_true',
                           help="Don't add PC/hex dump")
    my_parser.add_argument('-e', '--entrypoints',
                           help="use entrypoints.json for code/data hints, symbols and comments")
    my_parser.add_argument('-m', '--mapping', default=dir_path + "/lib/c64-mapping.json",
                           help="use given mapping.json for OS comments")
    my_parser.add_argument('-nc', '--nocomments', action='store_true',
                           help="do not add any comments to the output file")

    # Execute the parse_args() method
    args = my_parser.parse_args()

    #
    #
    #   file conversion
    #
    #

    # load the opcodes list
    opcodes = load_opcodes(dir_path + "/lib/opcodes.json")

    if args.output:
        output = args.output
    else:
        output = str(args.input + ".asm")

    if args.nocomments:
        symbols = []
        print("no mapping file")
    else:
        print("using mapping file", args.mapping)
        symbols = [
            Symbol.fromdict(d)
            for d in load_json(args.mapping)["mapping"]
        ]

    if args.entrypoints:
        print("reading entrypoints file: " + args.entrypoints)
        metadata = load_json(args.entrypoints)
        entrypoints = [
            Symbol.fromdict(d)
            for d in metadata["entrypoints"]
        ]
    else:
        metadata = {}
        entrypoints = []

    # load prg
    startaddress = args.startaddress
    if startaddress is None and 'startaddress' in metadata:
        startaddress = hex_to_number(metadata['startaddress'])
    startaddress, bytes = load_file(args.input, startaddress)
    # print_bytes_as_hex(bytes)

    internal_entries = []
    for sym in entrypoints:
        addr_int = hex_to_number(sym.addr)
        if sym.symbol and addr_in_program(addr_int, startaddress, startaddress + len(bytes)):
            sym.loc = "internal"
            internal_entries.append(sym)
        # also copy everything for the symbol table
        symbols.append(sym)

    dupes = find_dupes([sym.addr for sym in symbols])
    if dupes:
        print(f"Warning: duplicate addr {', '.join(sorted(dupes))}")
    dupes = find_dupes([sym.symbol for sym in symbols if sym.symbol])
    if dupes:
        print(f"Warning: duplicate symbols {', '.join(sorted(dupes))}")

    symtab = {sym.addr: sym for sym in symbols}

    # turn bytes into asm code
    byte_array = analyze(startaddress, bytes, opcodes, internal_entries)

    # generate human-friendly symbols
    add_symbols(byte_array, symtab)

    # convert it into a readable format
    convert_to_program(byte_array, opcodes, symtab, output, args.counts, hexdump=not args.nohexdump)
