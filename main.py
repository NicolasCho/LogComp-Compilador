import sys
import re
from abc import ABC, abstractmethod

class AuxFunctions:
    symbols = ["+", "-", "*", "/", "(", ")"]

    def is_digit(self,word):
        return word >= '0' and word <= "9"

    def is_symbol(self, word):
        return word in self.symbols
    
    def validate_word(self, word):
        return (self.is_digit(word) or self.is_symbol(word) or word==" ")
    
    def create_token(self, word):
        if word.isdigit():
            return Token("number", int(word))
        elif word == "":
            return Token("EOF", None)
        else:
            return Token(word, None)

class Token:
    def __init__(self, type, value):
        self.type = type
        self.value = value 

class Tokenizer(AuxFunctions):
    def __init__(self, source, position, next):
        self.source = source
        self.position = position
        self.next = next #Token

    def selectNext(self):
        next_token_literal, pos = self.run_tokenizer(self.source, self.position)
        self.position = pos
        self.next = self.create_token(next_token_literal)
        return self.next
    
    def run_tokenizer(self, code, curr_char):
        token = ""
        while curr_char < len(code):
            if not self.validate_word(code[curr_char]):
                raise Exception("Invalid character")
            if code[curr_char] == " ":
                if token != "":
                    curr_char += 1
                    break
                else:
                    curr_char += 1
                    continue

            if self.is_digit(code[curr_char]):
                token += code[curr_char]
            else:
                if token == "":
                    token = code[curr_char]
                    curr_char += 1
                    break
                else:
                    break
                
            curr_char += 1
        return token, curr_char

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
        else:
            return int(self.children[0].Evaluate() / self.children[1].Evaluate()) 

class UnOp(Node):
    def Evaluate(self):
        if self.value == "+":
            return self.children[0].Evaluate() 
        return -self.children[0].Evaluate()

class IntVal(Node):
    def Evaluate(self):
        return self.value    

class NoOp(Node):
    def Evaluate(self):
        return None

class Parser(AuxFunctions):
    tokenizer = None

    def parseExpression(self, primary_parse = True):
        val =  self.parseTerm()
        while True: 
            if primary_parse and self.tokenizer.next.type ==")":
                raise Exception("Expression without opening parenthesis")
            if self.tokenizer.next.type == "EOF" or self.tokenizer.next.type ==")":
                break
            op = self.tokenizer.next.type
            ret_val = self.parseTerm()
            val = BinOp(op,[val, ret_val])
        if val is None:
            raise Exception("Empty expression")
        return val

    def parseTerm(self):
        val = self.parseFactor()
        while True:
            self.tokenizer.selectNext()
            if self.tokenizer.next.type == "number":
                raise Exception("A number cannot be followed by another number")
            if self.tokenizer.next.type == '*' or self.tokenizer.next.type == '/':
                op = self.tokenizer.next.type
                ret_val = self.parseFactor()
                val = BinOp(op, [val, ret_val])
            else:
                break
        return val
    
    def parseFactor(self):
        self.tokenizer.selectNext()
        token_type = self.tokenizer.next.type
        if token_type == "number":
            return IntVal(self.tokenizer.next.value, None)
        elif token_type == "+" or token_type == "-":
            op_value = token_type
            ret_val = self.parseFactor()
            return UnOp(op_value, [ret_val])
        elif token_type == "(":
            ret_val = self.parseExpression(primary_parse=False)
            if self.tokenizer.next.type != ")":
                raise Exception("Must close parenthesis")
            return ret_val
        else:
            raise Exception ("ERROR")

    def run(self, code):
        pre_proc = PrePro.filter(code)
        Parser.tokenizer = Tokenizer(pre_proc, 0, Token(None, None))
        return self.parseExpression()   

class PrePro:
    @staticmethod
    def filter(source):
        i = 0
        while i < len(source):
            if source[i] == "#":
                break
            i += 1
        return source[:i]

if __name__ == "__main__":
    a = Parser()
    file = sys.argv[1]
    with open(file, 'r') as f:
        expression = f.readline()
    f.close()
    b = a.run(expression)
    print(b.Evaluate())