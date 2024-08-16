# Name: Kyle Odland
# Course: CS361
# A password manager application that can add, delete and show password
# information.

import os
import shelve
import zmq


def main():

    # set up context for ZMQ
    context = zmq.Context()
    gen_socket = set_up_socket_generate(context)
    encrypt_socket = set_up_socket_encrypt(context)
    user_socket = set_up_socket_user(context)

    current_entry = ''

    user_name, user_password, valid_user = login_screen(user_socket)
    encrypt_key = user_password
    db = open_database(user_name)

    if not valid_user:
        exit_program(db, context)
        return

    home_screen()
    while True:
        print()
        user_input = input("Please choose an option: ")

        if user_input.lower() == "home":
            home_screen()
        elif user_input.lower() == "help":
            help_screen(db)
        elif user_input.lower() == "list":
            list_screen(db)
            current_entry = ''
        elif user_input.lower() == "add":
            add_screen(db, gen_socket, encrypt_socket, encrypt_key)
        elif user_input.lower()[:6] == "delete":
            delete_screen(db, current_entry, user_input)
        elif user_input.lower()[:4] == "view":
            current_entry = view_screen(db, user_input)
        elif user_input.lower() == "show":
            show_screen(db, current_entry, encrypt_socket, encrypt_key)
        elif user_input.lower() == "rate":
            rate_password(gen_socket)
        elif user_input.lower() == "exit":
            break

    exit_program(db, context)


def set_up_socket_generate(context):
    # set up a reply socket for the generate password microservice
    gen_socket = context.socket(zmq.REQ)
    gen_port = 5556
    # connect the socket to a port number
    gen_socket.connect("tcp://localhost:" + str(gen_port))
    return gen_socket


def set_up_socket_encrypt(context):
    # set up a reply socket for the generate password microservice
    encrypt_socket = context.socket(zmq.REQ)
    encrypt_port = 5557
    # connect the socket to a port number
    encrypt_socket.connect("tcp://localhost:" + str(encrypt_port))
    return encrypt_socket


def set_up_socket_user(context):
    # set up a reply socket for the generate password microservice
    user_socket = context.socket(zmq.REQ)
    encrypt_port = 5558
    # connect the socket to a port number
    user_socket.connect("tcp://localhost:" + str(encrypt_port))
    return user_socket


def open_database(user_name):
    # establish a database for password information
    db = shelve.open(user_name, "c", writeback=True)
    return db


def login_screen(user_socket):
    clear()
    print("Welcome to P*SSW*RD!")
    print("Enter a username and password to log into your password manager")
    print("New users can create a P*ssw*rd account and log in")
    user_input = input("Sign up or Log in? ")
    if user_input.lower() == "sign up":
        username = input("Username: ")
        user_password = input("Password: ")

        return username, user_password, add_user(user_socket, username, user_password)
    else:
        print("Enter the correct username and password within 3 tries")
        for i in range(1,4):
            print("Attempt " + str(i))
            username = input("Username: ")
            user_password = input("Password: ")
            # if the user logs in with the correct information
            verified_user = authenticate(user_socket, username, user_password)
            if verified_user:
                break

        return username, user_password, verified_user


def authenticate(user_socket, user, password):
    request = {"action": "check", "username": user, "password": password}
    user_socket.send_json(request)
    response = user_socket.recv()
    return response.decode() == 'True'


def add_user(user_socket, username, password):
    request = {"action": "add", "username": username, "password": password}
    user_socket.send_json(request)
    response = user_socket.recv()
    return response.decode() == 'True'


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
    print("Welcome to P*ssw*rd\n")
    print("Store and manage passwords for all of your websites and apps")
    print("Never forget a password again!\n")

    print("Choose how you'd like to get started:")
    commands()


def help_screen(db):
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
    list_screen(db)


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
    print("Type \"rate\" to get a rating for your password")
    print("When viewing password information, here are some commands")
    print("Type \"show\" to show the current password")
    print("Type \"delete\" to delete the current password")


def list_screen(db):
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
    print("rate password")
    print("help")
    print("exit")


