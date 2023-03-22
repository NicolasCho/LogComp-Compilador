import sys
from ats import *

class AuxFunctions:
    symbols = ["+", "-", "*", "/", "(", ")","=","\n"]

    def is_digit(self,word):
        return word >= '0' and word <= "9"
    
    def create_token(self, word):
        if word.isdigit():
            return Token("number", int(word))
        elif word == "":
            return Token("EOF", None)
        else:
            return Token(word, None)
        
class SymbolTable:
    table = {}

    def getter(self, sym):
        try:
            return self.table[sym]
        except:
            raise Exception("Variable not found")
    
    def setter(self, sym, val):
        if sym == "number":
            raise Exception("Not a valid variable")
        self.table[sym] = val

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
            char = code[curr_char]
            if char == " ":
                if token == "":
                    curr_char += 1
                    continue
                else:
                    curr_char += 1
                    break
            elif char in self.symbols:
                if token == "":
                    token = char
                    curr_char += 1
                    break
                else:
                    break
            elif char.isdigit():
                token += char
                curr_char += 1
                continue
            else:
                if token.isdigit():
                    raise Exception("Variable can't start with number")
                else:
                    token += char
                    curr_char += 1
                    continue
        return token, curr_char

class Parser(AuxFunctions):
    tokenizer = None

    def parseBlock(self):
        block = Block(None, [])
        val = self.parseStatement()
        while True:
            block.children.append(val)
            if self.tokenizer.next.type == "EOF":
                break
            elif self.tokenizer.next.type == "\n":
                val  = self.parseStatement()
            else:
                raise Exception("Error")
        return block
    
    def parseStatement(self):
        self.tokenizer.selectNext()
        curr_token = self.tokenizer.next.type
        if curr_token == "\n" or curr_token =="EOF":
            return NoOp(None, None)
        elif curr_token == "println":
            self.tokenizer.selectNext()
            if self.tokenizer.next.type != "(":
                raise Exception ("Syntax error")
            
            val = self.parseExpression()
            
            if self.tokenizer.next.type != ")":
                raise Exception ("Syntax error")
            self.tokenizer.selectNext()
            return PrintNode(None, [val])
        else:
            ident = Identifier(curr_token,[])
            self.tokenizer.selectNext()
            if self.tokenizer.next.type != "=":
                raise Exception("Assignement error")
            val = self.parseExpression()
            return Assignement(None, [ident, val])

    def parseExpression(self):
        val =  self.parseTerm()
        while True: 
            if self.tokenizer.next.type != "+" and self.tokenizer.next.type !="-":
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
            ret_val = self.parseExpression()
            if self.tokenizer.next.type != ")":
                raise Exception("Must close parenthesis")
            return ret_val
        else:
            return Identifier(token_type, [])

    def run(self, code):
        pre_proc = PrePro.filter(code)
        Parser.tokenizer = Tokenizer(pre_proc, 0, Token(None, None))
        return self.parseBlock()   

class PrePro:
    @staticmethod
    def filter(source):        
        source_proc = ""
        write = True
        i = 0
        while i < len(source):
            if source[i] == "#":
                write = False
            elif source[i] == "\n":
                write = True
            if write:
                source_proc += source[i]
            i += 1
        return source_proc

if __name__ == "__main__":
    a = Parser()
    file = sys.argv[1]
    with open(file, 'r') as f:
        code = f.read()
    b = a.run(code)
    b.Evaluate()