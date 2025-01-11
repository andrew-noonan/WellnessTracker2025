import tkinter as tk
from tkinter import simpledialog

class DynamicVar:
    def __init__(self, variable_id, conditions1, conditions2, conditions3, conditions4, conditions5, conditions6, allVals, value):
        self.variable_id = variable_id
        self.conditions1 = self.parse_conditions(conditions1)
        self.conditions2 = self.parse_conditions(conditions2)
        self.conditions3 = self.parse_conditions(conditions3)
        self.conditions4 = self.parse_conditions(conditions4)
        self.conditions5 = self.parse_conditions(conditions5)
        self.conditions6 = self.parse_conditions(conditions6)
        self.allVals = allVals
        self.value = 'N/A'  # This will store the current value(s) for the variable.

    def parse_conditions(self, conditions_str):
        """Parses a condition string into a list of subconditions (tuples)."""
        if not conditions_str:
            return []
        # Split by comma and strip whitespace, then group into tuples
        parts = [part.strip() for part in conditions_str.split(',')]
        return [(parts[i], parts[i + 1]) for i in range(0, len(parts), 2)]
    def __str__(self):
        """Returns a string representation of the variable."""
        cond_strs = []
        for cond in (self.conditions1, self.conditions2, self.conditions3,self.conditions4, self.conditions5, self.conditions6):
            cond_strs.append('; '.join([f"{subcond[0]}: {subcond[1]}" for subcond in cond]))
        conditions_str = ' | '.join(filter(None, cond_strs))  # Filters out empty conditions
        value_str = self.value
        return f"ID: {self.variable_id} Conditions: [{conditions_str}], Value: {value_str}"

class Question:
    def __init__(self, question_id, question_type, conditions1, conditions2, conditions3, prompt):
        self.question_id = question_id
        self.type = question_type
        self.conditions1 = self.parse_conditions(conditions1)
        self.conditions2 = self.parse_conditions(conditions2)
        self.conditions3 = self.parse_conditions(conditions3)
        self.prompt = prompt
        self.values = []  # This will store the current value(s) for the question.
        self.asked = False
        self.conditionsSatisfied = False
        self.dependents = set()

    def parse_conditions(self, conditions_str):
        """Parses a condition string into a list of subconditions (tuples)."""
        if not conditions_str:
            return []
        # Split by comma and strip whitespace, then group into tuples
        parts = [part.strip() for part in conditions_str.split(',')]
        return [(parts[i], parts[i + 1]) for i in range(0, len(parts), 2)]
    
    def __str__(self):
        """Returns a string representation of the question."""
        cond_strs = []
        for cond in (self.conditions1, self.conditions2, self.conditions3):
            cond_strs.append('; '.join([f"{subcond[0]}: {subcond[1]}" for subcond in cond]))
        conditions_str = ' | '.join(filter(None, cond_strs))  # Filters out empty conditions
        value_str = ', '.join(self.values) if self.values else "n/a"
        return f"ID: {self.question_id}, Prompt: {self.prompt}, Conditions: [{conditions_str}], Value: {value_str}, Conditions Satisfied: {self.conditionsSatisfied}, Dependents: [{self.dependents}]"

# Inherited Checkbox Question Class
class CheckboxQuestion(Question):
    def __init__(self, question_id, question_type, conditions1, conditions2, conditions3, prompt, options):
        super().__init__(question_id, question_type, conditions1, conditions2, conditions3, prompt)
        self.options = options

