from abc import ABC, abstractmethod
from main import SymbolTable
import globals

global symbol_table
symbol_table = SymbolTable()

def writeASM(asm_code): 
    with open(globals.asm_file, "a") as asm:
        asm.write("\n" + asm_code)

class Node(ABC):
    i = 0
    def __init__(self, value, children):
        self.value = value
        self.children = children
        self.id = self.newId()

 
    def newId(self):
        Node.i += 1
        return Node.i

    @abstractmethod
    def Evaluate(self):
        pass

class BinOp(Node):
    def Evaluate(self):
        # if self.value == "==":
        #     return ("Int",int(self.children[0].Evaluate()[1] == self.children[1].Evaluate()[1]))
        
        # #Avalia se os tipos são compatíveis
        # if self.children[0].Evaluate()[0] != self.children[1].Evaluate()[0]:
        #     raise Exception ("Incompatible types")

        left_eval = self.children[0].Evaluate()
        writeASM("PUSH EBX")
        right_eval = self.children[1].Evaluate()
        writeASM("POP EAX")

        if self.value == "+":
            writeASM("ADD EAX, EBX")
            writeASM("MOV EBX, EAX")
        elif self.value == "-":
            writeASM("SUB EAX, EBX")
            writeASM("MOV EBX, EAX")
        elif self.value == "*":
            writeASM("IMUL EBX")
            writeASM("MOV EBX, EAX")
        elif self.value == "&&":
            writeASM("AND EAX, EBX")
            writeASM("MOV EBX, EAX")
        elif self.value == "||":
            writeASM("OR EAX, EBX")
            writeASM("MOV EBX, EAX")
        elif self.value == "==":
            writeASM("CMP EAX, EBX")
            writeASM("CALL binop_je")
        elif self.value == ">":
            writeASM("CMP EAX, EBX")
            writeASM("CALL binop_jg")
        elif self.value == "<":
            writeASM("CMP EAX, EBX")
            writeASM("CALL binop_jl")
        elif self.value == "/":
            writeASM("DIV EBX")
            writeASM("MOV EBX, EAX")
        return ("Int",None)
    
#Não implementado para asm
class ConcOp(Node):
    def Evaluate(self):
        return ("Str", str(self.children[0].Evaluate()[1]) + str(self.children[1].Evaluate()[1]))

class UnOp(Node):
    def Evaluate(self):
        child_value = self.children[0].Evaluate()
        if self.value == "+":
            writeASM("ADD EBX, 0")
            return ("Int",None)
        elif self.value == "-":
            writeASM("MOV EAX, {}".format(child_value[1]))
            writeASM("MOV EBX, -1")
            writeASM("IMUL EBX")
            writeASM("MOV EBX, EAX")
            return ("Int", None)
        else:
            writeASM("NEG EBX")
            return ("Int", None)

class IntVal(Node):
    def Evaluate(self):
        writeASM ("MOV EBX, {}".format(self.value))
        return ("Int",None)

#Não implementado para asm
class StrVal(Node):
    def Evaluate(self):
        return ("String",self.value)

class NoOp(Node):
    def Evaluate(self):
        return None
    
class Identifier(Node):
    def Evaluate(self):
        ident_val = symbol_table.getter(self.value)
        writeASM("MOV EBX, [EBP - {}]".format(ident_val[2]))
        #return ident_val

class PrintNode(Node):
    def Evaluate(self):
        print_val = self.children[0].Evaluate()
        writeASM("PUSH EBX")
        writeASM("CALL print")
        writeASM("POP EBX")
        #print(print_val[1])

class Assignement(Node):
    def Evaluate(self):
        symbol = self.children[0].value
        value = self.children[1].Evaluate()  #Faz o asm do filho da direita (MOV EBX, value)
        if symbol in symbol_table.table:    # Se o símbolo já existe na table
            if value[0] != symbol_table.table[self.children[0].value][0]: # Se os tipos são divergentes
                raise Exception("Trying to assign different variable type")
            sp = symbol_table.getter(symbol)[2] 
            writeASM("MOV [EBP-{}], EBX".format(sp)) 
            #symbol_table.setter(symbol, ([value[0], value[1], sp]))
        else:
            sp = symbol_table.sp
            writeASM("PUSH DWORD 0")
            # writeASM("MOV [EBP-{}], EBX".format(sp)) 
            symbol_table.declaration(symbol, ([value[0], value[1], symbol_table.sp]))


class Block(Node):
    def Evaluate(self):
        for child in self.children:
            child.Evaluate()

# Não implementado
class ReadlnNode(Node):
    def Evaluate(self):
        return ("Int",int(input()))
    
class WhileNode(Node):
    def Evaluate(self):
        writeASM("LOOP_{}:".format(self.id))
        left_child_eval = self.children[0].Evaluate()
        writeASM("CMP EBX, False")
        writeASM("JE EXIT_{}".format(self.id))
        right_child_eval = self.children[1].Evaluate()
        writeASM("JMP LOOP_{}".format(self.id))
        writeASM("EXIT_{}:".format(self.id))

        # while self.children[0].Evaluate()[1]:
        #     self.children[1].Evaluate()

class IfNode(Node):
    def Evaluate(self):
        writeASM("IF_{}:".format(self.id))
        left_child_eval = self.children[0].Evaluate()
        writeASM("CMP EBX, False")
        if len(self.children[2].children)==0:  #  Apenas if
            writeASM("JE EXIT_{}".format(self.id))
            self.children[1].Evaluate()
            writeASM("JMP EXIT_{}".format(self.id))
            writeASM("EXIT_{}:".format(self.id))
        else:                              # Condição if/else presente
            writeASM("JE ELSE_{}".format(self.id))
            self.children[1].Evaluate()
            writeASM("JMP EXIT_{}".format(self.id))
            writeASM("ELSE_{}:".format(self.id))
            self.children[2].Evaluate()
            writeASM("EXIT_{}:".format(self.id))

class VarDeclar(Node):
    def Evaluate(self):
        sp = symbol_table.sp
        writeASM("PUSH DWORD 0")
        symbol_table.declaration(self.children[0].value, (self.value, None, sp))