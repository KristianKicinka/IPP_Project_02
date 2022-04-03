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
        self.frame_stack = list()

        self.global_frames = dict()
        self.temporary_frame = None

        self.labels = dict()
        self.current_instruction_id = 0
        self.instructions_count = 0

    def create_temporary_frame(self):
        self.temporary_frame = dict()

    def add_to_temporary_frame(self, key, data):
        if not (self.temporary_frame is None):
            self.temporary_frame[key] = data
        else:
            close_script(NOT_EXISTING_FRAME)

    def get_temporary_frame(self):
        if not(self.temporary_frame is None):
            return self.temporary_frame
        else:
            close_script(NOT_EXISTING_FRAME)

    def add_to_frame_stack(self, data):
        self.frame_stack.append(data)

    def get_frame_stack(self):
        return self.frame_stack

    def get_frame_stack_top(self):
        if len(self.frame_stack) != 0:
            return self.frame_stack[-1]
        else:
            close_script(NOT_EXISTING_FRAME)

    def add_to_data_stack(self, data):
        self.data_stack.append(data)

    def add_to_call_stack(self, data):
        self.call_stack.append(data)

    def add_to_global_frames(self, key, data):
        self.global_frames[key] = data

    def add_to_labels(self, key, data):
        self.labels[key] = data

    def set_instructions_count(self, count):
        self.instructions_count = count

    def increase_current_instruction(self):
        self.current_instruction_id += 1

    def get_data_stack(self):
        return self.data_stack

    def get_call_stack(self):
        return self.call_stack

    def get_global_frames(self):
        return self.global_frames

    def get_labels(self):
        return self.labels

    def get_instructions_count(self):
        return self.instructions_count

    def get_current_instruction_id(self):
        return self.current_instruction_id


class Argument:

    def __init__(self, arg_type, value):
        self.arg_type = arg_type
        self.value = value

    def get_arg_type(self):
        return self.arg_type

    def get_value(self):
        return self.value


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
            label = instruction.get_arguments()[0].get_value()
            if label in interpreter.get_labels().keys():
                close_script(SEMANTIC_ERROR)
            index = instructions.index(instruction)
            interpreter.add_to_labels(label, index)


def get_variable(var_name, frame_type):
    var_obj = None
    if frame_type == "GF":
        if not (var_name in interpreter.get_global_frames().keys()):
            close_script(SEMANTIC_ERROR)
        var_obj = interpreter.get_global_frames().get(var_name)
    elif frame_type == "LF":
        if not(var_name in interpreter.get_frame_stack_top().keys()):
            close_script(SEMANTIC_ERROR)
        var_obj = interpreter.get_frame_stack_top().get(var_name)
    elif frame_type == "TF":
        if not (var_name in interpreter.get_temporary_frame().keys()):
            close_script(SEMANTIC_ERROR)
        var_obj = interpreter.get_temporary_frame().get(var_name)

    return var_obj


def return_symbol_data(symbol: Argument, data_type):
    data = None
    if symbol.get_arg_type() == "var":
        var_name = symbol.get_value()[3:]
        frame_type = symbol.get_value()[:2]

        var_obj = get_variable(var_name, frame_type)

        if data_type == "value":
            data = var_obj.get_value()
        elif data_type == "type":
            data = var_obj.get_type()
    else:
        if data_type == "value":
            data = symbol.get_value()
        elif data_type == "type":
            data = symbol.get_arg_type()
    return data


def process_aritmetic_operation(instruction, operation):
    var_name, frame_type = get_variable_name_and_frame_type(instruction)
    var_obj: Variable = get_variable(var_name, frame_type)

    symbol_1: Argument = instruction.get_arguments()[1]
    symbol_2: Argument = instruction.get_arguments()[2]

    symbol_1_type = return_symbol_data(symbol_1, "type")
    symbol_2_type = return_symbol_data(symbol_2, "type")

    if not (symbol_1_type != "int" and symbol_2_type != "int"):
        close_script(WRONG_OPERANDS_TYPES_ERROR)

    symbol_1_value = return_symbol_data(symbol_1, "value")
    symbol_2_value = return_symbol_data(symbol_2, "value")

    res = None
    if operation == "add":
        res = int(symbol_1_value) + int(symbol_2_value)
    elif operation == "sub":
        res = int(symbol_1_value) - int(symbol_2_value)
    elif operation == "mul":
        res = int(symbol_1_value) * int(symbol_2_value)
    elif operation == "idiv":
        if int(symbol_2_value) == 0:
            close_script(WRONG_OPERAND_VALUE_ERROR)
        res = int(symbol_1_value) // int(symbol_2_value)

    var_obj.set_value(res)
    var_obj.set_type("int")


