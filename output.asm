
    brk
    ora ($01,x)
    ora $01
    asl $01
    php
    ora #$01
    asl
    ora $1234
    asl $1234

.l1011
    bpl .l1011
    ora ($12),y
    ora $01,x
    asl $01,x
    clc
    ora $1234,y
    ora $1234,x
    asl $1234,x
    jsr $1234
    and ($12,x)
    bit $01
    and $01
    rol $01
    plp
    and #$12
    rol
    bit #$1234
    and $1234
    rol $1234

.l103b
    bmi .l103b
    and ($12),y
    and $01,x
    rol $01,x
    sec
    and $1234,y
    and $1234,x
    rol $1234,x
    rts
    eor ($12,x)
    eor $01
    lsr $01
    pha
    eor #$12
    lsr
    jmp $1234
    eor $1234
    lsr $1234

.l1061
    bvc .l1061
    eor ($12),y
    eor $01,x
    lsr $01,x
    cli
    eor $1234,y
    eor $1234,x
    lsr $1234,x
    rts
    adc ($12,x)
    adc $01
    ror $01
    pla
    adc #$12
    ror
    jmp ($1000)
    adc $1234
    ror $1234

.l1087
    bvs .l1087
    adc ($12),y
    adc $01,x
    ror $01,x
    sei
    adc $1234,y
    adc $1234,x
    ror $1234,x
    sta ($12,x)
    sty $01
    sta $01
    stx $01
    dey
    txa
    sty $1234
    sta #$1234
    stx $1234

.l10ac
    bcc .l10ac
    sta ($12),y
    sty $01,x
    sta $01,x
    stx $01,y
    tya
    sta $1234,y
    txs
    sta $1234,x
    ldy #$12
    lda ($12,x)
    ldx #$12
    ldy $01
    lda $01
    ldx $01
    tay
    lda #$12
    tax
    ldy $1234
    lda #$1234
    ldx $1234

.l10d7
    bcs .l10d7
    lda ($12),y
    ldy $01,x
    lda $01,x
    ldx $01,x
    clv
    lda $1234,y
    tsx
    ldy $1234,x
    lda $1234,x
    ldx $1234,x
    cpy #$12
    cmp ($12,x)
    cpy $01
    cmp $01
    dec $01
    iny
    cmp #$12
    dex
    cpy $1234
    cmp $1234
    dec $1234

.l1106
    bne .l1106
    cmp ($12),y
    cmp $01,x
    dec $01,x
    cld
    cmp $1234,y
    cmp $1234,x
    dec $1234,x
    cpx #$12
    sbc ($12,x)
    cpx $01
    sbc $01
    inc $01
    inx
    sbc #$12
    nop
    cpx $1234
    sbc $1234
    inc $1234

.l112f
    beq .l112f
    sbc ($12),y
    sbc $01,x
    inc $01,x
    sed
    sbc $1234,y
    sbc $1234,x
    inc $1234,x