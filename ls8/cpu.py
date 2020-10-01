"""CPU functionality."""

import sys


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.reg = [0] * 8
        self.ram = [0] * 256
        self.pc = 0
        self.running = False
        self.ir_dict = {}
        self.ir_dict[0b00000001] = self.HTL
        self.ir_dict[0b10000010] = self.LDI
        self.ir_dict[0b01000111] = self.PRN
        self.ir_dict[0b10100010] = self.MUL

    def load(self, file):
        """Load a program into memory."""

        address = 0

        with open(file) as program:
            for line in program:
                line = line.strip().split()

                if len(line) == 0:
                    continue

                if line[0] == "#":
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
        elif op == "MUL":
            self.ram[reg_a] *= self.ram[reg_b]
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
        value = self.ram[MAR]
        print(value)

    def ram_write(self, MDR, MAR):
        self.ram[MAR] = MDR

    def HTL(self):
        self.running = False

    def LDI(self):
        address = self.ram[self.pc+1]
        value = self.ram[self.pc+2]

        self.ram_write(value, address)
        self.pc += 3

    def PRN(self):
        address = self.ram[self.pc+1]

        self.ram_read(address)
        self.pc += 2

    def MUL(self):
        address_one = self.ram[self.pc+1]
        address_two = self.ram[self.pc+2]

        self.alu("MUL",  address_one, address_two)
        self.pc += 3

    def run(self):
        """Run the CPU."""
        self.running = True

        while self.running:
            ir = self.ram[self.pc]

            if ir in self.ir_dict:
                self.ir_dict[ir]()

            else:
                print("Not a valid instruction")
                self.running = False
