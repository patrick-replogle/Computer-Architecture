"""CPU functionality."""

import sys

# Save valid instruction responses as variables for readability
HLT = 0b00000001
LDI = 0b10000010
PRN = 0b01000111
MULT = 0b10100010
PUSH = 0b01000101
POP = 0b01000110
CALL = 0b01010000
RET = 0b00010001
ADD = 0b10100000


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.sp = 7  # stack pointer
        self.reg[self.sp] = 0xF4  # Stack pointer is set to F4 to start
        self.pc = 0  # program counter
        self.running = False
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

        print()

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

        # print(f"stack: {self.ram[0xE4:0xF4]}")

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
