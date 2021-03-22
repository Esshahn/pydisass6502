# pyDisAssembler6502 

A simple 6502 machine language disassembler written in Python.

This disassembler is in a very early phase but already quite functional.
The main disadvantage of this disassembler compared to UI based programs is the lack of an interactive interface to define which sections are code and which are data.

## Usage

```
python3 disass.py inputfile.prg outputfile.asm
```

Takes a binary PRG file (e.g. a Commodore 64 program) and outputs the disassembled assembly listing.

For more information check out the article I wrote about it: 
https://www.awsm.de/blog/pydisass/
