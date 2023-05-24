from abc import ABC, abstractmethod
from main import SymbolTable, FuncTable

global symbol_table
global func_table
symbol_table = SymbolTable()
func_table = FuncTable()

class Node(ABC):
    def __init__(self, value, children):
        self.value = value
        self.children = children
   
    @abstractmethod
    def Evaluate(self):
        pass

class BinOp(Node):
    def Evaluate(self,scope):
        if self.value == "==":
            return ("Int",int(self.children[0].Evaluate(scope)[1] == self.children[1].Evaluate(scope)[1]))
        
        #Avalia se os tipos são compatíveis
        if self.children[0].Evaluate(scope)[0] != self.children[1].Evaluate(scope)[0]:
            raise Exception ("Incompatible types")

        if self.value == "+":
            return ("Int",self.children[0].Evaluate(scope)[1] + self.children[1].Evaluate(scope)[1])
        elif self.value == "-":
            return ("Int",self.children[0].Evaluate(scope)[1] - self.children[1].Evaluate(scope)[1])
        elif self.value == "*":
            return ("Int",self.children[0].Evaluate(scope)[1] * self.children[1].Evaluate(scope)[1])
        elif self.value == "&&":
            return ("Int",self.children[0].Evaluate(scope)[1] and self.children[1].Evaluate(scope)[1])
        elif self.value == "||":
            return ("Int",self.children[0].Evaluate(scope)[1] or self.children[1].Evaluate(scope)[1])
        elif self.value == ">":
            return ("Int",int(self.children[0].Evaluate()[1] > self.children[1].Evaluate()[1]))
        elif self.value == "<":
            return ("Int",int(self.children[0].Evaluate()[1] < self.children[1].Evaluate()[1]))
        else:
            return ("Int",int(self.children[0].Evaluate(scope)[1] / self.children[1].Evaluate(scope)[1]))

class ConcOp(Node):
    def Evaluate(self, scope):
        return ("Str", str(self.children[0].Evaluate(scope)[1]) + str(self.children[1].Evaluate(scope)[1]))

class UnOp(Node):
    def Evaluate(self, scope):
        if self.value == "+":
            return ("Int",self.children[0].Evaluate(scope)[1])
        elif self.value == "-":
            return ("Int",-self.children[0].Evaluate(scope)[1])
        else:
            return ("Int",not self.children[0].Evaluate(scope)[1])

class IntVal(Node):
    def Evaluate(self,  scope):
        return ("Int",self.value)
    
class StrVal(Node):
    def Evaluate(self, scope):
        return ("String",self.value)

class NoOp(Node):
    def Evaluate(self, scope):
        return None
    
class Identifier(Node):
    def Evaluate(self, scope):
        return scope.getter(self.value)

class PrintNode(Node):
    def Evaluate(self, scope):
        print(self.children[0].Evaluate(scope)[1])

class Assignement(Node):
    def Evaluate(self, scope):
        value = self.children[1].Evaluate()
        if self.children[0].value in scope.table:
            if value[0] != scope.table[self.children[0].value][0]: 
                raise Exception("Trying to assign different variable type")
        scope.setter(self.children[0].value, value)

class Block(Node):
    def Evaluate(self, scope):
        for child in self.children:
            if isinstance(child, RetNode):
                return child.Evaluate(scope)
            child.Evaluate(scope)

class ReadlnNode(Node):
    def Evaluate(self):
        return ("Int",int(input()))
    
class WhileNode(Node):
    def Evaluate(self, scope):
        while self.children[0].Evaluate(scope)[1]:
            self.children[1].Evaluate(scope)

class IfNode(Node):
    def Evaluate(self, scope):
        if self.children[0].Evaluate(scope)[1]:
            self.children[1].Evaluate(scope)
        else:
            self.children[2].Evaluate(scope)

class VarDec(Node):
    def Evaluate(self, scope):
        var_ident = self.children[0].value
        var_value = self.children[1].Evaluate(scope)

        if self.value == "Int":
            if var_value is None:
                scope.create(var_ident, (self.value, 0))
            else:
                if var_value[0]!="Int":
                    raise Exception ("Not an Integer")
                scope.create(var_ident, (self.value, var_value[1]))
        else:
            if var_value is None:
                scope.create(var_ident, (self.value, ""))
            else:
                if var_value[0]!="String":
                    raise Exception ("Not a String")
                scope.create(var_ident, (self.value, var_value[1]))

class FuncDec(Node):
    #children[0]: Identifier || children[1]: [VarDec, VarDec, ...]  || children[2]: Block 
    def Evaluate(self):
        if len(self.children) != 3:
            raise Exception("Error in function declaration")
        func_table.setter(self.children[0].value, (self.value, self))

class FuncCall(Node):
    #children: [arg, arg, arg, ...]
    def Evaluate(self):
        func_entry = FuncTable.getter(self.value) # Retorna: ("nome_func", FuncNode)
        if len(self.children) != len(func_entry[1].children[1]):
            raise Exception("Number of arguments from function declaration and function call differ")
        func_scope = SymbolTable()
        for arg_dec, arg_val in zip(func_entry[1].children[1], self.children):
            arg_dec.Evaluate(func_scope)                         # Eval dos vardec (coloca na nova st) [arg = VarDec]
            func_scope.setter(arg_dec.children[0].value, arg_val.Evaluate())  # Eval no escopo global
        return func_entry[1].children[2].Evaluate(func_scope)    # Eval do bloco em escopo local
                                                                 # Espera um "return" dentro do bloco

class RetNode(Node):
    def Evaluate(self, scope):
        return self.children.Evaluate(scope)    # Deve fazer eval em escopo local