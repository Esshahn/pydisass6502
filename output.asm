
.l1000    brk
.l1001    ora ($01,x)
.l1003    ora $01
.l1005    asl $01
.l1007    php
.l1008    ora #$01
.l100a    asl
.l100b    ora $1234
.l100e    asl $1234
.l1011    bpl $fe
.l1013    ora ($12),y
.l1015    ora $01,x
.l1017    asl $01,x
.l1019    clc
.l101a    ora $1234,y
.l101d    ora $1234,x
.l1020    asl $1234,x
.l1023    jsr $1234
.l1026    and ($12,x)
.l1028    bit $01
.l102a    and $01
.l102c    rol $01
.l102e    plp
.l102f    and #$12
.l1031    rol
.l1032    bit #$1234
.l1035    and $1234
.l1038    rol $1234
.l103b    bmi $fe
.l103d    and ($12),y
.l103f    and $01,x
.l1041    rol $01,x
.l1043    sec
.l1044    and $1234,y
.l1047    and $1234,x
.l104a    rol $1234,x
.l104d    rts
.l104e    eor ($12,x)
.l1050    eor $01
.l1052    lsr $01
.l1054    pha
.l1055    eor #$12
.l1057    lsr
.l1058    jmp $1234
.l105b    eor $1234
.l105e    lsr $1234
.l1061    bvc $fe
.l1063    eor ($12),y
.l1065    eor $01,x
.l1067    lsr $01,x
.l1069    cli
.l106a    eor $1234,y
.l106d    eor $1234,x
.l1070    lsr $1234,x
.l1073    rts
.l1074    adc ($12,x)
.l1076    adc $01
.l1078    ror $01
.l107a    pla
.l107b    adc #$12
.l107d    ror
.l107e    jmp ($1000)
.l1081    adc $1234
.l1084    ror $1234
.l1087    bvs $fe
.l1089    adc ($12),y
.l108b    adc $01,x
.l108d    ror $01,x
.l108f    sei
.l1090    adc $1234,y
.l1093    adc $1234,x
.l1096    ror $1234,x
.l1099    sta ($12,x)
.l109b    sty $01
.l109d    sta $01
.l109f    stx $01
.l10a1    dey
.l10a2    txa
.l10a3    sty $1234
.l10a6    sta #$1234
.l10a9    stx $1234
.l10ac    bcc $fe
.l10ae    sta ($12),y
.l10b0    sty $01,x
.l10b2    sta $01,x
.l10b4    stx $01,y
.l10b6    tya
.l10b7    sta $1234,y
.l10ba    txs
.l10bb    sta $1234,x
.l10be    ldy #$12
.l10c0    lda ($12,x)
.l10c2    ldx #$12
.l10c4    ldy $01
.l10c6    lda $01
.l10c8    ldx $01
.l10ca    tay
.l10cb    lda #$12
.l10cd    tax
.l10ce    ldy $1234
.l10d1    lda #$1234
.l10d4    ldx $1234
.l10d7    bcs $fe
.l10d9    lda ($12),y
.l10db    ldy $01,x
.l10dd    lda $01,x
.l10df    ldx $01,x
.l10e1    clv
.l10e2    lda $1234,y
.l10e5    tsx
.l10e6    ldy $1234,x
.l10e9    lda $1234,x
.l10ec    ldx $1234,x
.l10ef    cpy #$12
.l10f1    cmp ($12,x)
.l10f3    cpy $01
.l10f5    cmp $01
.l10f7    dec $01
.l10f9    iny
.l10fa    cmp #$12
.l10fc    dex
.l10fd    cpy $1234
.l1100    cmp $1234
.l1103    dec $1234
.l1106    bne $fe
.l1108    cmp ($12),y
.l110a    cmp $01,x
.l110c    dec $01,x
.l110e    cld
.l110f    cmp $1234,y
.l1112    cmp $1234,x
.l1115    dec $1234,x
.l1118    cpx #$12
.l111a    sbc ($12,x)
.l111c    cpx $01
.l111e    sbc $01
.l1120    inc $01
.l1122    inx
.l1123    sbc #$12
.l1125    nop
.l1126    cpx $1234
.l1129    sbc $1234
.l112c    inc $1234
.l112f    beq $fe
.l1131    sbc ($12),y
.l1133    sbc $01,x
.l1135    inc $01,x
.l1137    sed
.l1138    sbc $1234,y
.l113b    sbc $1234,x
.l113e    inc $1234,x