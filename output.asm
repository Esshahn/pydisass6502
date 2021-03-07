; converted with pydisass6502 by awsm of mayday!

* = $1000

l1000
           ldy #$00

l1002
           sty $d020
           iny
           cpy #$08
           bne l1002
           inc $d021
           jmp l1000





           