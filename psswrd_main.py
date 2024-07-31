# Name: Kyle Odland
# Course: CS361
# A password manager application that can add, delete and show password
# information.

import os
import shelve


def clear():
    """
    Clears the terminal window
    :return None
    """
    os.system('clear' or 'cls')


def home_screen():
    """
    Displays the CLI home screen to the user
    :return None
    """
    clear()
    print()
    print("Welcome to Passw*rd\n")
    print("Store and manage passwords for all of your websites and apps")
    print("Never forget a password again!\n")

    print("Choose how you'd like to get started:")
    commands()


def help_screen():
    """
    Displays the help screen to the user
    :return None
    """
    clear()
    print("Here are some commands you can use in this program")
    print()
    print("The basic commands are:")
    commands()
    commands_additional()
    input("Press enter to return... ")
    list_screen()


def commands():
    """
    Prints user commands to the console
    :return None
    """
    print("Type \"list\" to go to your list of passwords")
    print("Type \"add\" to add new password information")
    print("Type \"help\" any time for help")
    print("Type \"home\" any time to return to the home screen")
    print("Type \"exit\" any time to exit the program")


def commands_additional():
    """
    Prints additional user commands to the console
    :return None
    """
    print("You can also interact with the list of password information")
    print("Here are some commands when looking at your password database: ")
    print("Type \"view [entry number]\" to view a specific entry")
    #print("Type \"view [website name]\" to view the entry for that website")
    print("Type \"delete [entry number]\" to delete a specific entry")
    print("Type \"delete [website name]\" to delete the entry for that website")

    print("When viewing password information, here are some commands")
    print("Type \"show\" to show the current password")
    print("Type \"delete\" to delete the current password")


def list_screen():
    """
    Displays the user's list of password information
    :return None
    """
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

    print_list_options()


def print_list_options():
    """
    Prints the commands that can be made from the list screen
    :return None
    """
    print()
    print("Options:")
    print("add new entry")
    print("delete entry")
    print("view entry")
    print("help")


def add_screen():
    """
    Prompts the user to add a new password to the password database
    :return None
    """
    clear()

    # prompt the user for password information
    print("Add new password information")
    print("Enter 1 to return to list without saving")
    website = input("add website: ")

    # return to list if the user enters 1
    if website == "1":
        list_screen()
    else:
        user_name = input("add username: ")
        password = input("add password: ")

        # add information to the password database
        db[website] = {'entry': len(db) + 1, 'site': website, 'user': user_name,
                       'password': password}

    cleanup_database()
    list_screen()


def view_screen():
    """
    Gets the entry number that the user wants to view
    :return None
    """
    if user_input.lower() == "view":
        view_entry = input("Which login information would you like to view? (enter #) ")
        clear()
    else:
        view_entry = user_input.split(" ", 1)[1]

    return view_information(view_entry)


def view_information(view_entry):
    """
    Prints password information for the entry that the user wants to view
    :param  view_entry, String with the entry that the user wants to view
    :return key, String that is the dictionary key for the
            entry the user wants to view
    """
    clear()
    # loop through the database
    for key in db.keys():
        # if the entry number matches, print the user information
        if db[key]['entry'] == int(view_entry):
            print("Website:          " + db[key]['site'])
            print("User Name:        " + db[key]['user'])
            print("Password:         ******")

    print_view_options()
    return key


def print_view_options():
    """
    Prints the commands that can be made from the view screen
    :return None
    """
    print()
    print("Options:")
    print("show password")
    print("delete password information")
    print("back to list")
    print("help")
    print("exit")


def show_screen(key):
    """
    Gets the entry number that the user wants to view
    :param  key, String with the dictionary key for the password database dictionary
    :return None
    """
    clear()
    print("Website:          " + db[key]['site'])
    print("User Name:        " + db[key]['user'])
    print("Password:         " + db[key]['password'])
    print()
    input("Press enter to return to view screen... ")

    # show the view screen again for the entry
    view_information(db[key]['entry'])


def delete_screen(current_entry):
    """
    Gets the entry that the user wants to delete
    :param  current_entry, String with the entry that the user wants to delete
    :return database length as an int
    """
    print("WARNING: Deletion is permanent, your password information will be gone")
    if current_entry != '':
        delete_key = current_entry
    elif user_input.lower() == "delete":
        print("Which password information would you like to delete?")
        print("Type \"back\" to go back")
        delete_key = input("Enter website or entry number: ")
    else:
        delete_key = user_input.split(" ", 1)[1]

    return delete_information(delete_key, current_entry)


def delete_information(delete_entry, current_entry):
    """
    Prints password information for the entry that the user wants to view
    :param  delete_entry, String with the entry that the user wants to delete
    :param  current_entry, String with last entry that the user has viewed
    :return database length as an int
    """
    clear()
    # if the user entered back to return
    if delete_entry.lower() == 'back':
        list_screen()
    else:
        del_choice = input("Are you sure you want to delete this password? (y/n) ")

        if del_choice.lower() == 'n' and current_entry == '':
            list_screen()
        elif del_choice.lower() == 'n' and current_entry != '':
            # show the view screen again for the entry
            view_information(current_entry)
        elif not delete_entry.isnumeric():
            del db[delete_entry]
        else:
            for key in db.keys():
                if db[key]['entry'] == int(delete_entry):
                    del db[key]

        cleanup_database()
        list_screen()


def cleanup_database():
    """
    Cleans up the database entry numbers after an addition or deletion
    :return None
    """
    new_entry_num = 0
    for key in db.keys():
        new_entry_num += 1
        db[key]['entry'] = new_entry_num


# establish a database for password information
db = shelve.open("log", "c", writeback=True)
current_key = ''
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
        current_key = ''
    elif user_input.lower()[:4] == "view":
        current_key = view_screen()
    elif user_input.lower() == "show":
        show_screen(current_key)
    elif user_input.lower()[:6] == "delete":
        delete_screen(current_key)
    elif user_input.lower() == "exit":
        break

db.sync()
db.close()
print("\nExiting passw*rd...")
