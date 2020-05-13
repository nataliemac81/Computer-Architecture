"""CPU functionality."""

import sys

# op codes
LDI = 0b10000010
HLT = 0b00000001
PRN = 0b01000111
MUL = 0b10100010
POP = 0b01000110
PUSH = 0b01000101


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.pc = 0
        self.reg = [0] * 8 
        self.pointer = 7
        self.reg[self.pointer] = len(self.ram) - 1

    def load(self):
        """Load a program into memory."""

        address = 0

        print(sys.argv)
        if len(sys.argv) != 2:
            print("Please enter proper file name")
            sys.exit(1)

        file = sys.argv[1]
        with open(file) as f:
            for line in f:
                comment_split = line.strip().split('#')
                num = comment_split[0].strip()
                if num == '':
                    continue
                instruction = int(num, 2)
                self.ram[address] = instruction
                address += 1


        # For now, we've just hardcoded a program:

        # program = [
        #     # From print8.ls8
        #     0b10000010, # LDI R0,8
        #     0b00000000,
        #     0b00001000,
        #     0b01000111, # PRN R0
        #     0b00000000,
        #     0b00000001, # HLT
        # ]

        # for instruction in program:
        #     self.ram[address] = instruction
        #     address += 1


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == MUL:
            self.reg[reg_a] *= self.reg[reg_b]
        #elif op == "SUB": etc
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def ram_read(self, address): # address == MAR: Memory Address Register
        value = self.ram[address]
        return value

    def ram_write(self, value, address): # value == MDR: Memory Data Register
        self.ram[address] = value

    def run(self):
        """Run the CPU."""
        while True:
            op_code = self.ram[self.pc]
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)

            if op_code == LDI:
                # set the value of a register to an int
                self.reg[operand_a] = operand_b
                self.pc += 3              
            elif op_code == HLT:
                sys.exit(0)
            elif op_code == PRN:
                # print to the console the decimal int value stored in given register
                num = self.reg[operand_a]
                print(num)
                self.pc += 2
            elif op_code == MUL:
                self.alu(op_code, operand_a, operand_b)
                self.pc += 3
            elif op_code == POP:
                # pop value of stack at pointer location
                value = self.ram[self.reg[self.pointer]]
                register = self.ram[self.pc + 1]
                # store value in given register
                self.reg[register] = value
                # increment the stack pointer
                self.reg[self.pointer] += 1
                self.pc += 2 
            elif op_code == PUSH:
                register = self.ram[self.pc + 1]
                # decrement the stack pointer
                self.reg[self.pointer] -= 1
                # read the next value for register location
                reg_value = self.reg[register]
                # add the value from that register and add to stack
                self.ram[self.reg[self.pointer]] = reg_value
                self.pc += 2 
            else:
                print(f"Instruction {op_code} is unknown")
                sys.exit(1)
