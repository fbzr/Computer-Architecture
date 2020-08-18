"""CPU functionality."""

import sys
import os




class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [None] * 256
        self.reg = [None] * 8

        # program counter
        self.pc = 0
        
        self.LDI = 0b10000010
        self.PRN = 0b01000111
        self.HLT = 0b00000001
        
    def load(self):
        """Load a program into memory."""
        file_path = "\\examples\\" + sys.argv[1]

        address = 0

        # For now, we've just hardcoded a program:
        # instructions
        # program = [
        #     # From print8.ls8
        #     self.LDI, # LDI R0,8
        #     0b00000000,
        #     0b00001000,
        #     self.PRN, # PRN R0
        #     0b00000000,
        #     self.HLT, # HLT
        # ]


        # for instruction in program:
        #     self.ram[address] = instruction
        #     address += 1

            
        with open(os.path.dirname(os.path.abspath(__file__)) + file_path) as f:
            for line in [line[:8] for line in f]:
                try:
                    value = int(line, 2)
                    self.ram[address] = value
                    address += 1
                except ValueError:
                    pass

    # MDR === Memory Address Register (index)
    def ram_read(self, MAR):
        return self.ram[MAR]

    # MDR === Memory Data Register (value)
    def ram_write(self, MDR, MAR):
        self.ram[MAR] = MDR

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
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

    def run(self):
        """Run the CPU."""
        running = True

        

        while running:
            op_size = 1
            
            # Istruction Register - It needs to read the memory address that's stored in register PC, and store that result in IR
            ir = self.ram_read(self.pc)

            if ir == self.HLT:
                running = False
            elif ir == self.LDI: # sets a specified register to  a specified value
                # memory address register (index)
                reg_index = self.ram_read(self.pc + 1)
                # memory data register (value)
                value = self.ram_read(self.pc + 2)
                
                # save in register
                self.reg[reg_index] = value
                
                # Operation size
                op_size = 3
            elif ir == self.PRN:
                # memory address register (index)
                reg_index = self.ram_read(self.pc + 1)
                
                print(self.reg[reg_index])
                
                op_size = 2

            # update program counter
            self.pc += op_size
