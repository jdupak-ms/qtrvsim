// Bubble sort benchmark
// This benchmark tests branch prediction and memory access patterns
// Compatible with QtRvSim integrated assembler

.globl _start

// System call numbers
.equ __NR_exit, 93

.text
.org 0x200

_start:
    // Initialize stack pointer
    li sp, 0x8000

    // Load array address and size
    li a0, 0x1000         // array address
    li a1, 32             // array size

    // Call bubble sort
    jal ra, bubble_sort

    // Exit program
    addi a7, zero, __NR_exit
    addi a0, zero, 0
    ecall

// bubble_sort: Sort array in ascending order
// Arguments: a0 = pointer to array, a1 = array size
bubble_sort:
    addi sp, sp, -16
    sw ra, 12(sp)
    sw s0, 8(sp)
    sw s1, 4(sp)
    sw s2, 0(sp)

    mv s0, a0             // s0 = array pointer
    mv s1, a1             // s1 = n

    addi s1, s1, -1       // n - 1 for outer loop

outer:
    blez s1, done_sort
    li s2, 0              // swapped = false
    li t0, 0              // i = 0

inner:
    bge t0, s1, end_inner

    // Calculate addresses
    slli t1, t0, 2        // i * 4
    add t2, s0, t1        // &array[i]
    lw t3, 0(t2)          // array[i]
    lw t4, 4(t2)          // array[i+1]

    // Compare and swap if needed
    ble t3, t4, no_swap

    // Swap
    sw t4, 0(t2)
    sw t3, 4(t2)
    li s2, 1              // swapped = true

no_swap:
    addi t0, t0, 1
    j inner

end_inner:
    beqz s2, done_sort    // Early exit if no swaps
    addi s1, s1, -1
    j outer

done_sort:
    lw ra, 12(sp)
    lw s0, 8(sp)
    lw s1, 4(sp)
    lw s2, 0(sp)
    addi sp, sp, 16
    ret

.data
.org 0x1000
array:
    .word 64, 34, 25, 12, 22, 11, 90, 42
    .word 18, 77, 55, 33, 99, 1, 45, 67
    .word 89, 23, 56, 78, 43, 21, 87, 65
    .word 32, 54, 76, 98, 10, 88, 44, 66
