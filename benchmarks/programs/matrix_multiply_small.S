// Matrix multiplication benchmark (4x4 matrices)
// This benchmark tests basic computation and memory access patterns
// Compatible with QtRvSim integrated assembler

.globl _start

// System call numbers
.equ __NR_exit, 93

// Memory layout
.equ MATRIX_A, 0x1000
.equ MATRIX_B, 0x1040
.equ MATRIX_C, 0x1080

.text
.org 0x200

_start:
    // Initialize stack pointer
    li sp, 0x8000

    // Initialize matrix pointers
    li a0, MATRIX_A       // matrix A
    li a1, MATRIX_B       // matrix B
    li a2, MATRIX_C       // result matrix C
    li a3, 4              // matrix dimension

    // Call matrix multiply
    jal ra, matrix_multiply

    // Exit program
    addi a7, zero, __NR_exit
    addi a0, zero, 0
    ecall

// matrix_multiply: C = A * B
// Arguments: a0=A, a1=B, a2=C, a3=N
matrix_multiply:
    addi sp, sp, -32
    sw ra, 28(sp)
    sw s0, 24(sp)
    sw s1, 20(sp)
    sw s2, 16(sp)
    sw s3, 12(sp)
    sw s4, 8(sp)
    sw s5, 4(sp)
    sw s6, 0(sp)

    mv s0, a0             // s0 = A
    mv s1, a1             // s1 = B
    mv s2, a2             // s2 = C
    mv s3, a3             // s3 = N

    li s4, 0              // i = 0
outer_loop:
    bge s4, s3, done_outer

    li s5, 0              // j = 0
middle_loop:
    bge s5, s3, done_middle

    li t3, 0              // sum = 0
    li s6, 0              // k = 0
inner_loop:
    bge s6, s3, done_inner

    // Calculate A[i][k] address: A + (i * N + k) * 4
    mul t0, s4, s3
    add t0, t0, s6
    slli t0, t0, 2
    add t0, s0, t0
    lw t1, 0(t0)          // t1 = A[i][k]

    // Calculate B[k][j] address: B + (k * N + j) * 4
    mul t0, s6, s3
    add t0, t0, s5
    slli t0, t0, 2
    add t0, s1, t0
    lw t2, 0(t0)          // t2 = B[k][j]

    // sum += A[i][k] * B[k][j]
    mul t0, t1, t2
    add t3, t3, t0

    addi s6, s6, 1
    j inner_loop

done_inner:
    // Store C[i][j] = sum
    mul t0, s4, s3
    add t0, t0, s5
    slli t0, t0, 2
    add t0, s2, t0
    sw t3, 0(t0)

    addi s5, s5, 1
    j middle_loop

done_middle:
    addi s4, s4, 1
    j outer_loop

done_outer:
    lw ra, 28(sp)
    lw s0, 24(sp)
    lw s1, 20(sp)
    lw s2, 16(sp)
    lw s3, 12(sp)
    lw s4, 8(sp)
    lw s5, 4(sp)
    lw s6, 0(sp)
    addi sp, sp, 32
    ret

.data
.org 0x1000
matrix_a:
    .word 1, 2, 3, 4
    .word 5, 6, 7, 8
    .word 9, 10, 11, 12
    .word 13, 14, 15, 16

.org 0x1040
matrix_b:
    .word 1, 0, 0, 0
    .word 0, 1, 0, 0
    .word 0, 0, 1, 0
    .word 0, 0, 0, 1

.org 0x1080
matrix_c:
    .word 0, 0, 0, 0
    .word 0, 0, 0, 0
    .word 0, 0, 0, 0
    .word 0, 0, 0, 0
