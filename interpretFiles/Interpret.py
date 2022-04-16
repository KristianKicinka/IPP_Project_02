# Project : IPP Projekt - 2.úloha Interpret.
# @author Kristián Kičinka (xkicin02)

from .config import *


# Objekt interpret uchováva potrebné pre chod celého skriptu.
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
        if not (self.temporary_frame is None):
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

    def frame_stack_pop(self):
        if len(self.frame_stack) == 0:
            close_script(NOT_EXISTING_FRAME)
        return self.frame_stack.pop()

    def call_stack_pop(self):
        if len(self.call_stack) == 0:
            close_script(NOT_EXISTING_FRAME)
        return self.call_stack.pop()

    def data_stack_pop(self):
        if len(self.data_stack) == 0:
            close_script(NOT_EXISTING_FRAME)
        return self.data_stack.pop()

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
