# byoc_logisim
byoc from Richard Whipple's book using Logisim-evolution and a python assembler

CPU Specification is based on a CPU containing:

    * Program Control Unit (PCU)
    * Memory Unit (MU)
    * Arithmetic Logic Unit (ALU)
    * Clock Unit (CU)

I run the assembler like this:
```

[nick@Nicks-Mac-mini.local ~/Desktop/logisim]$ python3 assembler_v0.1.py sieve100.asm
0000 d0050 11010000000001010000 start:     call clr_scr    ; Clear screen
0001 08000 00001000000000000000            mvi  d,hi(0000) ; Display title
0002 0c000 00001100000000000000            mvi  e,lo(0000)
0003 d0052 11010000000001010010            call mout
0004 d004e 11010000000001001110            call new_line   ; Skip a line
0005 d004e 11010000000001001110            call new_line   ; Skip a line
0006 08000 00001000000000000000            mvi  d,hi(001c)
0007 0c01c 00001100000000011100            mvi  e,lo(001c)
0008 d0052 11010000000001010010            call mout
0009 d004e 11010000000001001110            call new_line   ; Skip a line
000a d004e 11010000000001001110            call new_line
000b 14064 00010100000001100100            mvi  l,100      ; HL is the pointer to DRAM
000c 10000 00010000000000000000            mvi  h,0
000d 0c064 00001100000001100100            mvi  e,100      ; E is max value
000e 58060 01011000000001100000 loop0:     mov  m,e        ; Store value
000f 95100 10010101000100000000            dcr  l          ; Decrement address
0010 8d100 10001101000100000000            dcr  e          ; Decrement value
0011 a21fd 10100010000111111101            bnz  loop0      ; If value not zero, do again
0012 04002 00000100000000000010            mvi  c,2        ; Start with 2 as base value
0013 54020 01010100000000100000 loop1:     mov  l,c        ; Set DRAM pointer to address of base value
0014 999c0 10011001100111000000            or   m,m        ; Has the base value been stricken?
0015 a0005 10100000000000000101            bz   next_n     ; If so, move on to next value to strike
0016 94020 10010100000000100000 loop2:     add  l,c        ; Otherwise, compute address of multiple
0017 18000 00011000000000000000            mvi  m,0        ; Zero location to strike
0018 34465 00110100010001100101            cpi  l,101      ; Have multiples 100 or less been stricken?
0019 a41fd 10100100000111111101            bc   loop2      ; If not, strike another
001a 85000 10000101000000000000 next_n:    inc  c          ; Otherwise, next base value
001b 2440a 00100100010000001010            cpi  c,10       ; Reached 10?
001c a21f7 10100010000111110111            bnz  loop1      ; If not, do multiple zeroing again
001d 14002 00010100000000000010            mvi  l,2        ; Start at location 2
001e 10000 00010000000000000000            mvi  h,0
001f 999c0 10011001100111000000 loop3:     or   m,m        ; Is value zero?
0020 a0006 10100000000000000110            bz   dspl_next  ; If so, display next value
0021 4c0c0 01001100000011000000            mov  e,m        ; Move prime to DE
0022 08000 00001000000000000000            mvi  d,0
0023 d002a 11010000000000101010 cont2:     call dout       ; Display DE
0024 00020 00000000000000100000            mvi  b,32
0025 d0047 11010000000001000111            call bout
0026 95000 10010101000000000000 dspl_next: inc  l          ; Pointer to next n
0027 34464 00110100010001100100            cpi  l,100      ; Past last prime?
0028 a41f7 10100100000111110111            bc   loop3      ; If not, do again
0029 f0029 11110000000000101001 self:      jmp  self       ; Done
002a 97000 10010111000000000000 dout:      push l          ; Save HL
002b 93000 10010011000000000000            push h
002c 14000 00010100000000000000            mvi  l,0        ; Zero suppression flag
002d 00000 00000000000000000000            mvi  b,0        ; Zero hundreds counter
002e 04064 00000100000001100100            mvi  c,100      ; Pass position bias (100) to convert subroutine
002f d0039 11010000000000111001            call cnvrt      ; Display hundreds digit
0030 00000 00000000000000000000            mvi  b,0        ; Zero tens counter
0031 0400a 00000100000000001010            mvi  c,10       ; Pass position bias (10) to convert sub
0032 d0039 11010000000000111001            call cnvrt      ; Display tens digit
0033 40060 01000000000001100000            mov  b,e        ; Display remainder as ones digit
0034 20030 00100000000000110000            adi  b,48       ; Add ASCII bias
0035 d0047 11010000000001000111            call bout       ; Display ones digit on TTY
0036 93800 10010011100000000000            pop  h          ; Restore HL
0037 97800 10010111100000000000            pop  l
0038 c0000 11000000000000000000            ret             ; Done-return to calling routine
0039 100ff 00010000000011111111 cnvrt:     mvi  h,255      ; Set zero suppress auxillary flag to -1
003a 91000 10010001000000000000 cnvrt_0:   inc  h          ; Increment it
003b 8c220 10001100001000100000            sub  e,c        ; Subtract position bias from DE
003c 88300 10001000001100000000            sbb  d,b
003d a61fd 10100110000111111101            bnc  cnvrt_0    ; If result positive, subtract bias again
003e 8c020 10001100000000100000            add  e,c        ; Otherwise, add bias back to DE
003f 88100 10001000000100000000            adc  d,b
0040 904a0 10010000010010100000            cmp  h,l        ; Is result zero?
0041 a2002 10100010000000000010            bnz  cnvrt_1    ; If not, display it
0042 c0000 11000000000000000000            ret             ; Otherwise, just return displaying
0043 95100 10010101000100000000 cnvrt_1:   dcr  l          ; Turn off zero suppression
0044 40080 01000000000010000000            mov  b,h        ; Add ASCII bias then display it
0045 20030 00100000000000110000            adi  b,48
0046 f0047 11110000000001000111            jmp  bout
0047 9f000 10011111000000000000 bout:      push a          ; Save A
0048 9f904 10011111100100000100 bout_0:    inp  a,4        ; Is TTY busy
0049 3d880 00111101100010000000            ani  a,128
004a a21fe 10100010000111111110            bnz  bout_0     ; If so, wait
004b 83105 10000011000100000101            out  5,b        ; Otherwise, display character
004c 9f800 10011111100000000000            pop  a          ; Restore A
004d c0000 11000000000000000000            ret             ; Return to calling routine
004e 0000d 00000000000000001101 new_line:  mvi  b,13       ; Display new line character
004f f0047 11110000000001000111            jmp  bout
0050 0000c 00000000000000001100 clr_scr:   mvi  b,12       ; Display clear screen character
0051 f0047 11110000000001000111            jmp  bout
0052 60000 01100000000000000000 mout:      lrom b          ; Get first message byte from DROM
0053 81900 10000001100100000000            or   b,b        ; Is it zero?
0054 a0005 10100000000000000101            bz   mout_done  ; If so, done
0055 d0047 11010000000001000111            call bout       ; Otherwise, display it
0056 8d000 10001101000000000000            inc  e          ; Increment DE
0057 89200 10001001001000000000            inz  d
0058 f0052 11110000000001010010            jmp  mout       ; Do again
0059 c0000 11000000000000000000 mout_done: ret

ROM(540): d0050 08000 0c000 d0052 d004e d004e 08000 0c01c d0052 d004e d004e 14064 10000 0c064 58060 95100 8d100 a21fd 04002 54020 999c0 a0005 94020 18000 34465 a41fd 85000 2440a a21f7 14002 10000 999c0 a0006 4c0c0 08000 d002a 00020 d0047 95000 34464 a41f7 f0029 97000 93000 14000 00000 04064 d0039 00000 0400a d0039 40060 20030 d0047 93800 97800 c0000 100ff 91000 8c220 88300 a61fd 8c020 88100 904a0 a2002 c0000 95100 40080 20030 f0047 9f000 9f904 3d880 a21fe 83105 9f800 c0000 0000d f0047 0000c f0047 60000 81900 a0005 d0047 8d000 89200 f0052 c0000 
DROM(48): 53 69 65 76 65 20 6f 66 20 45 72 61 74 6f 73 74 68 65 6e 65 73 20 2d 20 31 30 30 00 46 75 6e 6b 65 65 20 4d 75 6e 6b 65 65 20 4d 46 45 52 0a 00
```