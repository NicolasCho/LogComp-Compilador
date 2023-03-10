import sys
import re

class AuxFunctions:
    symbols = ["+", "-", "*", "/", "(", ")"]

    def is_digit(self,word):
        return word >= '0' and word <= "9"

    def is_symbol(self, word):
        return word in self.symbols
    
    def validate_word(self, word):
        return (self.is_digit(word) or self.is_symbol(word) or word==" ")
    
    def calculator(self, a, b, operator):
        if operator == '+':
            return a + b
        elif operator == '-':
            return a - b
        elif operator == '*':
            return a * b
        return int(a / b)
    
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
                    break
                else:
                    curr_char += 1
                    pass

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

class Parser(AuxFunctions):
    tokenizer = None

    def parseExpression(self):
        val =  self.parseTerm()
        while True: 
            if self.tokenizer.next.type == "EOF" or self.tokenizer.next.type ==")":
                break
            op = self.tokenizer.next.type
            ret_val = self.parseTerm()
            val = self.calculator(val, ret_val, op)
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
                val = self.calculator(val, ret_val, op)
            else:
                break
        return val
    
    def parseFactor(self):
        self.tokenizer.selectNext()
        token_type = self.tokenizer.next.type
        if token_type == "number":
            return self.tokenizer.next.value
        elif token_type == "+" or token_type == "-":
            op_value = token_type
            ret_val = self.parseFactor()
            if op_value == "-":
                return -ret_val
            else:
                return ret_val
        elif token_type == "(":
            ret_val = self.parseExpression()
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
    b = a.run(sys.argv[1])
    print(b)