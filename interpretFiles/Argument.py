# Project : IPP Projekt - 2.úloha Interpret.
# @author Kristián Kičinka (xkicin02)

# Objekt argument združuje a uchováva dáta o argumentoch programu.
class Argument:

    def __init__(self, name, arg_type, value):
        self.name = name
        self.arg_type = arg_type
        self.value = value

    def get_arg_type(self):
        return self.arg_type

    def get_value(self):
        return self.value

    def get_name(self):
        return self.name
