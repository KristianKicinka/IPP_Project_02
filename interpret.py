import re
import argparse
import sys
import xml.etree.ElementTree as ET

DEFINED_INSTRUCTIONS = {"DEFVAR": 1, "POPS": 1, "MOVE": 2, "INT2CHAR": 2, "STRLEN": 2, "TYPE": 2, "NOT": 2, "READ": 2,
                        "ADD": 3, "SUB": 3, "MUL": 3, "IDIV": 3, "LT": 3, "GT": 3, "EQ": 3, "AND": 3, "OR": 3,
                        "STRI2INT": 3, "CONCAT": 3, "GETCHAR": 3, "SETCHAR": 3, "CREATEFRAME": 0, "PUSHFRAME": 0,
                        "POPFRAME": 0, "RETURN": 0, "BREAK": 0, "CALL": 1, "LABEL": 1, "JUMP": 1, "PUSHS": 1,
                        "WRITE": 1, "EXIT": 1, "DPRINT": 1, "JUMPIFEQ": 3, "JUMPIFNEQ": 3
                        }

NO_ERROR = 0
PARAMETER_ERROR = 10
INPUT_FILE_READ_ERROR = 11
INPUT_FILE_WRITE_ERROR = 12
XML_FORMAT_ERROR = 31
XML_STRUCTURE_ERROR = 32
SEMANTIC_ERROR = 52
WRONG_OPERANDS_TYPES_ERROR = 53
NOT_EXISTING_VARIABLE = 54
NOT_EXISTING_FRAME = 55
MISSING_VALUE_ERROR = 56
WRONG_OPERAND_VALUE_ERROR = 57
STRING_WORKING_ERROR = 58
INTERNAL_ERROR = 99

# Objects


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



class Argument:

    def __init__(self, arg_type, value):
        self.arg_type = arg_type
        self.value = value

    def get_arg_type(self):
        return self.arg_type

    def get_value(self):
        return self.arg_type

# Implementation


def close_script(exit_code: int):
    if exit_code == PARAMETER_ERROR:
        print(f"Chýbajúci parameter skriptu!", file=sys.stderr)
    elif exit_code == INPUT_FILE_READ_ERROR:
        print(f"Chyba pri otváraní vstupných súborov!", file=sys.stderr)
    elif exit_code == INPUT_FILE_WRITE_ERROR:
        print(f"Chyba pri otvorení vstupných súborov pre zápis!", file=sys.stderr)
    elif exit_code == XML_FORMAT_ERROR:
        print(f"Chybný XML formát vo vstupnom súbore!", file=sys.stderr)
    elif exit_code == XML_STRUCTURE_ERROR:
        print(f"Neočakávaná štruktúra XML!", file=sys.stderr)
    elif exit_code == SEMANTIC_ERROR:
        print(f"Chyba pri sémantických kontrolách vstupného kódu v IPPcode22!", file=sys.stderr)
    elif exit_code == WRONG_OPERANDS_TYPES_ERROR:
        print(f"Behová chyba interpretácie – zlé typy operandov!", file=sys.stderr)
    elif exit_code == NOT_EXISTING_VARIABLE:
        print(f"Behová chyba interpretácie – prrístup k neexistujúcej premennej!", file=sys.stderr)
    elif exit_code == NOT_EXISTING_FRAME:
        print(f"Behová chyba interpretácie – rámec neexistuje!", file=sys.stderr)
    elif exit_code == MISSING_VALUE_ERROR:
        print(f"Behová chyba interpretácie – chýbajúca hodnota!", file=sys.stderr)
    elif exit_code == WRONG_OPERAND_VALUE_ERROR:
        print(f"Behová chyba interpretácie – zlá hodnota operandu!", file=sys.stderr)
    elif exit_code == STRING_WORKING_ERROR:
        print(f"Behová chyba interpretácie – chybná práca s reťazcom!", file=sys.stderr)
    elif exit_code == INTERNAL_ERROR:
        print(f"Interná chyba!")

    exit(exit_code)


def process_arguments():
    arg_parse = argparse.ArgumentParser()
    arg_parse.add_argument("--source", nargs=1, help="Vstupný súbor s XML reprezentáciou zdrojového kódu.")
    arg_parse.add_argument("--input", nargs=1, help="Súbor so vstupmi pre interpretáciu zdrojového kódu.")

    load_args = vars(arg_parse.parse_args())

    tmp_source_path = None
    tmp_input_path = None

    if load_args.get("input") is None and load_args.get("source") is None:
        close_script(PARAMETER_ERROR)
    elif load_args.get("source") is None:
        tmp_input_path = load_args.get("input")[0]
    elif load_args.get("input") is None:
        tmp_source_path = load_args.get("source")[0]

    return tmp_input_path, tmp_source_path


def load_xml_file(src_file):

    if src_file is None:
        tmp_tree = ET.parse(sys.stdin)
    else:
        tmp_tree = ET.parse(src_file)

    return tmp_tree


def load_input_file(inp_file):
    if inp_file is None:
        tmp_file = sys.stdin
    else:
        tmp_file = open(inp_file)
    return tmp_file


def check_xml_file(tmp_tree):
    root = tmp_tree.getroot()

    if root.tag != "program":
        close_script(XML_FORMAT_ERROR)

    for child_element in root:
        if child_element.tag != "instruction":
            close_script(XML_STRUCTURE_ERROR)
        instruction_attr_list = list(child_element.attrib.keys())
        if not("order" in instruction_attr_list) or not("opcode" in instruction_attr_list):
            close_script(XML_FORMAT_ERROR)
        for sub_element in child_element:
            if not(re.match(r"arg[123]", sub_element.tag)):
                close_script(XML_STRUCTURE_ERROR)
            argument_attr_list = list(sub_element.attrib.keys())
            if not("type" in argument_attr_list):
                close_script(XML_FORMAT_ERROR)


def load_instructions(tmp_tree):
    tmp_instructions = list()
    defined_instructions = DEFINED_INSTRUCTIONS.keys()
    root = tmp_tree.getroot()

    for child_element in root:
        if not(child_element.attrib.get("opcode").upper() in defined_instructions):
            close_script(XML_STRUCTURE_ERROR)

        instruction = Instruction(child_element.attrib.get("opcode").upper(), int(child_element.attrib.get("order")))

        for sub_child in child_element:
            argument = Argument(sub_child.attrib.get("type"), sub_child.text)
            instruction.add_argument(argument)
        if len(instruction.get_arguments()) != DEFINED_INSTRUCTIONS.get(instruction.get_opcode()):
            close_script(XML_STRUCTURE_ERROR)

        tmp_instructions.append(instruction)

    return tmp_instructions


if __name__ == '__main__':

    input_path, source_path = process_arguments()
    tree = load_xml_file(source_path)
    check_xml_file(tree)
    input_file = load_input_file(input_path)
    instructions = load_instructions(tree)
    instructions.sort(key=lambda inst: inst.order)

    for line in input_file:
        print(line)

    print(input_path)
    print(source_path)

    for instruction in instructions:
        print(f"Instruction : {instruction.get_opcode()} order : {instruction.get_order()}")
