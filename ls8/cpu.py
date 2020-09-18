"""CPU functionality."""
EQUAL_FLAG = 0b001
GREATER_FLAG = 0b010
LESS_FLAG = 0b100

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.reg = [0] * 7 + [0xF4]
        self.ram = [0] * 256
        self.pc = 0
        self.sp = 7
        self.flag = 0

    def ram_read(self, MAR):
        return self.ram[MAR]

    def ram_write(self, MAR, MDR):
        self.ram[MAR] = MDR

    def load(self):
        """Load a program into memory."""

        address = 0
        
        # checks if there is an argument in CLI
        if len(sys.argv) <= 1:
            print(">> No Valid Arguments")
            sys.exit()
        else:
            # stores CLI argument
            arg = sys.argv[1]


        # open/closes file
        with open(arg, "r") as e:

            # confirmation for file opened
            print(f">> Loaded: {e.name.split('/')[-1].upper()}")

            for instruction in e.readlines():

                # strips white space
                instruction = instruction.split("#")[0].strip()
                
                # ignores blank lines
                if not instruction:
                    continue
            
                # loads to ram
                self.ram[address] = int(instruction, 2)
                address += 1    


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == "SUB":
            self.reg[reg_a] -= self.reg[reg_b]
        elif op == "DIV":
            self.reg[reg_a] //= self.reg[reg_b]
        elif op == "AND":
            self.reg[reg_a] &= self.reg[reg_b]
        elif op == "OR":
            self.reg[reg_a] |= self.reg[reg_b]
        elif op == "XOR":
            self.reg[reg_a] ^= self.reg[reg_b]
        elif op == "NOT":
            self.reg[reg_a] = ~self.reg[reg_a]
        elif op == "SHL":
            self.reg[reg_a] <<= self.reg[reg_b]
        elif op == "SHR":
            self.reg[reg_a] >>= self.reg[reg_b]

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
            ir = self.ram[self.pc]

            # HLT
            if ir == 0b00000001:
                running = False
                sys.exit()

            # LDI
            if ir == 0b10000010:
                reg_index = self.ram[self.pc + 1]
                data_value = self.ram[self.pc + 2]
                self.reg[reg_index] = data_value
                self.pc += 3
            
            # PRN
            if ir == 0b01000111:
                reg_index = self.ram[self.pc + 1]
                print(f"** {self.reg[reg_index]}")
                self.pc += 2

            # PUSH
            if ir == 0b01000101:
                # decrement sp
                self.reg[self.sp] -= 1

                # get reg index to push
                reg_num = self.ram[self.pc + 1]

                # get value from reg index
                value = self.reg[reg_num]

                # copy value to sp address
                stack_top = self.reg[self.sp]
                self.ram[stack_top] = value
                self.pc += 2

            # POP
            if ir == 0b01000110:
                # get reg index to pop
                reg_num = self.ram[self.pc + 1]
   
                # get top of stack address
                stack_top = self.reg[self.sp]

                # get value from stack top
                value = self.ram[stack_top]

                # store value in register
                self.reg[reg_num] = value

                self.reg[self.sp] += 1
                self.pc += 2

            # CALL
            if ir == 0b01010000:
                rtn_index = self.pc + 2

                self.reg[self.sp] -= 1

                self.ram[self.reg[self.sp]] = rtn_index

                self.pc = self.reg[self.ram_read(self.pc + 1)]

            # RET
            if ir == 0b00010001:
                self.pc = self.ram[self.reg[self.sp]]
                self.reg[self.sp] += 1

            # CMP
            if ir == 0b10100111:
                reg_1 = self.reg[self.ram_read(self.pc + 1)]
                reg_2 = self.reg[self.ram_read(self.pc + 2)]

                if reg_1 < reg_2:
                    self.flag = LESS_FLAG

                elif reg_1 > reg_2:
                    self.flag = GREATER_FLAG

                else:
                    self.flag = EQUAL_FLAG

                self.pc += 3

            # JEQ
            if ir == 0b01010101:
                if self.flag == EQUAL_FLAG:
                    self.pc = self.reg[self.ram_read(self.pc + 1)]

                else:
                    self.pc += 2

            # JNE
            if ir == 0b01010110:
                if self.flag != EQUAL_FLAG:
                    self.pc = self.reg[self.ram_read(self.pc + 1)]

                else:
                    self.pc += 2

            # JMP
            if ir == 0b01010100:
                self.pc = self.reg[self.ram_read(self.pc + 1)]

            # ALU OPS -----

            # MUL
            if ir == 0b10100010:
                value_one = self.ram[self.pc + 1]
                value_two = self.ram[self.pc + 2]
                print(f">> Multiply: {self.reg[value_one]} x {self.reg[value_two]}")
                self.alu("MUL", value_one, value_two)
                self.pc += 3

            # ADD
            if ir == 0b10100000:
                value_one = self.ram[self.pc + 1]
                value_two = self.ram[self.pc + 2]
                print(f">> Add: {self.reg[value_one]} + {self.reg[value_two]}")
                self.alu("ADD", value_one, value_two)
                self.pc += 3

            # SUB
            if ir == 0b10100001:
                value_one = self.ram[self.pc + 1]
                value_two = self.ram[self.pc + 2]
                print(f">> Sub: {self.reg[value_one]} - {self.reg[value_two]}")
                self.alu("SUB", value_one, value_two)
                self.pc += 3

            # DIV
            if ir == 0b10100011:
                value_one = self.ram[self.pc + 1]
                value_two = self.ram[self.pc + 2]
                print(f">> Div: {self.reg[value_one]} // {self.reg[value_two]}")
                self.alu("DIV", value_one, value_two)
                self.pc += 3

            # AND
            if ir == 0b10101000:
                value_one = self.ram[self.pc + 1]
                value_two = self.ram[self.pc + 2]
                print(f">> And: {self.reg[value_one]} & {self.reg[value_two]}")
                self.alu("AND", value_one, value_two)
                self.pc += 3

            # OR
            if ir == 0b10101010:
                value_one = self.ram[self.pc + 1]
                value_two = self.ram[self.pc + 2]
                print(f">> Or: {self.reg[value_one]} | {self.reg[value_two]}")
                self.alu("OR", value_one, value_two)
                self.pc += 3

            # XOR
            if ir == 0b10101011:
                value_one = self.ram[self.pc + 1]
                value_two = self.ram[self.pc + 2]
                print(f">> Xor: {self.reg[value_one]} ^ {self.reg[value_two]}")
                self.alu("XOR", value_one, value_two)
                self.pc += 3

            # NOT
            if ir == 0b10101011:
                value_one = self.ram[self.pc + 1]
                print(f">> Not: ~{self.reg[value_one]}")
                self.alu("NOT", value_one)
                self.pc += 2

            # SHL
            if ir == 0b10101100:
                value_one = self.ram[self.pc + 1]
                value_two = self.ram[self.pc + 2]
                print(f">> Shl: {self.reg[value_one]} << {self.reg[value_two]}")
                self.alu("SHL", value_one, value_two)
                self.pc += 3

            # SHR
            if ir == 0b10101101:
                value_one = self.ram[self.pc + 1]
                value_two = self.ram[self.pc + 2]
                print(f">> Shl: {self.reg[value_one]} >> {self.reg[value_two]}")
                self.alu("SHR", value_one, value_two)
                self.pc += 3