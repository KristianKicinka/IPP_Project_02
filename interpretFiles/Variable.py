# Project : IPP Projekt - 2.úloha Interpret.
# @author Kristián Kičinka (xkicin02)

# Objekt Variable uchováva dáta o premenných programu.
class Variable:
    def __init__(self, name):
        self.name = name
        self.type = None
        self.value = None

    def get_name(self):
        return self.name

    def get_type(self):
        return self.type

    def get_value(self):
        return self.value

    def set_name(self, name):
        self.name = name

    def set_type(self, var_type):
        self.type = var_type

    def set_value(self, value):
        self.value = value
