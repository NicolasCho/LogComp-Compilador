import sys
import re

class AuxFunctions:
    def is_number(self,word):
        return word >= '0' and word <= "9"

    def is_operator(self, word):
        return word == "+" or word == "-"
    
    def validate_word(self, word):
        return (self.is_number(word) or self.is_operator(word) or word==" ")
    
    def calculator(self, a, b,operator):
        if operator == '+':
            return a + b
        return a - b
    
    def create_token(self, word):
        if word.isdigit():
            return Token("number", int(word))
        elif word == "":
            return Token("EOF", None)
        else:
            return Token("operator", word)
 
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

class Parser(AuxFunctions):
    tokenizer = None

    def parseExpression(self):
        n_token = 0
        value = 0
        while True:
            curr_token = self.tokenizer.next
            next_token = Parser.tokenizer.selectNext()
            if n_token == 0:
                if next_token.type == "operator":
                    raise Exception("First token must be a number")
                value = next_token.value
            if curr_token.type == "number":
                if next_token.type == "number":
                    raise Exception("A number cannot be followed by another number")
            if curr_token.type == "operator":
                if next_token.type != "number":
                    raise Exception("An operator can only be followed by a number")
                value = self.calculator(value, next_token.value, curr_token.value)
            n_token += 1
            if next_token.type == "EOF":
                break
        if value is None:
            return 0
        return value
    
    def run(self, code):
        Parser.tokenizer = Tokenizer(code, 0, Token(None, None))
        return self.parseExpression()   

if __name__ == "__main__":
    a = Parser()
    b = a.run(sys.argv[1])
    print(b)
    