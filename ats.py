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
        if self.value == "+":
            return self.children[0].Evaluate() + self.children[1].Evaluate()
        elif self.value == "-":
            return self.children[0].Evaluate() - self.children[1].Evaluate() 
        elif self.value == "*":
            return self.children[0].Evaluate() * self.children[1].Evaluate() 
        elif self.value == "&&":
            return self.children[0].Evaluate() and self.children[1].Evaluate()
        elif self.value == "||":
            return self.children[0].Evaluate() or self.children[1].Evaluate()
        elif self.value == "==":
            return self.children[0].Evaluate() == self.children[1].Evaluate()
        elif self.value == ">":
            return self.children[0].Evaluate() > self.children[1].Evaluate()
        elif self.value == "<":
            return self.children[0].Evaluate() < self.children[1].Evaluate()
        else:
            return int(self.children[0].Evaluate() / self.children[1].Evaluate()) 

class UnOp(Node):
    def Evaluate(self):
        if self.value == "+":
            return self.children[0].Evaluate() 
        elif self.value == "-":
            return -self.children[0].Evaluate()
        else:
            return not self.children[0].Evaluate()

class IntVal(Node):
    def Evaluate(self):
        return self.value    

class NoOp(Node):
    def Evaluate(self):
        return None
    
class Identifier(Node):
    def Evaluate(self):
        return symbol_table.getter(self.value)

class PrintNode(Node):
    def Evaluate(self):
        print(self.children[0].Evaluate())

class Assignement(Node):
    def Evaluate(self):
        symbol_table.setter(self.children[0].value, self.children[1].Evaluate())

class Block(Node):
    def Evaluate(self):
        for child in self.children:
            child.Evaluate()

class ReadlnNode(Node):
    def Evaluate(self):
        return int(input())
    
class WhileNode(Node):
    def Evaluate(self):
        while self.children[0].Evaluate():
            self.children[1].Evaluate()

class IfNode(Node):
    def Evaluate(self):
        if self.children[0].Evaluate():
            self.children[1].Evaluate()
        else:
            self.children[2].Evaluate()
