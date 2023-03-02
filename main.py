import sys
import re

class AuxFunctions:
    def is_number(self,word):
        return word >= '0' and word <= "9"

    def is_operator(self, word):
        return word == "+" or word == "-" or word == "*" or word == "/"
    
    def validate_word(self, word):
        return (self.is_number(word) or self.is_operator(word) or word==" ")
    
    def calculator(self, a, b,operator):
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
            return Token("operator", word)

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
            elif self.is_operator(code[curr_char]):
                if token == "":
                    token = code[curr_char]
                    curr_char += 1
                    break
                else:
                    break
            else:
                token += code[curr_char]
            curr_char += 1
        return token, curr_char

class Parser(AuxFunctions):
    tokenizer = None

    def parseExpression(self):
        if self.is_operator(self.tokenizer.next.value):
            raise Exception("First token must be a number")
        val =  self.parseTerm()
        while True:  
            if self.tokenizer.next.type == "EOF":
                break
            op = self.tokenizer.next.value
            self.tokenizer.selectNext()
            if self.tokenizer.next.type != "number":
                raise Exception("An operator can only be followed by a number")
            if op == '+' or op == '-':
                val = self.calculator(val, self.parseTerm(), op)
        if val is None:
            raise Exception("Empty expression")
        return val

    def parseTerm(self):
        val = self.tokenizer.next.value
        self.tokenizer.selectNext()
        while True:
            if self.tokenizer.next.type == "number":
                raise Exception("A number cannot be followed by another number")
            if self.tokenizer.next.value == '*' or self.tokenizer.next.value == '/':
                op = self.tokenizer.next.value
                self.tokenizer.selectNext()
                if self.tokenizer.next.type != "number":
                    raise Exception("An operator can only be followed by a number")
                val = self.calculator(val, self.tokenizer.next.value, op)
                self.tokenizer.selectNext()
            else:
                break
        return val
    
    def run(self, code):
        pre_proc = PrePro.filter(code)
        Parser.tokenizer = Tokenizer(pre_proc, 0, Token(None, None))
        self.tokenizer.selectNext()
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