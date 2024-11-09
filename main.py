from models import Task
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker
import os

LISTS = {1: "active", 2: "queue", 3: "done", 4: "trash"}

def main():
    engine = create_engine('sqlite:///todo.db')
    Session = sessionmaker(bind=engine)
    session = Session()
    
    desired_list = -1
    action = -1
    
    #tasks = session.query(Task).filter(Task.id == 1).first()
    while desired_list != 0:
        clear_screen()
        print("TODO, or not TODO, that is the question...\n")
        print("What list do you want to interact with? (enter number)")
        print("     1) active")
        print("     2) queue")
        print("     3) done\n")
        print("     0) EXIT")
        
        try:
            desired_list = eval(input("\n>>> "))
        except:
            print("Invalid input!")

        if desired_list in [1,2,3]:
            clear_screen()
            print("TODO, or not TODO, that is the question...\n")
            print("What do you want to do? (enter number)")
            print("     1) view list")
            print("     2) add to list")
            print("     3) mark as done") if desired_list in [1, 2] else 0 # Do not allow this option for the "done" list
            print("     4) delete from list\n")
            print("     0) BACK")
            
            try:
                action = eval(input("\n>>> "))
            except:
                print("Invalid input!")
            
            if action == 1:
                tasks = read_list_from_db(Session, desired_list)
                display_page(tasks, 0, 5, len(tasks))
    
    clear_screen()
    return

def read_list_from_db(Session, list_id):
    session = Session()
    tasks = session.query(Task).filter(Task.status == list_id).order_by(desc(Task.rot)).all()
    return tasks

# displays ONE PAGE of a user-requested list. Handles multiple pages through recursion. Returns when the user no longer wants to view the list.
def display_page(l, item_index, page_size, total_task_count):
    clear_screen()

    page = l[item_index:item_index + page_size] # the current page
    line = ""  # equals one line in the terminal
    divider = ' | ' # sets the divider character between columns

    # print column names
    printable_item = init_printable_item()
    total_line_width = 0 # used later to render forward and back buttons
    for k in printable_item.keys():
        line += f'{k:<{printable_item[k]["column_length"]}}' + divider
        total_line_width += (printable_item[k]["column_length"] + len(divider.expandtabs())) # add length of divider
    # os.system(f"printf '\\e[8;{100};{total_line_width}t'") # sets terminal window size
    print('-' * total_line_width)
    print(line)
    print('.' * total_line_width)

    # create a printable item for each item and print it
    for item in page:
        printable_item = init_printable_item()

        # converts the sqlalchemy object into a dictionary
        item_dict = item.__dict__

        # remove columns that I do not want to print!
        item_dict.pop("_sa_instance_state") if item_dict.get("_sa_instance_state") else 0
        item_dict.pop("status") if item_dict.get("status") else 0

        # loop through each column, chop up its text based on its allowed column text length
        for column_name in item_dict.keys():
            full_column_text = str(item_dict[column_name])
            column_length = printable_item[column_name]["column_length"]

            i = 0
            while i < len(full_column_text):
                # loop through the string of current column and add these blocks one at a time
                substring = f'{full_column_text[i:i + column_length]:<{column_length}}' # add padding based on line sizes defined in "column_sizes"

                printable_item[column_name]["text"].append(substring)
                i += column_length

        print_printable_item(printable_item, divider=divider)

    # handle pagination based on user input
    print('-' * total_line_width)
    print(f'\n{'<<< back [b] | forward [f] | exit [e] >>>':^{total_line_width}}')
    direction = input()

    if direction == 'f':
        item_index = item_index + page_size if item_index + page_size <= total_task_count else page_size
        display_page(l, item_index, page_size, total_task_count)
    elif direction == 'b':
        item_index = item_index - page_size if item_index + page_size > item_index + page_size else 0 # ensures item_index cannot be less than zero
        display_page(l, item_index, page_size, total_task_count)
    elif direction == 'e':
        return

    return

# prints the printable item via printing each row of each item in the printable item one at a time
def print_printable_item(printable_item, divider=''):
    # calculate the maximum number of lines required for any column in the printable item
    max_depth = 0
    for k in printable_item.keys():
        max_depth = len(printable_item[k]["text"]) if len(printable_item[k]["text"]) > max_depth else max_depth

    # feed lines to buffer and print line by line
    for depth in range(max_depth):
        line = ""

        for k in printable_item.keys():
            line += f'{get_from_list(printable_item[k]["text"], depth, default=''):<{printable_item[k]["column_length"]}}' + divider

        print(line)

    return

# This object stores the column of a task as lists of texts corresponding to rows to be printed later.
# A list will have multiple items if the column text is too large to fit in a column length-wise, defined by "column_length".
def init_printable_item():
    # TODO: Make this reactive to the terminal size
    p = {
        "id": {
            "column_length": 4,
            "text": []
        },
        "title": {
            "column_length": 10,
            "text": []
        },
        "description": {
            "column_length": 60,
            "text": []
        },
        "difficulty": {
            "column_length": 10,
            "text": []
        },
        "project": {
            "column_length": 7,
            "text": []
        },
        "due_date": {
            "column_length": 12,
            "text": []
        },
        "create_date": {
            "column_length": 12,
            "text": []
        },
        "rot": {
            "column_length": 3,
            "text": []
        }
    }

    return p

def get_from_list(my_list, index, default=None):
    # returns
    try:
       return my_list[index]
    except:
       return default

def append_list(session, list_name):
    return

def clear_screen():
    # OS-agnostic function to clear the screen
    if os.name == 'posix':  # Unix-based systems
        os.system('clear')
    elif os.name == 'nt':  # Windows
        os.system('cls')

    return

if __name__ == "__main__":
    main()
