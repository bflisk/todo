from models import Task
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

LISTS = {1: "active", 2: "queue", 3: "done", 4: "trash"}

def main():
    engine = create_engine('sqlite:///todo.db')
    Session = sessionmaker(bind=engine)
    session = Session()
    
    choice = -1
    meta_choice = -1
    
    #tasks = session.query(Task).filter(Task.id == 1).first()
    while choice != 0:
        os.system('clear')
        print("TODO, or not TODO, that is the question...\n")
        print("What do you want to do? (enter number)")
        print("     1) view list")
        print("     2) add to list\n")
        print("     0) EXIT")
        
        try:
            choice = eval(input("\n>>> "))
        except:
            print("Invalid input!")

        if choice == 1:
            os.system('clear')
            print("TODO, or not TODO, that is the question...\n")
            print("What list do you want to view? (enter number)")
            print("     1) active")
            print("     2) queue")
            print("     3) done\n")
            print("     0) BACK")
            
            try:
                meta_choice = eval(input("\n>>> "))
            except:
                print("Invalid input!")
            
            if meta_choice in [1,2,3]:
                return_list(session, LISTS[meta_choice])
        elif choice == 2:
            os.system('clear')
            print("TODO, or not TODO, that is the question...\n")
            print("What list do you want to add to? (enter number)")
            print("     1) active")
            print("     2) queue")
            print("     3) done\n")
            print("     0) BACK")
            
            try:
                meta_choice = eval(input("\n>>> "))
            except:
                print("Invalid input!")
            
            if meta_choice in [1,2,3]:
                append_list(session, LISTS[meta_choice])
    
    os.system('clear')
    return

def display_list(session, list_name):
    return

def append_list(session, list_name):
    return

if __name__ == "__main__":
    main()
