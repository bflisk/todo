from venv import create

from sqlalchemy.orm.sync import clear

from models import Task
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker
import os
import time
from datetime import datetime, timedelta

LISTS = {1: "active", 2: "queue", 3: "done"}
ACTIVE_LIST_TASK_CAP = 5

def main():
    engine = create_engine('sqlite:///todo.db')
    Session = sessionmaker(bind=engine)
    session = Session()
    
    desired_list = -1
    action = -1
    
    #tasks = session.query(Task).filter(Task.id == 1).first()
    while desired_list != 0:
        clear_screen()
        print("\033[32mTODO, or not TODO, that is the question...\n")
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
            print("     2) add to list\n")
            print("     0) BACK")
            
            try:
                action = eval(input("\n>>> "))
            except:
                print("Invalid input!")
            
            if action == 1:
                # view list
                tasks = read_list_from_db(Session, desired_list)
                display_page(Session, desired_list, tasks, 0, 5, len(tasks))
            elif action == 2:
                # add to list
                if desired_list == 1:
                    # cap the active list to a certain number of tasks
                    active_list_task_count = session.query(Task).filter(Task.status == 1).count()
                    if active_list_task_count < ACTIVE_LIST_TASK_CAP:
                        create_new_task(Session, desired_list)
                    else:
                        print("Too many active tasks!")
                        time.sleep(2)
                else:
                    create_new_task(Session, desired_list)
    
    clear_screen()
    return

def read_list_from_db(Session, list_id):
    session = Session()
    tasks = session.query(Task).filter(Task.status == list_id).order_by(desc(Task.rot)).all()
    return tasks

def create_new_task(Session, list_id):
    session = Session()

    clear_screen()
    try:
        title = input("Title: ")
        description = input("Description: ")
        difficulty = eval(input("Expected difficulty: "))
        project = input("Project: ")
        days_to_add = eval(input("Days to complete: "))
    except:
        print("Invalid input!")
        time.sleep(2)
        return

    # generate create_date
    current_time = time.localtime()
    formatted_date = time.strftime("%Y-%m-%d", current_time)

    # generate due_date given user input
    date_obj = datetime.strptime(formatted_date, "%Y-%m-%d")
    due_date = date_obj + timedelta(days=days_to_add)
    due_date_formatted = due_date.strftime("%Y-%m-%d")

    new_task = Task(
        title=title,
        description=description,
        difficulty=difficulty,
        project=project,
        due_date=due_date_formatted,
        create_date=formatted_date,
        status=list_id,
        rot=1
    )

    session.add(new_task)
    session.commit()

    return

# displays ONE PAGE of a user-requested list and allows user to take action on 1 task in that page. Handles multiple pages through recursion.
# Returns when the user no longer wants to view the list.
def display_page(Session, list_id, l, item_index, page_size, total_task_count):
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
    print(f'\n{'<<< back [b] | forward [f] | task action [id of task] | exit [ENTER] >>>':^{total_line_width}}')
    direction = input()

    if direction == 'f':
        item_index = item_index + page_size if item_index + page_size <= total_task_count else page_size
        display_page(Session, list_id, l, item_index, page_size, total_task_count)
    elif direction == 'b':
        item_index = item_index - page_size if item_index + page_size > item_index + page_size else 0 # ensures item_index cannot be less than zero
        display_page(Session, list_id, l, item_index, page_size, total_task_count)
    elif direction.isnumeric():
        # the user wants to perform an action on a specific task
        take_action_on_task(Session, list_id, direction)
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

# displays a menu for a given task for the user to interact with. Perform designated action.
def take_action_on_task(Session, list_id, task_id):
    clear_screen()

    session = Session()
    task = session.query(Task).filter(Task.id == task_id).filter(Task.status == list_id).first()

    if task:
        choice = -1
        while choice not in [1,2,3,0]:
            clear_screen()
            print("TODO, or not TODO, that is the question...\n")
            print("What do you want to do with this task? (enter number)")
            print("     1) mark as complete")
            print("     2) move to other list")
            print("     3) delete\n")
            print("     0) BACK")

            try:
                choice = eval(input("\n>>> "))
            except:
                pass

            if choice == 1:
                # mark as complete
                session.query(Task).filter(Task.id == task_id).update({Task.status: 3})
                session.commit()
                print("\033[33mEPIC!!!\033[32m")
            elif choice == 2:
                clear_screen()
                # move to other list
                print("Which list would you like to move this task to?")
                print("     1) active")
                print("     2) queue")
                print("     3) done\n")
                print("     0) BACK")

                try:
                    move_list_choice = eval(input("\n>>> "))
                except:
                    return

                if move_list_choice in [1,2,3]:
                    if move_list_choice == 1:
                        # cap the active list to a certain number of tasks
                        active_list_task_count = session.query(Task).filter(Task.status == 1).count()
                        if active_list_task_count < ACTIVE_LIST_TASK_CAP:
                            session.query(Task).filter(Task.id == task_id).update({Task.status: move_list_choice})
                            session.commit()
                        else:
                            print("Too many active tasks!")
                            time.sleep(2)
                    else:
                        session.query(Task).filter(Task.id == task_id).update({Task.status: move_list_choice})
                        session.commit()
            elif choice == 3:
                # delete task
                clear_screen()
                print(f"Are you sure you want to delete task with id {task_id} and title {task.title}? (y/n)")
                delete_confirmation = input(">>> ")

                if delete_confirmation == 'y':
                    session.query(Task).filter(Task.id == task_id).delete()
                    session.commit()
    else:
        print(f"No task exists with id {task_id} in this list! (Press ENTER to continue)")
        input()

    return

def get_from_list(my_list, index, default=None):
    # returns
    try:
       return my_list[index]
    except:
       return default

# retrieves a single task from the db using task id
def retrieve_task(Session, task_id):
    session = Session()
    task = session.query(Task).filter(Task.id == task_id).first()
    return task

def append_list(session, list_name):
    return

# OS-agnostic function to clear the screen
def clear_screen():
    if os.name == 'posix':  # Unix-based systems
        os.system('clear')
    elif os.name == 'nt':  # Windows
        os.system('cls')

    return

if __name__ == "__main__":
    main()
