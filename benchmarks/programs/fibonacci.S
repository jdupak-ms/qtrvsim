// Fibonacci benchmark
// This benchmark tests recursive function calls and stack operations
// Compatible with QtRvSim integrated assembler

.globl _start

// System call numbers
.equ __NR_exit, 93

.text
.org 0x200

_start:
    // Initialize stack pointer
    li sp, 0x8000         // Stack at 0x8000

    // Calculate fibonacci(20)
    li a0, 20
    jal ra, fibonacci

    // Store result
    li t0, 0x1000         // result address
    sw a0, 0(t0)

    // Exit program
    addi a7, zero, __NR_exit
    addi a0, zero, 0
    ecall

// fibonacci: Calculate nth Fibonacci number recursively
// Arguments: a0 = n
// Returns: a0 = fib(n)
fibonacci:
    // Base cases: fib(0) = 0, fib(1) = 1
    li t0, 1
    ble a0, t0, fib_base

    // Save registers
    addi sp, sp, -12
    sw ra, 8(sp)
    sw s0, 4(sp)
    sw s1, 0(sp)

    mv s0, a0             // Save n

    // Calculate fib(n-1)
    addi a0, s0, -1
    jal ra, fibonacci
    mv s1, a0             // s1 = fib(n-1)

    // Calculate fib(n-2)
    addi a0, s0, -2
    jal ra, fibonacci
                          // a0 = fib(n-2)

    // Return fib(n-1) + fib(n-2)
    add a0, s1, a0

    // Restore registers
    lw ra, 8(sp)
    lw s0, 4(sp)
    lw s1, 0(sp)
    addi sp, sp, 12
    ret

fib_base:
    // Return n for base cases
    ret

.data
.org 0x1000
result:
    .word 0
