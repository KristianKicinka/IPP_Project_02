# Project : IPP Projekt - 2.úloha Interpret.
# @author Kristián Kičinka (xkicin02)

# Objekt inštrukcia, združuje dostupné dáta o inštrukciách
class Instruction:

    def __init__(self, opcode, order):
        self.opcode = opcode
        self.order = order
        self.arguments = []

    def get_opcode(self):
        return self.opcode

    def get_order(self):
        return self.order

    def add_argument(self, argument):
        self.arguments.append(argument)

    def get_arguments(self):
        return self.arguments
