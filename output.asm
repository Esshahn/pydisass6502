; converted with pydisass6502 by awsm of mayday!

* = $1000

.l1000
           nop
           nop
           jmp .l1000
           nop
           nop
           bne .l1000
           nop
           bcc .l101b
           nop
           nop
           jmp .l101b
           lda $d020
           sta $d021
           sta .l101b
           nop

.l101b
           rts