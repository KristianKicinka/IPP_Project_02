# Project : IPP Projekt - 2.úloha Interpret.
# @author Kristián Kičinka (xkicin02)

import argparse
import re
import xml.etree.ElementTree as ET

from interpretFiles.config import *

# Objekty

from interpretFiles.Argument import Argument
from interpretFiles.Instruction import Instruction
from interpretFiles.Interpret import Interpreter
from interpretFiles.Variable import Variable


# @brief Funkcia zabezpečuje spracovanie načítaných argumentov z terminálu
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


# @brief Funkcia zabezpečuje načítanie xml súboru
# @param src_file Zdrojový súbor (XML súbor)
def load_xml_file(src_file):
    tmp_tree = None

    if src_file is None:
        try:
            tmp_tree = ET.parse(sys.stdin)
        except:
            close_script(XML_FORMAT_ERROR)
    else:
        try:
            tmp_tree = ET.parse(src_file)
        except:
            close_script(XML_FORMAT_ERROR)

    return tmp_tree


# @brief Funkcia zabezpečuje načítanie xml súboru
# @param src_file Zdrojový súbor (XML súbor)
def load_input_file(inp_file):
    if inp_file is None:
        tmp_file = sys.stdin
    else:
        tmp_file = open(inp_file)
    return tmp_file


# @brief Funkcia zabezpečuje kontrolu xml súboru
# @param tmp_tree XML strom vytvorený pomocou ElementTree
def check_xml_file(tmp_tree):
    root = tmp_tree.getroot()
    if root.tag != "program":
        close_script(XML_STRUCTURE_ERROR)

    for child_element in root:
        if child_element.tag != "instruction":
            close_script(XML_STRUCTURE_ERROR)
        instruction_attr_list = list(child_element.attrib.keys())
        if not ("order" in instruction_attr_list) or not ("opcode" in instruction_attr_list):
            close_script(XML_STRUCTURE_ERROR)
        for sub_element in child_element:
            if not (re.match(r"arg[123]", sub_element.tag)):
                close_script(XML_STRUCTURE_ERROR)
            argument_attr_list = list(sub_element.attrib.keys())
            if not ("type" in argument_attr_list):
                close_script(XML_STRUCTURE_ERROR)


# @brief Funkcia zabezpečuje načítanie inštrukcií programu
# @param tmp_tree XML strom vytvorený pomocou ElementTree
def load_instructions(tmp_tree):
    tmp_instructions = list()
    defined_instructions = DEFINED_INSTRUCTIONS.keys()
    root = tmp_tree.getroot()

    for child_element in root:
        if not (child_element.attrib.get("opcode").upper() in defined_instructions):
            close_script(XML_STRUCTURE_ERROR)
        try:
            order_number = int(child_element.attrib.get("order"))
            if order_number <= 0:
                close_script(XML_STRUCTURE_ERROR)
        except:
            close_script(XML_STRUCTURE_ERROR)

        instruction = Instruction(child_element.attrib.get("opcode").upper(), int(child_element.attrib.get("order")))

        argument_names = list()
        for sub_child in child_element:
            argument = Argument(sub_child.tag, sub_child.attrib.get("type"), sub_child.text)
            instruction.add_argument(argument)
            argument_names.append(sub_child.tag)

        if check_duplicities(argument_names):
            close_script(XML_STRUCTURE_ERROR)

        arguments = instruction.get_arguments()
        arguments.sort(key=lambda arg: arg.name)

        if len(arguments) != int(DEFINED_INSTRUCTIONS.get(instruction.get_opcode())):
            close_script(XML_STRUCTURE_ERROR)

        check_arguments(arguments)

        tmp_instructions.append(instruction)

    orders_list = list()
    for instr in tmp_instructions:
        orders_list.append(instr.get_order())

    if check_duplicities(orders_list):
        close_script(XML_STRUCTURE_ERROR)

    return tmp_instructions


# @brief Funkcia zabezpečuje overenie duplicitných hodnôt v zadanom liste
# @param value_list List hodnôt, ktoré je nutné overiť
def check_duplicities(value_list: list):
    for element in value_list:
        if value_list.count(element) > 1:
            return True
    return False