def process_relation_operands(instruction, operation):
    var_name, frame_type = get_variable_name_and_frame_type(instruction)
    var_obj: Variable = get_variable(var_name, frame_type)

    symbol_1: Argument = instruction.get_arguments()[1]
    symbol_2: Argument = instruction.get_arguments()[2]

    symbol_1_type = return_symbol_data(symbol_1, "type")
    symbol_2_type = return_symbol_data(symbol_2, "type")

    if not((symbol_1_type == "int" or symbol_1_type == "string" or symbol_1_type == "bool")
           and symbol_1_type == symbol_2_type) and operation != "eq":
        close_script(WRONG_OPERANDS_TYPES_ERROR)
    if operation == "eq" and not(
            (symbol_1_type == "nil" and (symbol_2_type == "int" or symbol_2_type == "bool" or symbol_2_type == "string"))
            or
            ((symbol_1_type == "int" or symbol_1_type == "bool" or symbol_1_type == "string") and symbol_2_type == "nil")
            ):
        close_script(WRONG_OPERANDS_TYPES_ERROR)

    symbol_1_value = return_symbol_data(symbol_1, "value")
    symbol_2_value = return_symbol_data(symbol_2, "value")

    res = None

    if operation == "lt":
        if symbol_1_value < symbol_2_value:
            res = True
        else:
            res = False
    elif operation == "gt":
        if symbol_1_value > symbol_2_value:
            res = True
        else:
            res = False
    elif operation == "eq":
        if symbol_1_value == symbol_2_value:
            res = True
        else:
            res = False

    var_obj.set_value(res)
    var_obj.set_type("bool")


def process_logic_operators(instruction, operation):
    var_name, frame_type = get_variable_name_and_frame_type(instruction)
    var_obj: Variable = get_variable(var_name, frame_type)

    symbol_1: Argument = instruction.get_arguments()[1]
    symbol_2: Argument = instruction.get_arguments()[2]

    symbol_1_val = return_symbol_data(symbol_1, "value")
    symbol_2_val = return_symbol_data(symbol_2, "value")

    res = None
    if operation == "and":
        res = bool(symbol_1_val) and bool(symbol_2_val)
    elif operation == "or":
        res = bool(symbol_1_val) or bool(symbol_2_val)

    var_obj.set_value(res)
    var_obj.set_type("bool")


def get_variable_name_and_frame_type(instruction):
    var = instruction.get_arguments()[0].get_value()
    var_name = var[3:]
    frame_type = var[:2]
    return var_name, frame_type


# Execute functions


def execute_defvar(instruction):
    print("defvar")
    var_name, frame_type = get_variable_name_and_frame_type(instruction)
    var_obj = Variable(var_name)

    if frame_type == "GF":
        if var_name in interpreter.get_global_frames().keys():
            close_script(SEMANTIC_ERROR)
        interpreter.add_to_global_frames(var_name, var_obj)
    elif frame_type == "LF":
        if var_name in interpreter.get_frame_stack_top().keys():
            close_script(SEMANTIC_ERROR)
        interpreter.get_frame_stack_top()[var_name] = var_obj
    elif frame_type == "TF":
        if var_name in interpreter.get_temporary_frame().keys():
            close_script(SEMANTIC_ERROR)
        interpreter.add_to_temporary_frame(var_name, var_obj)


