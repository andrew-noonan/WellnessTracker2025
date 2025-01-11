# Entry point of the application
from helperClasses import Question, CheckboxQuestion
from helperFuncs import *

def main():
    """********************************** CONFIG **********************************"""
    config_filepath = r'C:\Users\anoon\Desktop\Code Dev\DynamicLicenseGenerator\templates\config1.xlsx'
    template_filepath = r'C:\Users\anoon\Desktop\Code Dev\DynamicLicenseGenerator\templates\template1.docx'
    output_directory = r'C:\Users\anoon\Desktop\Code Dev\DynamicLicenseGenerator\outputs'
    
    """********************************** QUESTION IMPORTING AND ASKING **********************************"""
    # Import all questions
    questions_dict = {}
    all_questions = importQuestions(config_filepath)

    # Create dictionary with QID as key
    for question in all_questions:
        questions_dict[question.question_id] = question

    # Add list of dependents to each one
    addDependents(questions_dict)

    # Check all initial question conditions - set conditionless to true
    for question in all_questions:
        check_question_conditions(question,questions_dict)

    # Recursively ask all questions
    for q in questions_dict.values():
        recursive_ask(q,questions_dict)
    # Print all questions and answers before proceeding with variable replacement
    print("\nQUESTIONS\n")
    for q in questions_dict.values():
        print(q)

    """********************************** VARIABLE IMPORTING **********************************"""
    # Detect all variable targerts in the template 
    found_variables = import_vars_from_template(template_filepath)

    # Create dictionary with static variable values - this will serve as template context
    variable_values = load_static_variables(config_filepath)

    # Add N/A to variables not defined in static section but found as target
    for var in found_variables.keys(): 
        if var not in variable_values.keys():
            variable_values[var] = "N/A"
        if "sec" in var:
            variable_values[var] = "{{" + var + "}}"
    
    # Import dynamic variable object dictionary from excel
    print("\nDYNAMIC VARIABLES\n")
    dynamic_var_dict = load_dynamic_variables(config_filepath, questions_dict)
    for var in dynamic_var_dict.values():
        print(var)
        variable_values[var.variable_id] = var.value

    print("\nGENERATING INTERMEDIATE REPORT\n")
    # First report allows for section numbering and internal variable placeholders
    intermediate_path = replace_template(template_filepath, variable_values, output_directory)

    finishing_touches(intermediate_path, questions_dict)

if __name__ == "__main__":
    main()