# @brief Funkcia zabezpečuje kontrolu dátového typu int
# @param value XML hodnota určená na overenie dátového typu
def check_integer(value):
    try:
        int(value)
        return True
    except ValueError:
        return False


# @brief Funkcia zabezpečuje overenie argumentov inštrukcií
# @param arguments XML List arbumentov
def check_arguments(arguments: list):
    index = 1
    for argument in arguments:
        if not(int(argument.get_name()[3:]) == index):
            close_script(XML_STRUCTURE_ERROR)
        index += 1


# @brief Funkcia zabezpečuje vyhľadanie a uloženie náveští
def find_labels():
    for instruction in instructions:
        if instruction.get_opcode() == "LABEL":
            label = instruction.get_arguments()[0].get_value()
            if label in interpreter.get_labels().keys():
                close_script(SEMANTIC_ERROR)
            index = instructions.index(instruction)
            interpreter.add_to_labels(label, index)


# @brief Funkcia zabezpečuje overenie načítaných naveští
# @param label kontrolované náveštie
def check_labels(label):
    if not(label in interpreter.get_labels().keys()):
        close_script(SEMANTIC_ERROR)


# @brief Funkcia zabezpečuje spracovanie premennej programu
# @param var_name Názov premennej
# @param frame_type Typ platnosti premennej
def get_variable(var_name, frame_type):
    var_obj = None
    if frame_type == "GF":
        if not (var_name in interpreter.get_global_frames().keys()):
            close_script(NOT_EXISTING_VARIABLE)
        var_obj = interpreter.get_global_frames().get(var_name)
    elif frame_type == "LF":
        if not (var_name in interpreter.get_frame_stack_top().keys()):
            close_script(NOT_EXISTING_VARIABLE)
        var_obj = interpreter.get_frame_stack_top().get(var_name)
    elif frame_type == "TF":
        if not (var_name in interpreter.get_temporary_frame().keys()):
            close_script(NOT_EXISTING_VARIABLE)
        var_obj = interpreter.get_temporary_frame().get(var_name)

    return var_obj


# @brief Funkcia zabezpečuje spracovanie dát a typu symbolov
# @param symbol Argument inštrukcie (premenná/symbol)
# @param data_type prepínač, ktorý určuje, čo sa má spracovať
def return_symbol_data(symbol: Argument, data_type):
    data = None
    if symbol.get_arg_type() == "var":
        var_name = symbol.get_value()[3:]
        frame_type = symbol.get_value()[:2]

        var_obj = get_variable(var_name, frame_type)

        if data_type == "value":
            data = process_value(var_obj.get_value(), var_obj.get_type())
            if data is None:
                close_script(MISSING_VALUE_ERROR)
        elif data_type == "type":
            data = var_obj.get_type()
    else:
        if data_type == "value":
            data = process_value(symbol.get_value(), symbol.get_arg_type())
        elif data_type == "type":
            data = symbol.get_arg_type()
    return data


# @brief Funkcia zabezpečuje hodnoty premennej alebo symbolu
# @param tmp_value hodnota premennej alebo symbolu
# @param value_type prepínač, ktorý určuje, dátový typ
def process_value(tmp_value, value_type):
    new_value = tmp_value
    if value_type == "string":
        if new_value is None:
            new_value = ""
        else:
            regex = r"\\[\d]{3}"
            escapes_list = re.findall(regex, tmp_value)
            for escape in escapes_list:
                char = chr(int(escape[1:]))
                new_value = new_value.replace(escape, char)
    elif value_type == "int":
        try:
            new_value = int(new_value)
        except:
            close_script(XML_STRUCTURE_ERROR)
    elif value_type == "bool":
        if new_value == "true":
            new_value = True
        elif new_value == "false":
            new_value = False

    return new_value