def execute_pops(instruction):
    print("pops")
    if len(interpreter.get_data_stack()) == 0:
        close_script(MISSING_VALUE_ERROR)

    var_name, frame_type = get_variable_name_and_frame_type(instruction)
    var_obj: Variable = get_variable(var_name, frame_type)

    value = interpreter.get_data_stack().pop()

    if type(value) == bool:
        var_obj.set_type("bool")
    elif type(value) == int:
        var_obj.set_type("int")
    elif value == "nil":
        var_obj.set_type("nil")
    elif type(value) == str:
        var_obj.set_type("string")

    var_obj.set_value(value)


def execute_move(instruction):
    print("move")
    var_name, frame_type = get_variable_name_and_frame_type(instruction)
    var_obj: Variable = get_variable(var_name, frame_type)

    symbol: Argument = instruction.get_arguments()[1]

    symbol_value = return_symbol_data(symbol, "value")
    symbol_type = return_symbol_data(symbol, "type")

    var_obj.set_value(symbol_value)
    var_obj.set_type(symbol_type)


def execute_int2char(instruction):
    print("int2char")

    var_name, frame_type = get_variable_name_and_frame_type(instruction)
    var_obj: Variable = get_variable(var_name, frame_type)

    symbol: Argument = instruction.get_arguments()[1]

    symbol_type = return_symbol_data(symbol, "type")
    print(symbol_type)
    symbol_val = return_symbol_data(symbol, "value")
    print(symbol_val)
    if symbol_type != "int":
        close_script(WRONG_OPERANDS_TYPES_ERROR)

    if int(symbol_val) < 0 or int(symbol_val) > 1114111:
        close_script(STRING_WORKING_ERROR)
    new_val = chr(int(symbol_val))

    var_obj.set_value(new_val)
    var_obj.set_type("string")


def execute_strlen(instruction):
    print("strlen")

    var_name, frame_type = get_variable_name_and_frame_type(instruction)
    var_obj: Variable = get_variable(var_name, frame_type)

    symbol: Argument = instruction.get_arguments()[1]

    symbol_type = return_symbol_data(symbol, "type")

    if symbol_type != "string":
        close_script(WRONG_OPERANDS_TYPES_ERROR)

    symbol_string = return_symbol_data(symbol, "value")
    string_len = len(symbol_string)

    var_obj.set_value(string_len)


def execute_type(instruction):
    print("type")
    var_name, frame_type = get_variable_name_and_frame_type(instruction)
    var_obj: Variable = get_variable(var_name, frame_type)

    symbol: Argument = instruction.get_arguments()[1]
    symbol_type = return_symbol_data(symbol, "type")

    if symbol_type is None:
        symbol_type = ""

    var_obj.set_value(symbol_type)
    var_obj.set_type("string")


def execute_not(instruction):
    print("not")
    var_name, frame_type = get_variable_name_and_frame_type(instruction)
    var_obj: Variable = get_variable(var_name, frame_type)

    symbol: Argument = instruction.get_arguments()[1]

    symbol_type = return_symbol_data(symbol, "type")
    symbol_value = return_symbol_data(symbol, "value")

    if symbol_type != "bool":
        close_script(WRONG_OPERANDS_TYPES_ERROR)

    res = not(bool(symbol_value))

    var_obj.set_value(res)
    var_obj.set_type("bool")


def execute_read(instruction):
    print("read")
    # TODO do read function


def execute_str2int(instruction):
    print("str2int")
    # TODO maybe check if symbol is string
    var_name, frame_type = get_variable_name_and_frame_type(instruction)
    var_obj: Variable = get_variable(var_name, frame_type)

    symbol: Argument = instruction.get_arguments()[1]
    symbol_val = return_symbol_data(symbol, "value")

    if len(symbol_val) > 1 or int(symbol_val) < 0 or int(symbol_val) > 65535:
        close_script(STRING_WORKING_ERROR)
    res = ord(symbol_val)

    var_obj.set_value(res)
    var_obj.set_type("int")


