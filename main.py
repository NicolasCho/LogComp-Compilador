import sys
from ats import *

#------------------------------------------------------------#

class SymbolTable:
    table = {}
    reserved_words = ["while", "println", "if", "else", "readline", "function", "return"]

    def getter(self, sym):
        try:
            return self.table[sym]
        except:
            raise Exception("Variable not found")
    
    def setter(self, sym, val): 
        if sym == "number":
            raise Exception("Not a valid variable")
        if sym in self.reserved_words:
            raise Exception("{} is a reserved word".format(sym))
        self.table[sym] = val

    def create(self, sym, val):
        if sym in self.table:
            raise Exception("Variable already declared")
        self.table[sym] = val

class FuncTable:
    table = {}

    def getter(self, func_key):
        return self.table[func_key]
    
    def setter(self, func_key, func_value):
        self.table[func_key] = func_value

#---------------------------------------------------------------#

class AuxFunctions:
    symbols = ["+", "-", "*", "/", "(", ")", "=", "\n", "==", ">", "<",
                "|","||", "&","&&", "!", '"', ".", ":", "::", ","]
    types = ["String", "Int"]
    def is_digit(self,word):
        return word >= '0' and word <= "9"
    
    def create_token(self, word):
        if word.isdigit():
            return Token("number", int(word))
        elif word == "":
            return Token("EOF", None)
        elif word in self.types:
            return Token("Type", word)
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
            char = code[curr_char]
            if char == " ":
                if token == "":
                    curr_char += 1
                    continue
                else:
                    curr_char += 1
                    break
            elif char in self.symbols:  #Verifica simbolos
                if char == '"':
                    if token == "(" or token ==".":
                        break
                    while True:
                        token += code[curr_char]
                        curr_char += 1
                        if curr_char == len(code):
                            raise Exception("Missing string end")
                        if code[curr_char] == '"':
                            token += code[curr_char]
                            curr_char += 1
                            break
                    break
                if token == "":
                    token += char
                    curr_char += 1
                    continue
                elif token == "=" or token == "|" or token == "&" or token == ":":
                    if char == '\n':
                        break
                    token += char
                    curr_char += 1
                    if token not in self.symbols:
                        raise Exception("Unrecognizable symbol!")
                    continue
                else:
                    break
            elif char.isdigit():        #Verifica dígitos
                if token in self.symbols:
                    break
                token += char
                curr_char += 1
                continue
            elif (char >= 'a' and char <= 'z') or (char >= 'A' and char <= 'Z') or char == "_":   #Verifica caracteres
                if token in self.symbols:
                    break
                elif token.isdigit():
                    raise Exception("Variable can't start with number")
                else:
                    token += char
                    curr_char += 1
                    continue
            else:
                raise Exception ("Unrecognizable character!")
        return token, curr_char

#----------------------------------------------------#