# @brief Funkcia zabezpečuje spracovanie aritmetických operácií programu
# @param instruction spracovávaná inštrukcia
# @param operation prepínač, ktorý určuje, typ operácie
def process_aritmetic_operation(instruction, operation):
    var_name, frame_type = get_variable_name_and_frame_type(instruction)
    var_obj: Variable = get_variable(var_name, frame_type)

    symbol_1: Argument = instruction.get_arguments()[1]
    symbol_2: Argument = instruction.get_arguments()[2]

    symbol_1_value = return_symbol_data(symbol_1, "value")
    symbol_2_value = return_symbol_data(symbol_2, "value")

    symbol_1_type = return_symbol_data(symbol_1, "type")
    symbol_2_type = return_symbol_data(symbol_2, "type")

    if not(symbol_1_type == "int" and symbol_2_type == "int"):
        close_script(WRONG_OPERANDS_TYPES_ERROR)

    res = None
    if operation == "add":
        res = symbol_1_value + symbol_2_value
    elif operation == "sub":
        res = symbol_1_value - symbol_2_value
    elif operation == "mul":
        res = symbol_1_value * symbol_2_value
    elif operation == "idiv":
        if symbol_2_value == 0:
            close_script(WRONG_OPERAND_VALUE_ERROR)
        res = symbol_1_value // symbol_2_value

    var_obj.set_value(res)
    var_obj.set_type("int")


# @brief Funkcia zabezpečuje spracovanie relačných operácií programu
# @param instruction spracovávaná inštrukcia
# @param operation prepínač, ktorý určuje, typ operácie
def process_relation_operands(instruction, operation):
    var_name, frame_type = get_variable_name_and_frame_type(instruction)
    var_obj: Variable = get_variable(var_name, frame_type)

    symbol_1: Argument = instruction.get_arguments()[1]
    symbol_2: Argument = instruction.get_arguments()[2]

    symbol_1_value = return_symbol_data(symbol_1, "value")
    symbol_2_value = return_symbol_data(symbol_2, "value")

    symbol_1_type = return_symbol_data(symbol_1, "type")
    symbol_2_type = return_symbol_data(symbol_2, "type")

    if not ((symbol_1_type == "int" or symbol_1_type == "string" or symbol_1_type == "bool")
            and symbol_1_type == symbol_2_type) and operation != "eq":
        close_script(WRONG_OPERANDS_TYPES_ERROR)
    if operation == "eq" and not(symbol_1_type == symbol_2_type or symbol_1_type == "nil" or symbol_2_type == "nil"):
        close_script(WRONG_OPERANDS_TYPES_ERROR)

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


# @brief Funkcia zabezpečuje spracovanie logických operácií programu
# @param instruction spracovávaná inštrukcia
# @param operation prepínač, ktorý určuje, typ operácie
def process_logic_operators(instruction, operation):
    var_name, frame_type = get_variable_name_and_frame_type(instruction)
    var_obj: Variable = get_variable(var_name, frame_type)

    symbol_1: Argument = instruction.get_arguments()[1]
    symbol_2: Argument = instruction.get_arguments()[2]

    symbol_1_val = return_symbol_data(symbol_1, "value")
    symbol_2_val = return_symbol_data(symbol_2, "value")

    symbol_1_type = return_symbol_data(symbol_1, "type")
    symbol_2_type = return_symbol_data(symbol_2, "type")

    if not(symbol_1_type == "bool" and symbol_2_type == "bool"):
        close_script(WRONG_OPERANDS_TYPES_ERROR)

    res = None
    if operation == "and":
        res = bool(symbol_1_val) and bool(symbol_2_val)
    elif operation == "or":
        res = bool(symbol_1_val) or bool(symbol_2_val)

    var_obj.set_value(res)
    var_obj.set_type("bool")


# @brief Funkcia zabezpečuje získanie názvu a typu platnosti premennej z argumentu
# @param instruction Spracovávaná inštrukcia
def get_variable_name_and_frame_type(instruction):
    var = instruction.get_arguments()[0].get_value()
    var_name = var[3:]
    frame_type = var[:2]
    return var_name, frame_type


# Execute functions


