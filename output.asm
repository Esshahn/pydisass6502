; converted with pydisass6502 by awsm of mayday!

* = $0801
            anc #$08                ; $0b, $08
            isb ($07,x)             ; $e3, $07
            shx $3032,y             ; $9e, $32, $30
            rol $31,x
            brk
            brk
            brk
            lda #$00
            sta $d020
            sta $d021
            ldy #$0c
            ldx #$00

l0819
            lda l0824,x
            sta $0400,x
            inx
            dey
            bne l0819
            rts


l0824
            php
            ora $0c
            nop $200f               ; $0c, $0f, $20
            slo $0f,x               ; $17, $0f
            jam                     ; $12
            nop $2104               ; $0c, $04, $21