def execute_concat(instruction):
    print("concat")
    var_name, frame_type = get_variable_name_and_frame_type(instruction)
    var_obj: Variable = get_variable(var_name, frame_type)

    symbol_1: Argument = instruction.get_arguments()[1]
    symbol_2: Argument = instruction.get_arguments()[2]

    symbol_1_type = return_symbol_data(symbol_1, "type")
    symbol_2_type = return_symbol_data(symbol_2, "type")

    if symbol_1_type != "string" or symbol_2_type != "string":
        close_script(SEMANTIC_ERROR)

    symbol_1_val = return_symbol_data(symbol_1, "value")
    symbol_2_val = return_symbol_data(symbol_2, "value")

    res = symbol_1_val + symbol_2_val

    var_obj.set_value(res)
    var_obj.set_type("string")


def execute_getchar(instruction):
    print("getchar")
    # TODO maybe check types of symbols 1(str) 2(int)
    var_name, frame_type = get_variable_name_and_frame_type(instruction)
    var_obj: Variable = get_variable(var_name, frame_type)

    symbol_1 = instruction.get_arguments()[1]
    symbol_2 = instruction.get_arguments()[2]

    string = return_symbol_data(symbol_1, "value")
    index = return_symbol_data(symbol_2, "value")

    if index < 0 or index > len(string):
        close_script(STRING_WORKING_ERROR)

    res = string[index]

    var_obj.set_value(res)
    var_obj.set_type("string")


def execute_setchar(instruction):
    # TODO maybe check types
    print("setchar")
    var_name, frame_type = get_variable_name_and_frame_type(instruction)
    var_obj: Variable = get_variable(var_name, frame_type)

    symbol_1: Argument = instruction.get_arguments()[1]
    symbol_2: Argument = instruction.get_arguments()[2]

    index = return_symbol_data(symbol_1, "value")
    string = return_symbol_data(symbol_2, "value")

    var_str = var_obj.get_value()

    if index < 0 or index > len(var_str) or len(string) == 0:
        close_script(STRING_WORKING_ERROR)

    res = var_str[index] = string[0]

    var_obj.set_value(res)
    var_obj.set_type("string")


def execute_createframe(instruction):
    print("createframe")
    interpreter.create_temporary_frame()


def execute_pushframe(instruction):
    print("pushframe")
    tmp_frame = interpreter.get_temporary_frame()
    interpreter.add_to_frame_stack(tmp_frame)
    interpreter.temporary_frame = None


def execute_popframe(instruction):
    print("popframe")
    local_frame = interpreter.frame_stack.pop()
    interpreter.temporary_frame = local_frame


def execute_return(instruction):
    print("return")


def execute_break(instruction):
    print("break")
    current_inst_id = interpreter.get_current_instruction_id()
    processed_instructions_count = current_inst_id - 1
    print(f"ID Spracovávanej inštrukcie : {current_inst_id}", file=sys.stderr)
    print(f"Počet spracovaných inštrukcií : {processed_instructions_count}", file=sys.stderr)
    print(f"Obsah rámcov : ", file=sys.stderr)
    print("GF:")
    for key in interpreter.get_global_frames().keys():
        var: Variable = interpreter.get_global_frames().get(key)
        print(f"{var.get_name()} - {var.get_value()}", file=sys.stderr)
    print("LF:")
    if not(interpreter.get_frame_stack_top() is None):
        for key in interpreter.get_frame_stack_top().keys():
            var: Variable = interpreter.get_temporary_frame().get(key)
            print(f"{var.get_name()} - {var.get_value()}", file=sys.stderr)
    print("TF:")
    if not(interpreter.get_temporary_frame() is None):
        for key in interpreter.get_temporary_frame().keys():
            var: Variable = interpreter.get_temporary_frame().get(key)
            print(f"{var.get_name()} - {var.get_value()}", file=sys.stderr)


def execute_call(instruction):
    print("call")
    position = interpreter.get_current_instruction_id() + 1
    interpreter.add_to_call_stack(position)
    label = instruction.get_arguments()[0].get_value()
    new_index = interpreter.get_labels().get(label)
    interpreter.current_instruction_id = new_index


def execute_jump(instruction):
    print("jump")
    label = instruction.get_arguments()[0].get_value()
    new_index = interpreter.get_labels().get(label)
    interpreter.current_instruction_id = new_index


