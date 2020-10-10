"""CPU functionality."""

import sys

# Instruction responses
HLT = 0b00000001
LDI = 0b10000010
PRN = 0b01000111
MULT = 0b10100010
PUSH = 0b01000101
POP = 0b01000110
CALL = 0b01010000
RET = 0b00010001
ADD = 0b10100000
CMP = 0b10100111
JMP = 0b01010100
JEQ = 0b01010101
JNE = 0b01010110
AND = 0b10101000
OR = 0b10101010
XOR = 0b10101011
NOT = 0b01101001


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.running = False
        self.sp = 7  # stack pointer
        self.reg[self.sp] = 0xF4  # Stack pointer is set to F4 to start
        self.pc = 0  # program counter
        self.e = 0  # equal flag
        self.l = 0  # less than flag
        self.g = 0  # greater than flag
        self.ir_methods = {
            HLT: self.hlt,
            LDI: self.ldi,
            PRN: self.prn,
            MULT: self.mult,
            PUSH: self.push,
            POP: self.pop,
            CALL: self.call,
            RET: self.ret,
            ADD: self.add,
            CMP: self.compare,
            JMP: self.jmp,
            JEQ: self.jeq,
            JNE: self.jne,
            AND: self.AND,
            OR: self.OR,
            XOR: self.xor,
            NOT: self.NOT,
        }

    def load(self, file_path):
        """Load a program into memory."""
        address = 0

        with open(file_path) as program:
            for line in program:
                line = line.strip().split()

                if len(line) == 0 or line[0] == "#":
                    continue

                try:
                    self.ram[address] = int(line[0], 2)

                except ValueError:
                    print(f"Invalid number: {line[0]}")

                address += 1

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]

        elif op == "MULT":
            self.reg[reg_a] *= self.reg[reg_b]

        elif op == "CMP":
            # Equal flag
            if self.reg[reg_a] == self.reg[reg_b]:
                self.e = 1
            else:
                self.e = 0
            # Less than flag
            if self.reg[reg_a] < self.reg[reg_b]:
                self.l = 1
            else:
                self.l = 0
            # Greater than flag
            if self.reg[reg_a] > self.reg[reg_b]:
                self.g = 1
            else:
                self.g = 0

        elif op == "AND":
            self.reg[reg_a] = self.reg[reg_a] & self.reg[reg_b]

        elif op == "OR":
            self.reg[reg_a] = self.reg[reg_a] | self.reg[reg_b]

        elif op == "XOR":
            self.reg[reg_a] = self.reg[reg_a] ^ self.reg[reg_b]

        elif op == "NOT":
            self.reg[reg_a] = ~self.reg[reg_a]

        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

    def ram_read(self, MAR):
        """Read value stored in given RAM memory address"""
        print(self.reg[MAR])

    def ram_write(self, MDR, MAR):
        """Write value into the given RAM memory address"""
        self.reg[MAR] = MDR

    def hlt(self):
        """HLT program"""
        self.running = False
        sys.exit(1)

    def ldi(self):
        """Run ram_write"""
        reg_num = self.ram[self.pc+1]
        value = self.ram[self.pc+2]

        self.ram_write(value, reg_num)
        self.pc += 3

    def prn(self):
        """Run ram_read"""
        reg_num = self.ram[self.pc + 1]

        self.ram_read(reg_num)
        self.pc += 2

    def add(self):
        """Run ADD from alu"""
        reg_num_one = self.ram[self.pc + 1]
        reg_num_two = self.ram[self.pc + 2]

        self.alu("ADD", reg_num_one, reg_num_two)
        self.pc += 3

    def mult(self):
        """Run MULT from alu"""
        reg_num_one = self.ram[self.pc+1]
        reg_num_two = self.ram[self.pc+2]

        self.alu("MULT", reg_num_one, reg_num_two)
        self.pc += 3

    def push(self):
        """Push value in the given register on the stack"""
        self.reg[self.sp] -= 1

        reg_num = self.ram[self.pc + 1]
        value = self.reg[reg_num]
        top_of_stack_addr = self.reg[self.sp]

        self.ram[top_of_stack_addr] = value
        self.pc += 2

    def pop(self):
        """Pop the value at the top of the stack into the given register"""
        top_of_stack_addr = self.reg[self.sp]
        value = self.ram[top_of_stack_addr]
        reg_num = self.ram[self.pc + 1]

        self.reg[reg_num] = value
        self.reg[self.sp] += 1
        self.pc += 2

    def call(self):
        """Calls a subroutine (function) at the address stored in the register"""
        ret_addr = self.pc + 2

        self.reg[self.sp] -= 1
        self.ram[self.reg[self.sp]] = ret_addr

        reg_num = self.ram[self.pc + 1]
        self.pc = self.reg[reg_num]

    def ret(self):
        """Return from subroutine"""
        ret_addr = self.ram[self.reg[self.sp]]
        self.reg[self.sp] += 1

        self.pc = ret_addr

    def compare(self):
        """Compare the values in two registers"""
        reg_one = self.ram[self.pc + 1]
        reg_two = self.ram[self.pc + 2]

        self.alu("CMP", reg_one, reg_two)
        self.pc += 3

    def jmp(self):
        """Jump to the address stored in the given register"""
        reg_num = self.ram[self.pc + 1]
        next_address = self.reg[reg_num]

        self.pc = next_address

    def jeq(self):
        """If equal flag is set (true), jump to the address stored in the given register"""
        if self.e == 1:
            self.jmp()
        else:
            self.pc += 2

    def jne(self):
        """If E flag is clear (false, 0), jump to the address stored in the given register"""
        if self.e == 0:
            self.jmp()
        else:
            self.pc += 2

    def AND(self):
        """Add the value in two registers and store the result in registerA"""
        reg_one = self.ram[self.pc + 1]
        reg_two = self.ram[self.pc + 2]

        self.alu("AND", reg_one, reg_two)
        self.pc += 3

    def OR(self):
        """Perform a bitwise-OR between the values in registerA and registerB, storing the result in registerA"""
        reg_one = self.ram[self.pc + 1]
        reg_two = self.ram[self.pc + 2]

        self.alu("OR", reg_one, reg_two)
        self.pc += 3

    def xor(self):
        """Perform a bitwise-XOR between the values in registerA and registerB, storing the result in registerA"""
        reg_one = self.ram[self.pc + 1]
        reg_two = self.ram[self.pc + 2]

        self.alu("XOR", reg_one, reg_two)
        self.pc += 3

    def NOT(self):
        """Perform a bitwise-NOT on the value in a register, storing the result in the register"""
        reg_one = self.ram[self.pc + 1]

        self.alu("NOT", reg_one, None)
        self.pc += 2

    def run(self):
        """Run the CPU."""
        self.running = True

        while self.running:
            ir = self.ram[self.pc]

            if ir in self.ir_methods:
                self.ir_methods[ir]()

            else:
                print(f"Invalid instruction {ir} at address {self.pc}")
                self.running = False
                sys.exit(1)
