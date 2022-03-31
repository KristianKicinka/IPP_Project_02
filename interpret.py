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


class Interpreter:

    def __init__(self):
        self.data_stack = list()
        self.call_stack = list()
        self.frame_stack = dict()
        self.labels = dict()

    def add_to_data_stack(self, data):
        self.data_stack.append(data)

    def add_to_call_stack(self, data):
        self.call_stack.append(data)

    def add_to_frame_stack(self, key, data):
        self.frame_stack[key] = data

    def add_to_labels(self, key, data):
        self.labels[key] = data

    def get_data_stack(self):
        return self.data_stack

    def get_call_stack(self):
        return self.call_stack

    def get_frame_stack(self):
        return self.frame_stack

    def get_labels(self):
        return self.labels


class Argument:

    def __init__(self, arg_type, value):
        self.arg_type = arg_type
        self.value = value

    def get_arg_type(self):
        return self.arg_type

    def get_value(self):
        return self.value

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


def find_labels():

    for instruction in instructions:
        if instruction.get_opcode() == "LABEL":
            label = instruction.get_arguments()[0]
            if label in interpreter.get_labels().keys():
                close_script(SEMANTIC_ERROR)
            index = instructions.index(instruction)
            interpreter.add_to_labels(label, index)


# Execute functions


def execute_defvar(instruction):
    print("defvar")
    var = instruction.get_arguments()[0].get_value()
    if var in interpreter.get_frame_stack().keys():
        close_script(SEMANTIC_ERROR)
    interpreter.add_to_frame_stack(var, None)


def execute_pops(instruction):
    print("pops")
    if len(interpreter.get_data_stack()) == 0:
        close_script(MISSING_VALUE_ERROR)
    var = instruction.get_arguments()[0].get_value()
    if not(var in interpreter.get_frame_stack().keys()):
        close_script(SEMANTIC_ERROR)
    value = interpreter.get_data_stack().pop()
    interpreter.get_frame_stack().update(var=value)


def execute_move(instruction):
    print("move")
    var = instruction.get_arguments()[0].get_value()
    if not(var in interpreter.get_frame_stack().keys()):
        close_script(SEMANTIC_ERROR)
    symbol_value = instruction.get_arguments()[1].get_type()
    interpreter.get_frame_stack().update(var=symbol_value)


def execute_int2char(instruction):
    print("int2char")


def execute_strlen(instruction):
    print("strlen")


def execute_type(instruction):
    print("type")


def execute_not(instruction):
    print("not")


def execute_read(instruction):
    print("read")


def execute_add(instruction):
    print("add")


def execute_sub(instruction):
    print("sub")


def execute_mul(instruction):
    print("mul")


def execute_idiv(instruction):
    print("idiv")


def execute_lt(instruction):
    print("lt")


def execute_gt(instruction):
    print("gt")


def execute_eq(instruction):
    print("eq")


def execute_and(instruction):
    print("and")


def execute_or(instruction):
    print("or")


def execute_str2int(instruction):
    print("str2int")


def execute_concat(instruction):
    print("concat")


def execute_getchar(instruction):
    print("getchar")


def execute_setchar(instruction):
    print("setchar")


def execute_createframe(instruction):
    print("createframe")


def execute_pushframe(instruction):
    print("pushframe")


def execute_popframe(instruction):
    print("popframe")


def execute_return(instruction):
    print("return")


def execute_break(instruction):
    print("break")


def execute_call(instruction):
    print("call")


def execute_jump(instruction):
    print("jump")


def execute_pushs(instruction):
    print("pushs")
    value = instruction.get_arguments()[0].get_value()
    interpreter.add_to_data_stack(value)


def execute_write(instruction):
    print("write")


def execute_exit(instruction):
    print("exit")


def execute_dprint(instruction):
    print("dprint")


def execute_jumpifeq(instruction):
    print("jumpifeq")


def execute_jumpifneq(instruction):
    print("jumpifneq")


def interpret_instructions():

    for instruction in instructions:
        opcode = instruction.get_opcode()
        if opcode == "DEFVAR":
            execute_defvar(instruction)
        elif opcode == "POPS":
            execute_pops(instruction)
        elif opcode == "MOVE":
            execute_move(instruction)
        elif opcode == "INT2CHAR":
            execute_int2char(instruction)
        elif opcode == "STRLEN":
            execute_strlen(instruction)
        elif opcode == "TYPE":
            execute_type(instruction)
        elif opcode == "NOT":
            execute_not(instruction)
        elif opcode == "READ":
            execute_read(instruction)
        elif opcode == "ADD":
            execute_add(instruction)
        elif opcode == "SUB":
            execute_sub(instruction)
        elif opcode == "MUL":
            execute_mul(instruction)
        elif opcode == "IDIV":
            execute_idiv(instruction)
        elif opcode == "LT":
            execute_lt(instruction)
        elif opcode == "GT":
            execute_gt(instruction)
        elif opcode == "EQ":
            execute_eq(instruction)
        elif opcode == "AND":
            execute_and(instruction)
        elif opcode == "OR":
            execute_or(instruction)
        elif opcode == "STR2INT":
            execute_str2int(instruction)
        elif opcode == "CONCAT":
            execute_concat(instruction)
        elif opcode == "GETCHAR":
            execute_getchar(instruction)
        elif opcode == "SETCHAR":
            execute_setchar(instruction)
        elif opcode == "CREATEFRAME":
            execute_createframe(instruction)
        elif opcode == "PUSHFRAME":
            execute_pushframe(instruction)
        elif opcode == "POPFRAME":
            execute_popframe(instruction)
        elif opcode == "RETURN":
            execute_return(instruction)
        elif opcode == "BREAK":
            execute_break(instruction)
        elif opcode == "CALL":
            execute_call(instruction)
        elif opcode == "LABEL":
            continue
        elif opcode == "JUMP":
            execute_jump(instruction)
        elif opcode == "PUSHS":
            execute_pushs(instruction)
        elif opcode == "WRITE":
            execute_write(instruction)
        elif opcode == "EXIT":
            execute_exit(instruction)
        elif opcode == "DPRINT":
            execute_dprint(instruction)
        elif opcode == "JUMPIFEQ":
            execute_jumpifeq(instruction)
        elif opcode == "JUMPIFNEQ":
            execute_jumpifneq(instruction)


if __name__ == '__main__':

    input_path, source_path = process_arguments()
    tree = load_xml_file(source_path)
    check_xml_file(tree)
    input_file = load_input_file(input_path)
    instructions = load_instructions(tree)
    instructions.sort(key=lambda inst: inst.order)
    interpreter = Interpreter()
    find_labels()
    interpret_instructions()