def add_screen(db, gen_socket, encrypt_socket, encrypt_key):
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
        list_screen(db)
    else:
        user_name = input("add username: ")
        password = input("add password\n"
                         "Type generate to automatically generate a new password: ")

        if password.lower() == "generate":
            password = generate_password(gen_socket)

        # encrypt password before adding to database
        encrypted_password = encrypt_password(encrypt_socket, password, encrypt_key)
        db[website] = {'entry': len(db) + 1, 'site': website, 'user': user_name,
                       'password': encrypted_password}

    cleanup_database(db)
    list_screen(db)


def generate_password(gen_socket):
    request = {"operation": "generate_password"}
    gen_socket.send_json(request)
    response = gen_socket.recv_json()
    return response["password"]


def rate_password(gen_socket):
    password = input("Type the password you would like to rate: ")
    request = {"operation": "rate_password", "password": password}
    gen_socket.send_json(request)
    response = gen_socket.recv_json()

    print("Your password is " + password + ":")
    print(f'Password Rating: {response["rating"]}')
    print(f'Feedback: {response["feedback"]}')


def encrypt_password(encrypt_socket, password, encrypt_key):
    request = {"task": "encrypt", "target": password, "key": encrypt_key}
    encrypt_socket.send_json(request)
    response = encrypt_socket.recv()
    return response.decode()


def decrypt_password(encrypt_socket, password, encrypt_key):
    request = {"task": "decrypt", "target": password, "key": encrypt_key}
    encrypt_socket.send_json(request)
    response = encrypt_socket.recv()
    return response.decode()


def cleanup_database(db):
    """
    Cleans up the database entry numbers after an addition or deletion
    :return None
    """
    new_entry_num = 0
    for key in db.keys():
        new_entry_num += 1
        db[key]['entry'] = new_entry_num


def view_screen(db, user_input):
    """
    Gets the entry number that the user wants to view
    :return None
    """
    if user_input.lower() == "view":
        view_entry = input("Which login information would you like to view? (enter #) ")
        clear()
    else:
        view_entry = user_input.split(" ", 1)[1]

    return view_information(db, view_entry)


def view_information(db, view_entry):
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
            break

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


def show_screen(db, key, encrypt_socket, encrypt_key):
    """
    Gets the entry number that the user wants to view
    :param  key, String with the dictionary key for the password database dictionary
    :return None
    """
    clear()
    print("Website:          " + db[key]['site'])
    print("User Name:        " + db[key]['user'])

    # decrypt the password in the database
    password = decrypt_password(encrypt_socket, db[key]['password'], encrypt_key)
    print("Password:         " + password)
    print()
    input("Press enter to return to view screen... ")

    # show the view screen again for the entry
    view_information(db, db[key]['entry'])


def delete_screen(db, current_entry, user_input):
    """
    Gets the entry that the user wants to delete
    :param  current_entry, String with the entry that the user wants to delete
    :return database length as an int
    """
    print()
    print("WARNING: Deletion is permanent, your password information will be gone")
    if current_entry != '':
        delete_key = current_entry
    elif user_input.lower() == "delete":
        print("Which password information would you like to delete?")
        print("Type \"back\" to go back")
        delete_key = input("Enter website or entry number: ")
    else:
        delete_key = user_input.split(" ", 1)[1]

    return delete_information(db, delete_key, current_entry)


def delete_information(db, delete_entry, current_entry):
    """
    Prints password information for the entry that the user wants to view
    :param  delete_entry, String with the entry that the user wants to delete
    :param  current_entry, String with last entry that the user has viewed
    :return database length as an int
    """
    clear()
    # if the user entered back to return
    if delete_entry.lower() == 'back':
        list_screen(db)
    else:
        del_choice = input("Are you sure you want to delete this password? (y/n) ")

        if del_choice.lower() == 'n' and current_entry == '':
            list_screen(db)
        elif del_choice.lower() == 'n' and current_entry != '':
            # show the view screen again for the entry
            view_information(db, current_entry)
        elif not delete_entry.isnumeric():
            del db[delete_entry]
        else:
            for key in db.keys():
                if db[key]['entry'] == int(delete_entry):
                    del db[key]

        cleanup_database(db)
        list_screen(db)

def exit_program(db, context):
    db.sync()
    db.close()
    context.destroy()
    print("\nExiting passw*rd...")


if __name__ == "__main__":
    main()
