# Name: Kyle Odland
# Course: CS361
# A password manager application that can add, delete and show password
# information.

import os
import shelve

entries = 0
db = shelve.open("log", "c", writeback=True)

def clear():
    os.system('clear' or 'cls')

def home_screen():
    clear()
    print()
    print("Welcome to Passw*rd\n")
    print("Store and manage passwords for all of your websites and apps")
    print("Never forget a password again!\n")

    print("Choose how you'd like to get started:")
    commands()

def commands():

    print("Type \"list\" to go to your list of passwords")
    print("Type \"add\" to add new password information")
    print("Type \"help\" any time for help")
    print("Type \"home\" any time to return to the home screen")
    print("Type \"exit\" any time to exit the program")

def commands_additional():
    print("You can also interact with the list of password information")
    print("Here are some commands when looking at your password database: ")
    print("Type \"view [entry number]\" to view a specific entry")
    print("Type \"view [website name]\" to view the entry for that website")
    print("Type \"delete [entry number]\" to delete a specific entry")
    print("Type \"delete [website name]\" to delete the entry for that website")

def help_screen():
    clear()
    print("Here are some commands you can use in this program")
    print()
    print("The basic commands are:")
    commands()
    commands_additional()


def list_screen():
    clear()
    print("Password Information")
    print()
    i = 0
    print("Entry #   |     Website    |     User Name")
    print("------------------------------------------")
    for keys in db.keys():
        i += 1
        print(f"{db[keys]['entry']:<10}|     {db[keys]['site'].upper():<11}|"
              f"     {db[keys]['user']:<10}")

    list_options()


def list_options():
    print()
    print("Options:")
    print("add new entry")
    print("delete entry")
    print("view entry")
    print("help")


def add_screen():
    global entries
    clear()
    print("Add new password information")
    print("Enter 1 to return to list without saving")
    website = input("add website: ")

    if website == "1":
        list_screen()
    else:
        user_name = input("add username: ")
        password = input("add password: ")

        entries += 1
        db[website] = {'entry': entries, 'site': website, 'user': user_name,
                       'password': password}


def clear_database():
    db.clear()


def view_screen():
    pass


def show_screen():
    pass


def delete_screen():
    print()
    print("WARNING: Any password information you delete is gone forever")
    del_choice = input("Are you sure you want to continue? (y/n) ")
    #if del_choice.lower() == "y":




home_screen()
while True:
    print()
    user_input = input("Please choose an option: ")

    if user_input.lower() == "home":
        home_screen()
    elif user_input.lower() == "help":
        help_screen()
    elif user_input.lower() == "add":
        add_screen()
    elif user_input.lower() == "list":
        list_screen()
    elif user_input.lower() == "clear":
        clear_database()
    elif user_input.lower() == "exit":
        break

db.sync()
db.close()
print("\nExiting passw*rd...")
