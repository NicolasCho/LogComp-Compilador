from abc import ABC, abstractmethod
from main import SymbolTable

global symbol_table
symbol_table = SymbolTable()

class Node(ABC):
    def __init__(self, value, children):
        self.value = value
        self.children = children
   
    @abstractmethod
    def Evaluate(self):
        pass

class BinOp(Node):
    def Evaluate(self):
        #Avalia se os tipos são compatíveis
        if self.children[0].Evaluate()[0] != self.children[1].Evaluate()[0]:
            raise Exception ("Incompatible types")

        if self.value == "+":
            return ("Int",self.children[0].Evaluate()[1] + self.children[1].Evaluate()[1])
        elif self.value == "-":
            return ("Int",self.children[0].Evaluate()[1] - self.children[1].Evaluate()[1])
        elif self.value == "*":
            return ("Int",self.children[0].Evaluate()[1] * self.children[1].Evaluate()[1])
        elif self.value == "&&":
            return ("Int",self.children[0].Evaluate()[1] and self.children[1].Evaluate()[1])
        elif self.value == "||":
            return ("Int",self.children[0].Evaluate()[1] or self.children[1].Evaluate()[1])
        elif self.value == "==":
            return ("Int",self.children[0].Evaluate()[1] == self.children[1].Evaluate()[1])
        elif self.value == ">":
            return ("Int",self.children[0].Evaluate()[1] > self.children[1].Evaluate()[1])
        elif self.value == "<":
            return ("Int",self.children[0].Evaluate()[1] < self.children[1].Evaluate()[1])
        else:
            return ("Int",int(self.children[0].Evaluate()[1] / self.children[1].Evaluate()[1]))

class ConcOp(Node):
    def Evaluate(self):
        return ("Str", str(self.children[0].Evaluate()[1]) + str(self.children[1].Evaluate()[1]))

class UnOp(Node):
    def Evaluate(self):
        if self.value == "+":
            return ("Int",self.children[0].Evaluate()[1])
        elif self.value == "-":
            return ("Int",-self.children[0].Evaluate()[1])
        else:
            return ("Int",not self.children[0].Evaluate()[1])

class IntVal(Node):
    def Evaluate(self):
        return ("Int",self.value)
    
class StrVal(Node):
    def Evaluate(self):
        return ("String",self.value)

class NoOp(Node):
    def Evaluate(self):
        return None
    
class Identifier(Node):
    def Evaluate(self):
        return symbol_table.getter(self.value)

class PrintNode(Node):
    def Evaluate(self):
        print(self.children[0].Evaluate()[1])

class Assignement(Node):
    def Evaluate(self):
        symbol_table.setter(self.children[0].value, self.children[1].Evaluate())

class Block(Node):
    def Evaluate(self):
        for child in self.children:
            child.Evaluate()

class ReadlnNode(Node):
    def Evaluate(self):
        return ("Int",int(input()))
    
class WhileNode(Node):
    def Evaluate(self):
        while self.children[0].Evaluate()[1]:
            self.children[1].Evaluate()

class IfNode(Node):
    def Evaluate(self):
        if self.children[0].Evaluate()[1]:
            self.children[1].Evaluate()
        else:
            self.children[2].Evaluate()

class VarDeclar(Node):
    def Evaluate(self):
        if self.value == "Int":
            if self.children[1].Evaluate() is None:
                symbol_table.setter(self.children[0].value, (self.value, 0))
            else:
                if self.children[1].Evaluate()[0]!="Int":
                    raise Exception ("Not an Integer")
                symbol_table.setter(self.children[0].value, (self.value, self.children[1].Evaluate()[1]))
        else:
            if self.children[1].Evaluate() is None:
                symbol_table.setter(self.children[0].value, (self.value, ""))
            else:
                if self.children[1].Evaluate()[0]!="String":
                    raise Exception ("Not a String")
                symbol_table.setter(self.children[0].value, (self.value, self.children[1].Evaluate()[1]))