# @brief Funkcia zabezpečuje vykonanie inštrukcie DEFVAR
# @param instruction Spracovávaná inštrukcia
def execute_defvar(instruction):
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


# @brief Funkcia zabezpečuje vykonanie inštrukcie POPS
# @param instruction Spracovávaná inštrukcia
def execute_pops(instruction):
    if len(interpreter.get_data_stack()) == 0:
        close_script(MISSING_VALUE_ERROR)

    var_name, frame_type = get_variable_name_and_frame_type(instruction)
    var_obj: Variable = get_variable(var_name, frame_type)

    value = interpreter.data_stack_pop()

    if type(value) == bool:
        var_obj.set_type("bool")
    elif type(value) == int:
        var_obj.set_type("int")
    elif value == "nil":
        var_obj.set_type("nil")
    elif type(value) == str:
        var_obj.set_type("string")

    var_obj.set_value(value)


# @brief Funkcia zabezpečuje vykonanie inštrukcie MOVE
# @param instruction Spracovávaná inštrukcia
def execute_move(instruction):
    var_name, frame_type = get_variable_name_and_frame_type(instruction)
    var_obj: Variable = get_variable(var_name, frame_type)

    symbol: Argument = instruction.get_arguments()[1]

    symbol_value = return_symbol_data(symbol, "value")
    symbol_type = return_symbol_data(symbol, "type")

    var_obj.set_value(symbol_value)
    var_obj.set_type(symbol_type)


# @brief Funkcia zabezpečuje vykonanie inštrukcie INT2CHAR
# @param instruction Spracovávaná inštrukcia
def execute_int2char(instruction):
    var_name, frame_type = get_variable_name_and_frame_type(instruction)
    var_obj: Variable = get_variable(var_name, frame_type)

    symbol: Argument = instruction.get_arguments()[1]

    symbol_val = return_symbol_data(symbol, "value")
    symbol_type = return_symbol_data(symbol, "type")

    if symbol_type != "int":
        close_script(WRONG_OPERANDS_TYPES_ERROR)

    if int(symbol_val) < 0 or int(symbol_val) > 1114111:
        close_script(STRING_WORKING_ERROR)
    new_val = chr(int(symbol_val))

    var_obj.set_value(new_val)
    var_obj.set_type("string")


# @brief Funkcia zabezpečuje vykonanie inštrukcie STRLEN
# @param instruction Spracovávaná inštrukcia
def execute_strlen(instruction):
    var_name, frame_type = get_variable_name_and_frame_type(instruction)
    var_obj: Variable = get_variable(var_name, frame_type)

    symbol: Argument = instruction.get_arguments()[1]

    symbol_string = return_symbol_data(symbol, "value")
    symbol_type = return_symbol_data(symbol, "type")

    if symbol_type != "string":
        close_script(WRONG_OPERANDS_TYPES_ERROR)

    string_len = len(symbol_string)

    var_obj.set_value(string_len)
    var_obj.set_type("int")


# @brief Funkcia zabezpečuje vykonanie inštrukcie TYPE
# @param instruction Spracovávaná inštrukcia
def execute_type(instruction):
    var_name, frame_type = get_variable_name_and_frame_type(instruction)
    var_obj: Variable = get_variable(var_name, frame_type)

    symbol: Argument = instruction.get_arguments()[1]
    symbol_type = return_symbol_data(symbol, "type")

    if symbol_type is None:
        symbol_type = ""

    var_obj.set_value(symbol_type)
    var_obj.set_type("string")


# @brief Funkcia zabezpečuje vykonanie inštrukcie NOT
# @param instruction Spracovávaná inštrukcia
def execute_not(instruction):
    var_name, frame_type = get_variable_name_and_frame_type(instruction)
    var_obj: Variable = get_variable(var_name, frame_type)

    symbol: Argument = instruction.get_arguments()[1]

    symbol_value = return_symbol_data(symbol, "value")
    symbol_type = return_symbol_data(symbol, "type")

    if symbol_type != "bool":
        close_script(WRONG_OPERANDS_TYPES_ERROR)

    res = not (bool(symbol_value))

    var_obj.set_value(res)
    var_obj.set_type("bool")