class Parser(AuxFunctions):
    tokenizer = None

    def parseBlock(self):
        block = Block(None, [])
        while True:
            self.tokenizer.selectNext()
            if self.tokenizer.next.type == "EOF":
                break
            statement_val  = self.parseStatement()
            block.children.append(statement_val)  
        return block
    
    def parseStatement(self):
        curr_token = self.tokenizer.next.type
        return_node = None
        if curr_token == "\n":
            return_node = NoOp(None, None)
        elif curr_token == "println":
            self.tokenizer.selectNext()
            if self.tokenizer.next.type != "(":
                raise Exception ("Syntax error")
            self.tokenizer.selectNext()
            val = self.parseRelExpression()
            if self.tokenizer.next.type != ")":
                raise Exception ("Syntax error")
            self.tokenizer.selectNext()
            return_node = PrintNode(None, [val])
        elif curr_token == "while":
            while_block = Block(None, [])
            self.tokenizer.selectNext()
            condition = self.parseRelExpression()
            if self.tokenizer.next.type != "\n":
                raise Exception("Syntax error")
            while True:
                self.tokenizer.selectNext()
                if self.tokenizer.next.type == "end":
                    break
                statement_val = self.parseStatement()
                while_block.children.append(statement_val)  
            self.tokenizer.selectNext()
            return_node = WhileNode(None, [condition,while_block])
        elif curr_token == "if":
            if_block = Block(None,[])
            else_block = Block(None,[])
            self.tokenizer.selectNext()
            condition = self.parseRelExpression()
            if self.tokenizer.next.type != "\n":
                raise Exception("Syntax error")
            while True:
                self.tokenizer.selectNext()
                if self.tokenizer.next.type == "end" or self.tokenizer.next.type == "else":
                    break
                statement_val = self.parseStatement()
                if_block.children.append(statement_val)
            if self.tokenizer.next.type == "else":
                self.tokenizer.selectNext()
                if self.tokenizer.next.type != "\n":
                    raise Exception("Syntax error")
                while True:
                    self.tokenizer.selectNext()
                    if self.tokenizer.next.type == "end":
                        break
                    statement_val = self.parseStatement()
                    else_block.children.append(statement_val)
            self.tokenizer.selectNext()
            return_node = IfNode(None,[condition,if_block,else_block])

        elif curr_token == "function":
            self.tokenizer.selectNext()
            func_ident = Identifier(self.tokenizer.next.type, [])
            self.tokenizer.selectNext()
            if self.tokenizer.next.type != "(":
                raise Exception ("Error in function declaration")
            self.tokenizer.selectNext()
            arg_list = []
            if self.tokenizer.next.type != ")":
                while True:
                    arg_ident = Identifier(self.tokenizer.next.type, [])
                    self.tokenizer.selectNext()
                    if self.tokenizer.next.type != "::":
                        raise Exception("Must declare argument type")
                    self.tokenizer.selectNext()
                    if self.tokenizer.next.type != "Type":
                        raise Exception("Expected var type")
                    arg_list.append(VarDec(self.tokenizer.next.value, [arg_ident, NoOp(None, None)]))
                    self.tokenizer.selectNext()
                    if self.tokenizer.next.type == ")":
                        break
                    if self.tokenizer.next.type != ",":
                        raise Exception("Arguments must be separated by commas")
                    self.tokenizer.selectNext()
            self.tokenizer.selectNext()  
            if self.tokenizer.next.type != "::":
                raise Exception("Must declare function return type")
            self.tokenizer.selectNext()  
            if self.tokenizer.next.type != "Type":
                raise Exception("Expected function return type")
            func_ret_type =  self.tokenizer.next.value
            self.tokenizer.selectNext()  
            if self.tokenizer.next.type != "\n":
                raise Exception("Must init new line")
            func_block = Block(None,[])
            while True:
                self.tokenizer.selectNext()
                if self.tokenizer.next.type == "end":
                    break
                statement_val = self.parseStatement()
                func_block.children.append(statement_val)
            self.tokenizer.selectNext() 
            return_node = FuncDec(func_ret_type, [func_ident, arg_list, func_block])

        elif curr_token == "return":
            self.tokenizer.selectNext()
            ret_val = self.parseRelExpression()
            return_node = RetNode(None, [ret_val])

        else:
            ident = Identifier(curr_token,[])
            self.tokenizer.selectNext()
            if self.tokenizer.next.type == "=":
                self.tokenizer.selectNext()
                val = self.parseRelExpression()
                return_node = Assignement(None, [ident, val])
            elif self.tokenizer.next.type == "::":
                self.tokenizer.selectNext()
                if self.tokenizer.next.type != "Type":
                   raise Exception("Expected var type")
                var_type = self.tokenizer.next.value
                self.tokenizer.selectNext()
                if self.tokenizer.next.type == "=":
                    self.tokenizer.selectNext()
                    val = self.parseRelExpression()
                    return_node = VarDec(var_type, [ident, val])
                else:
                    return_node = VarDec(var_type, [ident, NoOp(None, None)])
            elif self.tokenizer.next.type == "(":
                call_node = FuncCall(ident.value, [])
                self.tokenizer.selectNext()
                if self.tokenizer.next.type != ")":
                    while True:
                        ret_val = self.parseRelExpression()
                        call_node.children.append(ret_val)
                        if self.tokenizer.next.type == ")":
                            break
                        if self.tokenizer.next.type != ",":
                            raise Exception("Arguments must be separated by commas")
                        self.tokenizer.selectNext()
                return_node = call_node
                self.tokenizer.selectNext()
            else:
                raise Exception ("Identifier error")
            
        if self.tokenizer.next.type != "\n":
            raise Exception("Syntax error")
        return return_node
    
    def parseRelExpression(self):
        val = self.parseExpression()
        while True: 
            token_type = self.tokenizer.next.type
            if token_type == "==" or token_type == ">" or token_type == "<":
                op = self.tokenizer.next.type
                self.tokenizer.selectNext()
                ret_val = self.parseExpression()
                val = BinOp(op,[val, ret_val])
            else:
                break
        if val is None:
            raise Exception("Empty expression")
        return val

    def parseExpression(self):
        val =  self.parseTerm()
        while True: 
            token_type = self.tokenizer.next.type
            if token_type == "+" or token_type == "-" or token_type == "||":
                op = self.tokenizer.next.type
                self.tokenizer.selectNext()
                ret_val = self.parseTerm()
                val = BinOp(op,[val, ret_val])
            elif token_type == ".":
                op = self.tokenizer.next.type
                self.tokenizer.selectNext()
                ret_val = self.parseTerm()
                val = ConcOp(None,[val, ret_val])
            else:
                break
        if val is None:
            raise Exception("Empty expression")
        return val

    def parseTerm(self):
        val = self.parseFactor()
        while True:
            #self.tokenizer.selectNext()
            token_type = self.tokenizer.next.type
            if self.tokenizer.next.type == "number":
                raise Exception("A number cannot be followed by another number")
            if token_type == '*' or token_type == '/' or token_type == '&&':
                op = self.tokenizer.next.type
                self.tokenizer.selectNext()
                ret_val = self.parseFactor()
                val = BinOp(op, [val, ret_val])
            else:
                break
        return val
    
    def parseFactor(self):
        #self.tokenizer.selectNext()
        token_type = self.tokenizer.next.type
        if token_type == "number":
            ret_node = IntVal(self.tokenizer.next.value, None)
            self.tokenizer.selectNext()
        elif token_type[0] == '"':
            ret_node = StrVal(self.tokenizer.next.type[1:-1], None)
            self.tokenizer.selectNext()
        elif token_type == "+" or token_type == "-" or token_type == "!": 
            op_value = token_type
            self.tokenizer.selectNext()
            ret_val = self.parseFactor()
            ret_node = UnOp(op_value, [ret_val])
            #self.tokenizer.selectNext()
        elif token_type == "(":
            self.tokenizer.selectNext()
            # print(self.tokenizer.next.type)
            ret_val = self.parseRelExpression()
            if self.tokenizer.next.type != ")":
                raise Exception("Must close parenthesis")
            ret_node = ret_val
            self.tokenizer.selectNext()
        elif token_type == "readline":
            self.tokenizer.selectNext()
            if self.tokenizer.next.type != "(":
                raise Exception ("Syntax error")
            self.tokenizer.selectNext()
            if self.tokenizer.next.type != ")":
                raise Exception ("Syntax error")
            ret_node = ReadlnNode(None,[]) 
            self.tokenizer.selectNext()
        else:
            ident_node = Identifier(token_type, [])
            self.tokenizer.selectNext()
            if self.tokenizer.next.type == "(":
                call_node = FuncCall(ident_node.value, [])
                self.tokenizer.selectNext()
                if self.tokenizer.next.type != ")":
                    while True:
                        ret_val = self.parseRelExpression()
                        call_node.children.append(ret_val)
                        if self.tokenizer.next.type == ")":
                            break
                        if self.tokenizer.next.type != ",":
                            raise Exception("Arguments must be separated by commas")
                        self.tokenizer.selectNext()
                ret_node = call_node
                self.tokenizer.selectNext()
            else:
                ret_node = ident_node
        return ret_node


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
    b.Evaluate(symbol_table)