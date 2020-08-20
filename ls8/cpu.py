"""CPU functionality."""

import sys
import os

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [None] * 256

        # reserved
        # self.ram[0xF7] = 
        # self.ram[0xF6] = 
        # self.ram[0xF5] = 

        # 8 general-purpose 8-bit numeric registers R0-R7.
        self.reg = [None] * 8

        # stack pointer
        self.sp = 0xF4
        # Initialize the SP to address 0xF4
        self.reg[7] = self.sp

        # R5 is reserved as the interrupt mask (IM)
        # R6 is reserved as the interrupt status (IS)
        # R7 is reserved as the stack pointer (SP)

        # Instruction Register - contains a copy of the currently executing
        # instruction
        self.ir = None

        # The flags register FL holds the current flags status. These flags can change based on the operands given to the CMP opcode.

        # program counter
        self.pc = 0

        self.running = False
        
        
        """Instruction Opcodes"""
        self.HLT = 0b00000001
        self.LDI = 0b10000010
        self.PRN = 0b01000111
        self.ADD = 0b10100000
        self.SUB = 0b10100001
        self.MUL = 0b10100010
        self.DIV = 0b10100011
        self.PUSH = 0b01000101
        self.POP = 0b01000110
        self.CALL = 0b01010000
        self.RET = 0b00010001
        
        # Set up a branch table
        self.branchtable = {}
        self.branchtable[self.HLT] = self.op_hlt
        self.branchtable[self.LDI] = self.op_ldi
        self.branchtable[self.PRN] = self.op_prn
        self.branchtable[self.PUSH] = self.op_push
        self.branchtable[self.POP] = self.op_pop
        # self.branchtable[CALL] = self.handle_call
        # self.branchtable[RET] = self.handle_ret
        

        
    def load(self):
        """Load a program into memory."""
    
        try:
            file_path = "\\examples\\" + sys.argv[1]

            address = 0

            with open(os.path.dirname(os.path.abspath(__file__)) + file_path) as f:
                for line in f:
                    try:
                        current = line.split('#')[0].strip()
                        if current:
                            value = int(current, 2)
                            self.ram[address] = value
                            address += 1
                    except ValueError:
                        pass
        except IndexError:
            sys.exit("Command line argument is required")
        except FileNotFoundError:
            sys.exit("Invalid file")
        
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

    # MDR === Memory Address Register (index)
    def ram_read(self, MAR):
        return self.ram[MAR]

    # MDR === Memory Data Register (value)
    def ram_write(self, MDR, MAR):
        self.ram[MAR] = MDR


    def alu(self, op):
        """ALU operations."""
        reg_a = self.ram_read(self.pc + 1)
        reg_b = self.ram_read(self.pc + 2)

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "SUB":
            self.reg[reg_a] -= self.reg[reg_b]
        elif op == "MUL": 
            #Multiply the values in two registers together and store the result in registerA.
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == "SHL":
            self.reg[reg_a] <<= self.reg[reg_b]
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

    def op_add(self):
        self.alu("ADD")

    def op_sub(self):
        self.alu("SUB")

    def op_mul(self):
        self.alu("MUL")

    def op_shl(self):
        self.alu("SHL")


    def op_hlt(self):
        self.running = False

    def op_ldi(self):
        # memory address register (index)
        reg_index = self.ram_read(self.pc + 1)
        # memory data register (value)
        value = self.ram_read(self.pc + 2)
        
        # save in register
        self.reg[reg_index] = value

    # print
    def op_prn(self):
        # memory address register (index)
        reg_index = self.ram_read(self.pc + 1)
        
        print(self.reg[reg_index])

    def op_push(self):
        # Decrement the Stack Pointer
        self.sp -= 1

        # read the register index from ram
        reg_index = self.ram_read(self.pc + 1)

        # Get the value from the register
        value = self.reg[reg_index]

        # update stack
        self.ram_write(value, self.sp)

    def op_pop(self):
        # read value from stack
        value = self.ram_read(self.sp)

        # Get the register index number to copy into
        reg_index = self.ram_read(self.pc + 1)

        # Copy the value from the address pointed to by SP to the given register.
        self.reg[reg_index] = value

        # increment stack pointer
        self.sp += 1

    def run(self):
        """Run the CPU."""
        self.running = True

        while self.running:
            op_size = 1
            
            # Instruction Register - contains a copy of the currently executing
            # instruction
            self.ir = self.ram_read(self.pc)

            # get program counter from command
            op_size = ((self.ir >> 6) & 0b11) + 1
  
            # call the action function that matches on the table
            self.branchtable[self.ir]()

            # update program counter
            self.pc += op_size

