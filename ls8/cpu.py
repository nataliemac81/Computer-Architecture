"""CPU functionality."""

import sys

# op codes

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.pc = 0
        self.reg = [0] * 8 
        self.fl = [0] * 8 
        self.pointer = 7
        self.reg[self.pointer] = len(self.ram) - 1
        self.branchtable = {
            0b10000010: self.opcode_LDI,
            0b00000001: self.opcode_HLT,
            0b01000111: self.opcode_PRN,
            0b10100010: self.opcode_MUL,
            0b01000110: self.opcode_POP,
            0b01000101: self.opcode_PUSH,
            0b01010000: self.opcode_CALL,
            0b00010001: self.opcode_RET,
            0b10100111: self.opcode_CMP
        }

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

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""
        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == self.branchtable[0b10100010]:
            self.reg[reg_a] *= self.reg[reg_b]
        #elif op == "SUB": etc
        elif op == self.branchtable[0b10100111]:
            if self.reg[reg_a] == self.reg[reg_b]:
                # set the E flag to 1
                self.fl = 0b00000001
            elif self.reg[reg_a] < self.reg[reg_b]:
                # set the L flag to 1
                self.fl = 0b00000100
            elif self.reg[reg_a] > self.reg[reg_b]:
                # set the G flag to 1
                self.fl = 0b00000010
            else:
                # set the flag to 0
                self.fl = 0b00000000
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
            ir = self.ram[self.pc]
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)

            if ir in self.branchtable:
                self.branchtable[ir](operand_a, operand_b)
            else:
                print(f"Instruction {ir} is unknown")
                sys.exit(1)
            
    def opcode_LDI(self, a, b):
        # set the value of a register to an int
        self.reg[a] = b
        self.pc += 3  

    def opcode_HLT(self, a, b):
        sys.exit(0)

    def opcode_PRN(self, a, b):
        # print to the console the decimal int value stored in given register
        num = self.reg[a]
        print(num)
        self.pc += 2
    
    def opcode_MUL(self, a, b):
        ir = self.ram[self.pc]
        x = self.branchtable[ir]
        self.alu(x, a, b)
        self.pc += 3

    def opcode_POP(self, a, b):
        # pop value of stack at pointer location
        value = self.ram[self.reg[self.pointer]]
        register = self.ram[self.pc + 1]
        # store value in given register
        self.reg[register] = value
        # increment the stack pointer
        self.reg[self.pointer] += 1
        self.pc += 2 

    def opcode_PUSH(self, a, b):
        register = self.ram[self.pc + 1]
        # decrement the stack pointer
        self.reg[self.pointer] -= 1
        # read the next value for register location
        reg_value = self.reg[register]
        # add the value from that register and add to stack
        self.ram[self.reg[self.pointer]] = reg_value
        self.pc += 2
    
    def opcode_CALL(self, a, b):
        # store the next line to execute on the stack
        # return this line after the subroutine 
        self.reg[self.pointer] -= 1
        self.ram[self.reg[self.pointer]] = self.pc + 2
        # read which register stores the next line passed w/call 
        register = self.ram[self.pc + 1]
        # set the PC to the value in that register
        self.pc = self.reg[register]

    def opcode_RET(self, a, b):
        # pop the current value off stack
        return_address = self.ram[self.reg[self.pointer]]
        # increment the stack pointer up the stack
        self.reg[self.pointer] += 1
        # set the pc to that value
        self.pc = return_address

    def opcode_CMP(self, a, b):
        ir = self.ram[self.pc]
        x = self.branchtable[ir]
        self.alu(x, a, b)
        self.pc += 3