# @brief Funkcia zabezpečuje vykonanie inštrukcie READ
# @param instruction Spracovávaná inštrukcia
def execute_read(instruction):
    var_name, frame_type = get_variable_name_and_frame_type(instruction)
    var_obj: Variable = get_variable(var_name, frame_type)
    symbol: Argument = instruction.get_arguments()[1]
    symbol_value = return_symbol_data(symbol, "value")

    value = None

    for line in input_file:
        line = line.rstrip("\n")
        if line.lower() == "true" and symbol_value == "bool":
            value = True
            break
        elif line.lower() == "false" and symbol_value == "bool":
            value = False
            break
        elif symbol_value == "bool":
            value = False
            break
        elif check_integer(line) and symbol_value == "int":
            value = int(line)
            break
        elif type(line) is str and symbol_value == "string":
            value = line
            break
    if value is None:
        symbol_value = "nil"
        value = "nil"

    var_obj.set_value(value)
    var_obj.set_type(symbol_value)


# @brief Funkcia zabezpečuje vykonanie inštrukcie STRI2INT
# @param instruction Spracovávaná inštrukcia
def execute_stri2int(instruction):
    var_name, frame_type = get_variable_name_and_frame_type(instruction)
    var_obj: Variable = get_variable(var_name, frame_type)

    symbol_1: Argument = instruction.get_arguments()[1]
    symbol_2: Argument = instruction.get_arguments()[2]

    symbol_1_val = return_symbol_data(symbol_1, "value")
    symbol_2_val = return_symbol_data(symbol_2, "value")

    symbol_1_type = return_symbol_data(symbol_1, "type")
    symbol_2_type = return_symbol_data(symbol_2, "type")

    if not(symbol_1_type == "string" and symbol_2_type == "int"):
        close_script(WRONG_OPERANDS_TYPES_ERROR)

    if not(0 <= symbol_2_val <= len(symbol_1_val)-1):
        close_script(STRING_WORKING_ERROR)
    try:
        res = ord(symbol_1_val[symbol_2_val])
        var_obj.set_value(res)
        var_obj.set_type("int")
    except:
        close_script(STRING_WORKING_ERROR)


# @brief Funkcia zabezpečuje vykonanie inštrukcie CONCAT
# @param instruction Spracovávaná inštrukcia
def execute_concat(instruction):
    var_name, frame_type = get_variable_name_and_frame_type(instruction)
    var_obj: Variable = get_variable(var_name, frame_type)

    symbol_1: Argument = instruction.get_arguments()[1]
    symbol_2: Argument = instruction.get_arguments()[2]

    symbol_1_val = return_symbol_data(symbol_1, "value")
    symbol_2_val = return_symbol_data(symbol_2, "value")

    symbol_1_type = return_symbol_data(symbol_1, "type")
    symbol_2_type = return_symbol_data(symbol_2, "type")

    if symbol_1_type != "string" or symbol_2_type != "string":
        close_script(WRONG_OPERANDS_TYPES_ERROR)

    res = symbol_1_val + symbol_2_val

    var_obj.set_value(res)
    var_obj.set_type("string")


# @brief Funkcia zabezpečuje vykonanie inštrukcie GETCHAR
# @param instruction Spracovávaná inštrukcia
def execute_getchar(instruction):
    var_name, frame_type = get_variable_name_and_frame_type(instruction)
    var_obj: Variable = get_variable(var_name, frame_type)

    symbol_1 = instruction.get_arguments()[1]
    symbol_2 = instruction.get_arguments()[2]

    string = return_symbol_data(symbol_1, "value")
    index = return_symbol_data(symbol_2, "value")

    symbol_1_type = return_symbol_data(symbol_1, "type")
    symbol_2_type = return_symbol_data(symbol_2, "type")

    if not(symbol_1_type == "string" and symbol_2_type == "int"):
        close_script(WRONG_OPERANDS_TYPES_ERROR)

    if index < 0 or index > len(string)-1:
        close_script(STRING_WORKING_ERROR)

    res = string[index]

    var_obj.set_value(res)
    var_obj.set_type("string")


