import sys
import re

class Compiler(object):
    def __init__(self, argument):
        self.argument = argument
        self.order = self.parser()
        self.result = self.calculator()

    @property
    def argument(self): 
        return self._argument
    
    @argument.setter
    def argument(self,value):
        for word in value:
            if not self.is_number(word):
                if not self.is_operation(word) and word !=" ":
                    raise Exception("Not a number or operator")
        self._argument = value

    @property
    def order(self):
        return self._order

    @order.setter
    def order(self, value):
        if not value:
            raise Exception("Empty expression")

        i = 0
        for element in value:
            if (i%2 == 0 and self.is_operation(element)) or (i%2 == 1 and self.is_number(element)):
                raise Exception("Invalid order of operands")
            i += 1
        if self.is_operation(value[-1]):
            raise Exception("Expression cannot end with operator")
        
        self._order = value

    def is_number(self, word):
        return word >= '0' and word <= "9"

    def is_operation(self, word):
        return word == "+" or word == "-"
                
    def parser(self):
        units = re.split('([+ -])', self.argument)
        units = [item for item in units if item != ' ' and item != '']
        return units             
                
    def adder(self,a ,b):
        return a + b
    
    def subtractor(self, a, b):
        return a - b

    def calculator(self):
        total = int(self.order[0])
        i = 0
        for element in self.order:
            if element == "+":
                total = self.adder(total, int(self.order[i+1]))
            elif element == "-":
                total = self.subtractor(total, int(self.order[i+1]))
            i += 1
        return total
            

if __name__ == "__main__":
    a = Compiler(sys.argv[1])
    print(a.result)