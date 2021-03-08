from disassembler import *


# load prg
bytes = load_file("test.prg")

# turn bytes into asm code
startaddr = 4096
assembly = bytes_to_asm(bytes, startaddr, opcodes)

# convert it into a readable format
display_full_assembly(assembly)

program = create_program(assembly)

# save as file
write_asm_file("output.asm", program)
