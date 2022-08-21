; converted with pydisass6502 by awsm of mayday!

* = $0810

START       lda #$00                        ; 0810 a900
            sta $d020                       ; 0812 8d20d0 border color
            ldy #$0b                        ; 0815 a00b
_START1     lda s_A,y                       ; 0817 b92308
            sta $0400,y                     ; 081a 990004 start of screen memory
            dey                             ; 081d 88
            bpl _START1                     ; 081e 10f7
            jmp s_B                         ; 0820 4c2f08
s_A         !byte $08,$05,$0c,$0c,$0f,$20,$17,$0f,$12,$0c,$04,$21                   ; 0823 ..... .....!
s_B         lda $d020                       ; 082f ad20d0 border color
            sta $d021                       ; 0832 8d21d0 background color
            rts                             ; 0835 60
