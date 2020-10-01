"""CPU functionality."""

import sys

HLT = 0b00000001
LDI = 0b10000010
PRN = 0b01000111
MULT = 0b10100010
PUSH = 0b01000101
POP = 0b01000110


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.sp = 7  # Register 7 is reserved as stack pointer
        self.reg[self.sp] = 0xF4  # Stack pointer is set to F4 to start
        self.pc = 0  # program counter
        self.running = False

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
        """Instruction to HLT program"""
        self.running = False
        sys.exit(1)

    def ldi(self):
        """Instruction to run ram_write"""
        reg_num = self.ram[self.pc+1]
        value = self.ram[self.pc+2]

        self.ram_write(value, reg_num)
        self.pc += 3

    def prn(self):
        """Instruction to run ram_read"""
        reg_num = self.ram[self.pc+1]

        self.ram_read(reg_num)
        self.pc += 2

    def mult(self):
        """Instruction to run MULT from alu"""
        reg_num_one = self.ram[self.pc+1]
        reg_num_two = self.ram[self.pc+2]

        self.alu("MULT", reg_num_one, reg_num_two)
        self.pc += 3

    def push(self):
        """Instruction to push value in the given register on the stack"""
        self.sp -= 1

        reg_num = self.ram[self.pc + 1]
        value = self.reg[reg_num]
        top_of_stack_addr = self.sp
        self.ram[top_of_stack_addr] = value

        self.pc += 2

        # print(f"stack: {self.ram[0xE4:0xF4]}")

    def pop(self):
        """Instruction to pop the value at the top of the stack into the given register"""
        value = self.ram[self.sp]
        address = self.ram[self.pc + 1]
        self.reg[address] = value

        self.sp += 1
        self.pc += 2

    def call_stack(self, ir):
        instruction_response_dict = {
            HLT: self.hlt,
            LDI: self.ldi,
            PRN: self.prn,
            MULT: self.mult,
            PUSH: self.push,
            POP: self.pop,
        }

        if ir in instruction_response_dict:
            instruction_response_dict[ir]()

        else:
            print("Not a valid instruction")
            self.running = False
            sys.exit(1)

    def run(self):
        """Run the CPU."""
        self.running = True

        while self.running:
            ir = self.ram[self.pc]
            self.call_stack(ir)
