"""CPU functionality."""

import sys
import os

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU.
        When the LS-8 is booted, the following steps occur:

        R0-R6 are cleared to 0.
        R7 is set to 0xF4.
        PC and FL registers are cleared to 0.
        RAM is cleared to 0.
        """
        self.ram = [0] * 256

        # 8 general-purpose 8-bit numeric registers R0-R7.
        self.reg = [0] * 8
        # stack pointer
        self.SP = 7
        # Initialize the SP to address 0xF4
        self.reg[self.SP] = 0xF4

        # R5 is reserved as the interrupt mask (IM)
        # R6 is reserved as the interrupt status (IS)
        # R7 is reserved as the stack pointer (SP)

        # Instruction Register - contains a copy of the currently executing
        # instruction
        self.ir = None

        # The flags register FL holds the current flags status. These flags can change based on the operands given to the CMP opcode.

        # program counter
        self.pc = 0
        # Flag
        self.fl = 0b00000000

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
        self.CMP = 0b10100111
        self.JNE = 0b01010110
        self.JEQ = 0b01010101
        self.JMP = 0b01010100 
        self.AND = 0b10101000
        self.OR = 0b10101010
        self.XOR = 0b10101011
        self.NOT = 0b01101001
        self.SHL = 0b10101100
        self.SHR = 0b10101101
        self.MOD = 0b10100100

        # Set up a branch table
        self.branchtable = {}
        self.branchtable[self.HLT] = self.op_hlt
        self.branchtable[self.LDI] = self.op_ldi
        self.branchtable[self.PRN] = self.op_prn
        self.branchtable[self.PUSH] = self.op_push
        self.branchtable[self.POP] = self.op_pop
        self.branchtable[self.CALL] = self.op_call
        self.branchtable[self.RET] = self.op_ret
        self.branchtable[self.JNE] = self.op_jne
        self.branchtable[self.JEQ] = self.op_jeq
        self.branchtable[self.JMP] = self.op_jmp
        
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


    # MDR === Memory Address Register (index)
    def ram_read(self, MAR):
        return self.ram[MAR]

    # MDR === Memory Data Register (value)
    def ram_write(self, MDR, MAR):
        self.ram[MAR] = MDR

    def alu(self):
        """ALU operations."""
        reg_a = self.ram_read(self.pc + 1)
        reg_b = self.ram_read(self.pc + 2)

        try:
            if self.ir == self.ADD:
                self.reg[reg_a] += self.reg[reg_b]
            
            elif self.ir == self.SUB:
                self.reg[reg_a] -= self.reg[reg_b]
            
            elif self.ir == self.MUL: 
                #Multiply the values in two registers together and store the result in registerA.
                self.reg[reg_a] *= self.reg[reg_b]
            
            elif self.ir == self.DIV:
                self.reg[reg_a] /= self.reg[reg_b]
            
            elif self.ir == self.CMP:
                '''
                CMP registerA registerB
                Compare the values in two registers.
                If they are equal, set the Equal E flag to 1, otherwise set it to 0.
                If registerA is less than registerB, set the Less-than L flag to 1, otherwise set it to 0.
                If registerA is greater than registerB, set the Greater-than G flag to 1, otherwise set it to 0.

                FL bits: 00000LGE
                L Less-than: during a CMP, set to 1 if registerA is less than registerB, zero otherwise.
                G Greater-than: during a CMP, set to 1 if registerA is greater than registerB, zero otherwise.
                E Equal: during a CMP, set to 1 if registerA is equal to registerB, zero otherwise.
                '''
                # initialize with equal value
                self.fl = 0b00000001

                # check if values are different
                if (self.reg[reg_a] > self.reg[reg_b]):
                    self.fl <<= 1
                elif (self.reg[reg_a] < self.reg[reg_b]):
                    self.fl <<= 2
            elif self.ir == self.AND:
                # Bitwise-AND the values in registerA and registerB, then store the result in registerA.
                self.reg[reg_a] &= int(self.reg[reg_a]) & int(self.reg[reg_b])
            elif self.ir == self.OR:
                # Perform a bitwise-OR between the values in registerA and registerB, storing the result in registerA.
                self.reg[reg_a] |= self.reg[reg_b]
            elif self.ir == self.XOR:
                # XOR between the values in registerA and registerB, storing the result in registerA
                self.reg[reg_a] ^= self.reg[reg_b]
            elif self.ir == self.NOT:
                self.reg[reg_a] = ~self.reg[reg_a]
            elif self.ir == self.SHL:
                self.reg[reg_a] <<= self.reg[reg_b]
            elif self.ir == self.SHR:
                self.reg[reg_a] >>= self.reg[reg_b]
            elif self.ir == self.MOD:
                self.reg[reg_a] %= self.reg[reg_b]
            
            else:
                raise Exception

        except:
            print("Unsupported ALU operation")
            sys.exit()

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
        self.reg[self.SP] -= 1

        # read the register index from ram
        reg_index = self.ram_read(self.pc + 1)

        # Get the value from the register
        value = self.reg[reg_index]

        # update stack
        self.ram_write(value, self.reg[self.SP])

    def op_pop(self):
        # read value from stack
        value = self.ram_read(self.reg[self.SP])

        # Get the register index number to copy into
        reg_index = self.ram_read(self.pc + 1)

        # Copy the value from the address pointed to by SP to the given register.
        self.reg[reg_index] = value

        # increment stack pointer
        self.reg[self.SP] += 1

    def op_call(self):
        # Get the address of the instruction directly after CALL
        return_address = self.pc + 2

        # Push it onto the stack
        ## Decrement the Stack Pointer
        self.reg[self.SP] -= 1

        ## Store the return address at the top of the stack
        self.ram_write(return_address,self.reg[self.SP])

        # read register index to get address to jump to
        reg_index = self.ram_read(self.pc + 1)

        # get address stored in register
        address = self.reg[reg_index]

        # Set the PC to that address
        self.pc = address

    def op_ret(self):
        # Pop the address at the top of the stack

        # Get the address pointed to by the Stack Pointer
        address = self.ram_read(self.reg[self.SP])
        # increment the Stack Pointer
        self.reg[self.SP] += 1
        # Assign PC to that address
        self.pc = address

    def op_jne(self):
        # FL bits: 00000LGE
        # If E flag is clear (false, 0), 
        if not self.fl & 0b00000001:
            # jump to the address stored in the given register.
            # read address 
            reg_index = self.ram_read(self.pc + 1)
            self.pc = self.reg[reg_index]
        else:
            self.pc += (self.ir >> 6) + 1
    
    def op_jeq(self):
        '''
        JEQ register
        If equal flag is set (true), jump to the address stored in the given register.
        '''
        # FL bits: 00000LGE
        # If E flag is true, 1, 
        if self.fl & 0b00000001:
            # jump to the address stored in the given register.
            # read address 
            reg_index = self.ram_read(self.pc + 1)
            self.pc = self.reg[reg_index]
        else:
            self.pc += (self.ir >> 6) + 1

    def op_jmp(self):
        '''
        Jump to the address stored in the given register.
        Set the PC to the address stored in the given register.
        '''
        reg_index = self.ram_read(self.pc + 1)
        self.pc = self.reg[reg_index]

    def run(self):
        """Run the CPU.
        Execution Sequence
        The instruction pointed to by the PC is fetched from RAM, decoded, and executed.
        If the instruction does not set the PC itself, the PC is advanced to point to the subsequent instruction.
        If the CPU is not halted by a HLT instruction, go to step 1.
        """
        self.running = True

        while self.running:          
            # # debug helper  
            # self.trace()

            # Instruction Register - contains a copy of the currently executing
            # instruction
            self.ir = self.ram_read(self.pc)

            # AABCDDDD -> AA Number of operands for this opcode, 0-2
            # get program counter from command
            op_size = (self.ir >> 6) + 1
  
            try:
                # AABCDDDD: B 1 if this is an ALU operation
                # check if it's an ALU operation
                if (self.ir >> 5) & 0b1:
                    self.alu()
                else:
                    # call the action function that matches on the table
                    self.branchtable[self.ir]()
            except KeyError:
                print(f'Invalid operation: {self.ir}')
                sys.exit()

            # AABCDDDD
            # C 1 if this instruction sets the PC
            # Check if this instruction sets the PC directly
            updated_pc = (self.ir >> 4) & 0b0001
            if not updated_pc:
                # update program counter
                self.pc += op_size