demo = """
; lda #$00
A9                ; entry point. This must be code
00                ; byte is has to be part of the instruction
; sta $d020
8D                ; must be code as we haven't hit JMP or RTS or RTI yet
20                ; must be part of instruction
D0                ; must be part of instruction
; ldy #$0b
A0                ; must be code as we haven't hit JMP or RTS or RTI yet
0B                ; must be part of instruction

; loop
; lda hello,y     ; must still be code, but also mark position "hello" as data!
B9                ; must be part of instruction
23                ; must be part of instruction
08                ; must be part of instruction
; sta $0400,y
99                ; must be code as we haven't hit JMP or RTS or RTI yet
00                ; must be part of instruction
04                ; must be part of instruction
; dey
88                ; must be code as we haven't hit JMP or RTS or RTI yet
; bpl loop
10                ; must be code as we haven't hit JMP or RTS or RTI yet
f7                ; must be part of instruction, but also mark branch destination (loop) as code!
; jmp $82f
4C 2F 08                ; must be code as we haven't hit JMP or RTS or RTI yet

; hello
; !scr "hello world!"
08                ; must be data since it was defined by the absolute lda earlier
05 0C 0C 0F 20 17 0F 12 0C 04 21    ; no rules apply, so defaults to code = 0 and data = 0

AD 20 D0          ; lda $d020               ; load value from border color into A
8D 21 D0          ; sta $d021               ; store A into background color
60                ; rts
"""

hexdata = bytes(map(lambda s: int(s, 16), sum([line.split(';')[0].strip().split() for line in demo.splitlines()], [])))
open('demo.bin', 'wb').write(hexdata)
print(f'Wrote {len(hexdata)} bytes to demo.bin')
print('Now disassemble with: python disass.py -i demo.bin -o demo.asm -s 0x810')
