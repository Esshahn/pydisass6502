;     6502 instructions
;     All legal mnemonics sorted by their opcode value
;     
;     created by awsm of mayday! in 2021
;     https://www.awsm.de


* = $1000

      ; 0x
      BRK               ; 00
      ORA ($01,x)       ; 01
      ORA $01           ; 05
      ASL $01           ; 06
      PHP               ; 08
      ORA #$01          ; 09
      ASL               ; 0a
      ORA $1234         ; 0d
      ASL $1234         ; 0e

      ; 1x
      BPL *             ; 10
      ORA ($12),y       ; 11     
      ORA $01,x	      ; 15
      ASL $01,x         ; 16
      CLC 	            ; 18
      ORA $1234,y	      ; 19
      ORA $1234,x	      ; 1d
      ASL $1234,x       ; 1e

      ; 2x
      JSR $1234	      ; 20
      AND ($12,x)	      ; 21
      BIT $01	      ; 24
      AND $01	      ; 25
      ROL $01	      ; 26
      PLP 	            ; 28
      AND #$12	      ; 29
      ROL               ; 2a
      BIT $1234	      ; 2c
      AND $1234	      ; 2d
      ROL $1234         ; 2e

      ; 3x
      BMI * 	      ; 30
      AND ($12),y	      ; 31
      AND $01,x	      ; 35
      ROL $01,x	      ; 36
      SEC 	            ; 38
      AND $1234,y	      ; 39
      AND $1234,x	      ; 3d
      ROL $1234,x       ; 3e

      ; 4x
      RTI 	            ; 40
      EOR ($12,x)	      ; 41
      EOR $01	      ; 45
      LSR $01	      ; 46
      PHA 	            ; 48
      EOR #$12	      ; 49
      LSR               ; 4a
      JMP $1234	      ; 4c
      EOR $1234	      ; 4d
      LSR $1234         ; 4e

      ; 5x
      BVC *	            ; 50
      EOR ($12),y	      ; 51
      EOR $01,x	      ; 55
      LSR $01,x	      ; 56
      CLI 	            ; 58
      EOR $1234,y	      ; 59
      EOR $1234,x	      ; 5d
      LSR $1234,x       ; 5e

      ; 6x	
      RTS 	            ; 60
      ADC ($12,x)	      ; 61
      ADC $01	      ; 65
      ROR $01	      ; 66
      PLA 	            ; 68
      ADC #$12	      ; 69
      ROR               ; 6a
      JMP ($1000)	      ; 6c
      ADC $1234	      ; 6d
      ROR $1234         ; 6e

      ; 7x	
      BVS *	            ; 70
      ADC ($12),y	      ; 70
      ADC $01,x	      ; 75
      ROR $01,x	      ; 76
      SEI 	            ; 78
      ADC $1234,y	      ; 79
      ADC $1234,x	      ; 7d
      ROR $1234,x       ; 7e

      ; 8x	
      STA ($12,x)	      ; 81
      STY $01	      ; 84
      STA $01	      ; 85
      STX $01	      ; 86
      DEY 	            ; 88
      TXA 	            ; 8a
      STY $1234	      ; 8c
      STA $1234	      ; 8d
      STX $1234         ; 8e

      ; 9x	
      BCC *             ; 90
      STA ($12),y	      ; 91
      STY $01,x	      ; 94
      STA $01,x	      ; 95
      STX $01,y	      ; 96
      TYA 	            ; 98
      STA $1234,y	      ; 99
      TXS 	            ; 9a
      STA $1234,x       ; 9d

      ; Ax	
      LDY #$12	      ; a0
      LDA ($12,x)	      ; a1
      LDX #$12	      ; a2
      LDY $01	      ; a4
      LDA $01	      ; a5
      LDX $01	      ; a6
      TAY 	            ; a8
      LDA #$12	      ; a9
      TAX 	            ; aa
      LDY $1234	      ; ac
      LDA $1234	      ; ad
      LDX $1234         ; ae

      ; Bx
      BCS *             ; b0
      LDA ($12),y	      ; b1
      LDY $01,x	      ; b4
      LDA $01,x	      ; b5
      LDX $01,y	      ; b6
      CLV 	            ; b8
      LDA $1234,y	      ; b9
      TSX 	            ; ba
      LDY $1234,x	      ; bc
      LDA $1234,x	      ; bd
      LDX $1234,y       ; be

      ; Cx
      CPY #$12	      ; c0
      CMP ($12,x)	      ; c1
      CPY $01	      ; c4
      CMP $01	      ; c5
      DEC $01	      ; c6
      INY 	            ; c8
      CMP #$12	      ; c9
      DEX 	            ; ca
      CPY $1234	      ; cc
      CMP $1234	      ; cd
      DEC $1234         ; ce

      ; Dx	
      BNE *	            ; d0
      CMP ($12),y	      ; d1
      CMP $01,x	      ; d5
      DEC $01,x	      ; d6
      CLD 	            ; d8
      CMP $1234,y	      ; d9
      CMP $1234,x	      ; dd
      DEC $1234,x       ; de

      ; Ex
      CPX #$12	      ; e0
      SBC ($12,x)	      ; e1
      CPX $01	      ; e4
      SBC $01	      ; e5
      INC $01	      ; e6
      INX 	            ; e8
      SBC #$12	      ; e9
      NOP 	            ; ea
      CPX $1234	      ; ec
      SBC $1234	      ; ed
      INC $1234         ; ee

      ; Fx
      BEQ *	            ; f0
      SBC ($12),y	      ; f1
      SBC $01,x	      ; f5
      INC $01,x	      ; f6
      SED 	            ; f8
      SBC $1234,y	      ; f9
      SBC $1234,x	      ; fd
      INC $1234,x       ; fe
