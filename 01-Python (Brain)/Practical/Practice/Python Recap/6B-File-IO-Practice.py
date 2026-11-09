# This is a practice program used to create md files
import Magnum;

class CustomError(Exception):
    pass
"""
This is the dict of file type and list of values of that dict
we are able to create using this program
"""
file_type = {"Markdown": "md", "Text": "txt"}
file_extension = list(file_type.values())

markdown_details = [
    "Headings: Use hastag (#) to make Headings and subheadings, the more hashtags the smaller the subheading",
    "Lists: Use dash (-) to make a list",
    "Horizontal Line: Use three consecutive dashes (---) to make horizontal line"
]

"""
This function is used to check whenever the user is allowed to input
whether of not the user would like to quit

Note: if the input is an integer only don't forget to convert it
as follows --> [variable_name] = int([variable_name])
"""
def check_quit(user_input):
    if user_input.lower() == "q" or user_input.lower() == "quit":
        return False
    return True

def error_message(message):
    Magnum.dash(10, '*')
    print(F"Error: {message}")
    Magnum.dash(10, '*')


program_running = True
while(program_running):
    # 1. Ask the user which file type they would like to create
    print("Choose file to create")

    # List choices
    for index, file in enumerate(file_type, start = 1):
        print(f" {index}. {file}")

    Magnum.dash()

    try:
        # The user makes a choice
        file_choice = input("Choice: ")
        # refer to function definition comment
        program_running = check_quit(file_choice)
        if program_running == False:
            print("Exiting program...")
            break
        file_choice = int(file_choice)

        # if the users choice is not one of the numbers listed, it will present an error
        if file_choice > len(file_type) or file_choice < 1:
            raise CustomError(f"Please enter a valid number between 1 and {len(file_type)}")
    except ValueError as e:  # if the user enters anything other than a number
        error_message(f"{e}")
    except CustomError as e:
        error_message(e)
    finally:
        Magnum.dash()

    # 2. Create the File

    # Get the file name
    file_name = input("Enter file name: ")
    program_running = check_quit(file_name)
    if program_running == False:
        print("Exiting program...")
        break

    Magnum.dash()
    
    print("Paste or Write the content of the file (You can't quit)\n",
    "Type '[FILE CLOSE]' when you are done after every input")
    Magnum.dash(8, '=')
    print("[FILE OPEN]")
    Magnum.dash(8, '=')

    # Getting the file
    file_content = ""
    file_open = True
    while(file_open):
        content = input()
        if(content == "[FILE CLOSE]"):
            file_open = False
            break
        else:
            file_content += content

    # Creating the file
    extension = file_extension[file_choice - 1]
    with open(f"{file_name}.{extension}", "w") as f:
        f.write(file_content)
        
    Magnum.dash()
