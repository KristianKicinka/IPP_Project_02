import re
import argparse
import sys
import xml.etree.ElementTree as ET

PARAMETER_ERROR = 10
INPUT_FILE_READ_ERROR = 11
INPUT_FILE_WRITE_ERROR = 12
XML_FORMAT_ERROR = 31
XML_STRUCTURE_ERROR = 32
SEMANTIC_ERROR = 52
BAD_OPERANDS_TYPES_ERROR = 53
NOT_EXISTING_VARIABLE = 54
NOT_EXISTING_FRAME = 55
INTERNAL_ERROR = 99


def close_script(exit_code: int):
    if exit_code == PARAMETER_ERROR:
        print(f"Chýbajúci parameter skriptu!\n", file=sys.stderr)
    elif exit_code == INPUT_FILE_READ_ERROR:
        print(f"Chyba pri otváraní vstupných súborov!\n", file=sys.stderr)
    elif exit_code == INPUT_FILE_WRITE_ERROR:
        print(f"Chyba pri otvorení vstupných súborov pre zápis!\n", file=sys.stderr)
    elif exit_code == XML_FORMAT_ERROR:
        print(f"Chybný XML formát vo vstupnom súbore!\n", file=sys.stderr)
    elif exit_code == XML_STRUCTURE_ERROR:
        print(f"Neočakávaná štruktúra XML!\n", file=sys.stderr)
    elif exit_code == SEMANTIC_ERROR:
        print(f"Chyba pri sémantických kontrolách vstupného kódu v IPPcode22!\n", file=sys.stderr)
    elif exit_code == BAD_OPERANDS_TYPES_ERROR:
        print(f"Behová chyba interpretácie – zlé typy operandov!\n", file=sys.stderr)
    elif exit_code == NOT_EXISTING_VARIABLE:
        print(f"Behová chyba interpretácie – prrístup k neexistujúcej premennej!\n", file=sys.stderr)
    elif exit_code == NOT_EXISTING_FRAME:
        print(f"Behová chyba interpretácie – rámec neexistuje!\n", file=sys.stderr)
    elif exit_code == INTERNAL_ERROR:
        print(f"Interná chyba!\n")

    exit(exit_code)


def process_arguments():
    arg_parse = argparse.ArgumentParser()
    arg_parse.add_argument("--source", nargs=1, help="Vstupný súbor s XML reprezentáciou zdrojového kódu.")
    arg_parse.add_argument("--input", nargs=1, help="Súbor so vstupmi pre interpretáciu zdrojového kódu.")

    load_args = vars(arg_parse.parse_args())

    print(load_args.values())


if __name__ == '__main__':
    print(f"This is interpreter\n")
    process_arguments()

