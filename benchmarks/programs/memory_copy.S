// Memory copy benchmark
// This benchmark tests memory throughput and cache behavior
// Compatible with QtRvSim integrated assembler

.globl _start

// System call numbers
.equ __NR_exit, 93

// Memory layout
.equ SRC_BUFFER, 0x1000
.equ DST_BUFFER, 0x2000

.text
.org 0x200

_start:
    // Initialize stack pointer
    li sp, 0x8000

    // Initialize source buffer with test pattern
    li a0, SRC_BUFFER
    li a1, 256            // 256 words = 1KB
    jal ra, init_buffer

    // Copy buffer multiple times to stress cache
    li s0, 10             // iterations

copy_loop:
    beqz s0, done

    li a0, DST_BUFFER
    li a1, SRC_BUFFER
    li a2, 256            // 256 words

    jal ra, memcpy_words

    addi s0, s0, -1
    j copy_loop

done:
    // Exit program
    addi a7, zero, __NR_exit
    addi a0, zero, 0
    ecall

// init_buffer: Initialize buffer with incrementing values
// Arguments: a0 = buffer pointer, a1 = word count
init_buffer:
    li t0, 0              // counter

init_loop:
    bge t0, a1, init_done
    slli t1, t0, 2        // offset
    add t2, a0, t1        // address
    sw t0, 0(t2)          // store counter value
    addi t0, t0, 1
    j init_loop

init_done:
    ret

// memcpy_words: Copy words from source to destination
// Arguments: a0 = destination, a1 = source, a2 = word count
memcpy_words:
    li t0, 0              // counter

copy_word_loop:
    bge t0, a2, copy_done
    slli t1, t0, 2        // offset
    add t2, a1, t1        // src address
    add t3, a0, t1        // dst address
    lw t4, 0(t2)          // load word
    sw t4, 0(t3)          // store word
    addi t0, t0, 1
    j copy_word_loop

copy_done:
    ret
