; converted with pydisass6502 by awsm of mayday!

* = $0810

START       lda #$00                        ; 0810 a900    
            sta BRDCLR                      ; 0812 8d20d0  border color
            ldy #$0b                        ; 0815 a00b    
_START_1    lda __A__,y                     ; 0817 b92308  
            sta SCREEN,y                    ; 081a 990004  start of screen memory
            dey                             ; 081d 88      
            bpl _START_1                    ; 081e 10f7    
            jmp __B__                       ; 0820 4c2f08  
__A__
    !byte $08,$05,$0c,$0c,$0f,$20,$17,$0f,$12,$0c,$04,$21                   ; 0823 ..... .....!    
__B__       lda BRDCLR                      ; 082f ad20d0  border color
            sta BGCLR                       ; 0832 8d21d0  background color
            rts                             ; 0835 60      