# @brief Funkcia zabezpečuje vykonanie inštrukcie SETCHAR
# @param instruction Spracovávaná inštrukcia
def execute_setchar(instruction):
    var_name, frame_type = get_variable_name_and_frame_type(instruction)
    var_obj: Variable = get_variable(var_name, frame_type)

    symbol_1: Argument = instruction.get_arguments()[1]
    symbol_2: Argument = instruction.get_arguments()[2]

    index = return_symbol_data(symbol_1, "value")
    string = return_symbol_data(symbol_2, "value")

    symbol_1_type = return_symbol_data(symbol_1, "type")
    symbol_2_type = return_symbol_data(symbol_2, "type")
    var_type = var_obj.get_type()

    if var_type is None:
        close_script(MISSING_VALUE_ERROR)

    if not(var_type == "string" and symbol_1_type == "int" and symbol_2_type == "string"):
        close_script(WRONG_OPERANDS_TYPES_ERROR)

    var_str = var_obj.get_value()

    if index < 0 or index > len(var_str)-1 or len(string) == 0:
        close_script(STRING_WORKING_ERROR)

    res = var_str[:index] + string[0] + var_str[index+1:]

    var_obj.set_value(res)
    var_obj.set_type("string")


# @brief Funkcia zabezpečuje vykonanie inštrukcie CREATEFRAME
# @param instruction Spracovávaná inštrukcia
def execute_createframe(instruction):
    interpreter.create_temporary_frame()


# @brief Funkcia zabezpečuje vykonanie inštrukcie PUSHFRAME
# @param instruction Spracovávaná inštrukcia
def execute_pushframe(instruction):
    tmp_frame = interpreter.get_temporary_frame()
    interpreter.add_to_frame_stack(tmp_frame)
    interpreter.temporary_frame = None


# @brief Funkcia zabezpečuje vykonanie inštrukcie POPFRAME
# @param instruction Spracovávaná inštrukcia
def execute_popframe(instruction):
    local_frame = interpreter.frame_stack_pop()
    interpreter.temporary_frame = local_frame


# @brief Funkcia zabezpečuje vykonanie inštrukcie RETURN
# @param instruction Spracovávaná inštrukcia
def execute_return(instruction):
    if len(interpreter.get_call_stack()) == 0:
        close_script(MISSING_VALUE_ERROR)
    position = interpreter.call_stack_pop()
    interpreter.current_instruction_id = position


# @brief Funkcia zabezpečuje vykonanie inštrukcie BREAK
# @param instruction Spracovávaná inštrukcia
def execute_break(instruction):
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
    if not (interpreter.get_frame_stack_top() is None):
        for key in interpreter.get_frame_stack_top().keys():
            var: Variable = interpreter.get_temporary_frame().get(key)
            print(f"{var.get_name()} - {var.get_value()}", file=sys.stderr)
    print("TF:")
    if not (interpreter.get_temporary_frame() is None):
        for key in interpreter.get_temporary_frame().keys():
            var: Variable = interpreter.get_temporary_frame().get(key)
            print(f"{var.get_name()} - {var.get_value()}", file=sys.stderr)


# @brief Funkcia zabezpečuje vykonanie inštrukcie CALL
# @param instruction Spracovávaná inštrukcia
def execute_call(instruction):
    position = interpreter.get_current_instruction_id()
    interpreter.add_to_call_stack(position)
    label = instruction.get_arguments()[0].get_value()
    check_labels(label)
    new_index = interpreter.get_labels().get(label)
    interpreter.current_instruction_id = new_index


# @brief Funkcia zabezpečuje vykonanie inštrukcie JUMP
# @param instruction Spracovávaná inštrukcia
def execute_jump(instruction):
    label = instruction.get_arguments()[0].get_value()
    check_labels(label)
    new_index = interpreter.get_labels().get(label)
    interpreter.current_instruction_id = new_index


