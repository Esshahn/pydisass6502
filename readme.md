# pyDisAss6502 

A simple 6502 machine language disassembler written in Python.

This disassembler is in a very early phase but already quite functional.
The main disadvantage of this disassembler compared to UI based programs is the lack of an interactive interface to define which sections are code and which are data.

I've yet to implement a "data guessing" algorhythm. For now, pyDisAss6502 considers everything to be code (just like the disassembler in the Vice emulator for example). As a little convenience feature, all illegal opcodes are also referenced as a comment with the byte values. This usually is a good hint for data sections. 

To Do:
* implement all illegal opcodes
* guess data areas