def execute_pushs(instruction):
    print("pushs")
    symbol: Argument = instruction.get_arguments()[0]
    symbol_value = return_symbol_data(symbol, "value")
    symbol_type = return_symbol_data(symbol, "type")
    if symbol_type == "int":
        symbol_value = int(symbol_value)
    elif symbol_type == "bool":
        if symbol_value == "true":
            symbol_value = True
        elif symbol_value == "false":
            symbol_value = False

    interpreter.add_to_data_stack(symbol_value)


def execute_write(instruction):
    print("write")


def execute_exit(instruction):
    print("exit")
    symbol: Argument = instruction.get_arguments()[0]
    symbol_value = return_symbol_data(symbol, "value")
    if not(0 <= int(symbol_value) <= 49):
        close_script(WRONG_OPERAND_VALUE_ERROR)
    exit(int(symbol_value))


def execute_dprint(instruction):
    print("dprint")
    symbol: Argument = instruction.get_arguments()[0]
    symbol_val = return_symbol_data(symbol, "value")
    print(symbol_val, file=sys.stderr)


def execute_jumpifeq(instruction):
    print("jumpifeq")
    symbol_1 = instruction.get_arguments()[1]
    symbol_2 = instruction.get_arguments()[2]

    symbol_1_type = return_symbol_data(symbol_1, "type")
    symbol_2_type = return_symbol_data(symbol_2, "type")

    symbol_1_value = return_symbol_data(symbol_1, "value")
    symbol_2_value = return_symbol_data(symbol_2, "value")

    if not((symbol_1_type == symbol_2_type or symbol_1_type == "nil" or symbol_2_type == "nil")
           and symbol_1_value == symbol_2_value):
        close_script(WRONG_OPERANDS_TYPES_ERROR)

    label = instruction.get_arguments()[0].get_value()
    new_index = interpreter.get_labels().get(label)
    interpreter.current_instruction_id = new_index


def execute_jumpifneq(instruction):
    print("jumpifneq")
    symbol_1 = instruction.get_arguments()[1]
    symbol_2 = instruction.get_arguments()[2]

    symbol_1_type = return_symbol_data(symbol_1, "type")
    symbol_2_type = return_symbol_data(symbol_2, "type")

    symbol_1_value = return_symbol_data(symbol_1, "value")
    symbol_2_value = return_symbol_data(symbol_2, "value")

    if not((symbol_1_type == symbol_2_type or symbol_1_type == "nil" or symbol_2_type == "nil")
           and symbol_1_value != symbol_2_value):
        close_script(WRONG_OPERANDS_TYPES_ERROR)

    label = instruction.get_arguments()[0].get_value()
    new_index = interpreter.get_labels().get(label)
    interpreter.current_instruction_id = new_index


def interpret_instructions():

    while interpreter.get_current_instruction_id() < len(instructions):
        instruction = instructions[interpreter.get_current_instruction_id()]
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
            process_aritmetic_operation(instruction, "add")
        elif opcode == "SUB":
            process_aritmetic_operation(instruction, "sub")
        elif opcode == "MUL":
            process_aritmetic_operation(instruction, "mul")
        elif opcode == "IDIV":
            process_aritmetic_operation(instruction, "idiv")
        elif opcode == "LT":
            process_relation_operands(instruction, "lt")
        elif opcode == "GT":
            process_relation_operands(instruction, "gt")
        elif opcode == "EQ":
            process_relation_operands(instruction, "eq")
        elif opcode == "AND":
            process_logic_operators(instruction, "and")
        elif opcode == "OR":
            process_logic_operators(instruction, "or")
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
        interpreter.increase_current_instruction()
        print(interpreter.get_data_stack())


if __name__ == '__main__':

    input_path, source_path = process_arguments()
    tree = load_xml_file(source_path)
    check_xml_file(tree)
    input_file = load_input_file(input_path)
    instructions = load_instructions(tree)
    instructions.sort(key=lambda inst: inst.order)
    interpreter = Interpreter()
    interpreter.set_instructions_count(len(instructions))
    find_labels()
    interpret_instructions()