# @brief Funkcia zabezpečuje vykonanie inštrukcie PUSHS
# @param instruction Spracovávaná inštrukcia
def execute_pushs(instruction):
    symbol: Argument = instruction.get_arguments()[0]
    symbol_value = return_symbol_data(symbol, "value")

    interpreter.add_to_data_stack(symbol_value)


# @brief Funkcia zabezpečuje vykonanie inštrukcie WRITE
# @param instruction Spracovávaná inštrukcia
def execute_write(instruction):
    symbol = instruction.get_arguments()[0]
    symbol_value = return_symbol_data(symbol, "value")
    symbol_type = return_symbol_data(symbol, "type")

    if symbol_type == "int":
        symbol_value = int(symbol_value)
    elif symbol_type == "bool":
        if symbol_value == "true" or symbol_value is True:
            symbol_value = "true"
        elif symbol_value == "false" or symbol_value is False:
            symbol_value = "false"
    elif symbol_type == "nil":
        symbol_value = ""

    print(symbol_value, end='')


# @brief Funkcia zabezpečuje vykonanie inštrukcie EXIT
# @param instruction Spracovávaná inštrukcia
def execute_exit(instruction):
    symbol: Argument = instruction.get_arguments()[0]
    symbol_value = return_symbol_data(symbol, "value")
    if not (0 <= int(symbol_value) <= 49):
        close_script(WRONG_OPERAND_VALUE_ERROR)
    exit(int(symbol_value))


# @brief Funkcia zabezpečuje vykonanie inštrukcie DPRINT
# @param instruction Spracovávaná inštrukcia
def execute_dprint(instruction):
    symbol: Argument = instruction.get_arguments()[0]
    symbol_val = return_symbol_data(symbol, "value")
    print(symbol_val, file=sys.stderr)


# @brief Funkcia zabezpečuje vykonanie inštrukcie JUMPIFEQ
# @param instruction Spracovávaná inštrukcia
def execute_jumpifeq(instruction):
    symbol_1 = instruction.get_arguments()[1]
    symbol_2 = instruction.get_arguments()[2]

    symbol_1_value = return_symbol_data(symbol_1, "value")
    symbol_2_value = return_symbol_data(symbol_2, "value")

    symbol_1_type = return_symbol_data(symbol_1, "type")
    symbol_2_type = return_symbol_data(symbol_2, "type")

    if not (symbol_1_type == symbol_2_type or
            (symbol_1_type == "nil" and symbol_2_type != "nil") or (symbol_2_type == "nil" and symbol_1_type != "nil")):
        close_script(WRONG_OPERANDS_TYPES_ERROR)

    label = instruction.get_arguments()[0].get_value()
    check_labels(label)

    if symbol_1_value == symbol_2_value:
        new_index = interpreter.get_labels().get(label)
        interpreter.current_instruction_id = new_index


# @brief Funkcia zabezpečuje vykonanie inštrukcie JUMPIFNEQ
# @param instruction Spracovávaná inštrukcia
def execute_jumpifneq(instruction):
    symbol_1 = instruction.get_arguments()[1]
    symbol_2 = instruction.get_arguments()[2]

    symbol_1_value = return_symbol_data(symbol_1, "value")
    symbol_2_value = return_symbol_data(symbol_2, "value")

    symbol_1_type = return_symbol_data(symbol_1, "type")
    symbol_2_type = return_symbol_data(symbol_2, "type")

    if not (symbol_1_type == symbol_2_type or symbol_1_type == "nil" or symbol_2_type == "nil"):
        close_script(WRONG_OPERANDS_TYPES_ERROR)

    label = instruction.get_arguments()[0].get_value()
    check_labels(label)

    if symbol_1_value != symbol_2_value:
        new_index = interpreter.get_labels().get(label)
        interpreter.current_instruction_id = new_index


# @brief Funkcia zabezpečuje identifikáciu inštrukcií na spracovanie
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
        elif opcode == "STRI2INT":
            execute_stri2int(instruction)
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
            interpreter.increase_current_instruction()
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


# @brief Hlavná funckia
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
