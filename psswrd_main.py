# Name: Kyle Odland
# Course: CS361
# A password manager application that can add, delete and show password
# information. It can also automatically generate passwords, rate a password

import os
import zmq


def main():

    # set up context for ZMQ
    context = zmq.Context()
    db_socket = set_up_socket_database(context)
    user_socket = set_up_socket_user(context)
    encrypt_socket = set_up_socket_encrypt(context)
    gen_socket = set_up_socket_generate(context)

    current_entry = ''

    # get the verified user information
    username, user_password, valid_user = login_screen(user_socket)

    # if the user isn't authenticated, exit
    if not valid_user:
        exit_program(context)
        return

    # set up the encryption key
    encrypt_key = user_password

    # get the password database for the user in list form
    pw_list = get_database(db_socket, username)

    home_screen(username)
    while True:
        print()
        user_input = input("Please choose an option: ")

        if user_input.lower() == "home":
            home_screen(username)
        elif user_input.lower() == "help":
            help_screen(pw_list)
        elif user_input.lower() == "list":
            list_screen(pw_list)
            current_entry = ''
        elif user_input.lower() == "add":
            add_screen(pw_list, db_socket, gen_socket, encrypt_socket, encrypt_key)
        elif user_input.lower()[:6] == "delete":
            delete_screen(pw_list, db_socket, current_entry, user_input)
        elif user_input.lower()[:4] == "view":
            current_entry = view_screen(pw_list, user_input)
        elif user_input.lower() == "show":
            show_screen(pw_list, current_entry, encrypt_socket, encrypt_key)
        elif user_input.lower() == "rate":
            rate_password(gen_socket)
        elif user_input.lower() == "exit":
            break

    exit_program(context)


def set_up_socket_database(context):
    # set up a reply socket for the generate password microservice
    db_socket = context.socket(zmq.REQ)
    db_port = 5559
    # connect the socket to a port number
    db_socket.connect("tcp://localhost:" + str(db_port))
    return db_socket


def set_up_socket_user(context):
    # set up a reply socket for the generate password microservice
    user_socket = context.socket(zmq.REQ)
    encrypt_port = 5558
    # connect the socket to a port number
    user_socket.connect("tcp://localhost:" + str(encrypt_port))
    return user_socket


def set_up_socket_encrypt(context):
    # set up a reply socket for the generate password microservice
    encrypt_socket = context.socket(zmq.REQ)
    encrypt_port = 5557
    # connect the socket to a port number
    encrypt_socket.connect("tcp://localhost:" + str(encrypt_port))
    return encrypt_socket


def set_up_socket_generate(context):
    # set up a reply socket for the generate password microservice
    gen_socket = context.socket(zmq.REQ)
    gen_port = 5556
    # connect the socket to a port number
    gen_socket.connect("tcp://localhost:" + str(gen_port))
    return gen_socket


def get_database(db_socket, username):
    db_socket.send_json({'action': 'get', 'data': username})
    # password list will have a structure of [{entry 1}, {entry 2}, ...]
    # and entry structure will be {'entry': number, 'site': website,
    #                               'user': username, 'password': password}
    pw_list = db_socket.recv_json()
    return pw_list


def login_screen(user_socket):
    clear()
    print("Welcome to P*SSW*RD!")
    print("Store and manage passwords for all of your websites and apps")
    print("Never forget a password again!\n")
    print("\nEnter a username and password to log into your password manager")
    print("New users can create a P*SSW*RD account and log in\n")
    user_input = input("Sign Up or Log In? ")
    print()
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


def home_screen(username):
    """
    Displays the CLI home screen to the user
    :return None
    """
    clear()
    print()
    print("Welcome to P*SSW*RD, " + username + "\n")
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
    print("\nYou can also interact with the list of password information")
    print("Here are some commands when looking at your password database: ")
    print("Type \"view [entry number]\" to view a specific entry")
    print("Type \"delete [entry number]\" to delete a specific entry")
    print("Type \"delete [website name]\" to delete the entry for that website")
    print("Type \"rate\" to get a rating for your password")
    print("When viewing password information, here are some commands")
    print("Type \"show\" to show the current password")
    print("Type \"delete\" to delete the current password")


def list_screen(pw_list):
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
    for entry in pw_list:
        i += 1
        print(f"{entry['entry']:<10}|     {entry['site'].upper():<11}|"
              f"     {entry['user']:<10}")

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


def add_screen(pw_list, db_socket, gen_socket, encrypt_socket, encrypt_key):
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
        list_screen(pw_list)
    else:
        user_name = input("add username: ")
        password = input("add password\n"
                         "(Type generate to automatically generate a new password): ")

        if password.lower() == "generate":
            password = generate_password(gen_socket)
            print("Your randomly generated password is: ", password)

        # encrypt password before adding to database
        encrypted_password = encrypt_password(encrypt_socket, password, encrypt_key)
        add_entry = {'entry': len(pw_list) + 1, 'site': website, 'user': user_name,
                     'password': encrypted_password}

        add_entry_to_database(pw_list, db_socket, add_entry)

    list_screen(pw_list)


def generate_password(gen_socket):
    request = {"operation": "generate_password"}
    gen_socket.send_json(request)
    response = gen_socket.recv_json()
    return response["password"]


def encrypt_password(encrypt_socket, password, encrypt_key):
    request = {"action": "encrypt", "target": password, "key": encrypt_key}
    encrypt_socket.send_json(request)
    response = encrypt_socket.recv()
    return response.decode()


def decrypt_password(encrypt_socket, password, encrypt_key):
    request = {"action": "decrypt", "target": password, "key": encrypt_key}
    encrypt_socket.send_json(request)
    response = encrypt_socket.recv()
    return response.decode()


def add_entry_to_database(pw_list, db_socket, entry):
    # add entry to pw list
    pw_list.append(entry)

    # send entry to password database to add
    db_socket.send_json({'action': "add", 'data': entry})
    db_socket.recv_json()


def delete_screen(pw_list, db_socket, current_entry, user_input):
    """
    Gets the entry that the user wants to delete
    :param  current_entry, String with the entry that the user wants to delete
    :return database length as an int
    """
    print()
    print("WARNING: Deletion is permanent, your password information will be gone")
    if current_entry != '':
        delete_key = current_entry['site']
    elif user_input.lower() == "delete":
        print("Which password information would you like to delete?")
        print("Type \"back\" to go back")
        delete_key = input("Enter website or entry number: ")
    else:
        delete_key = user_input.split(" ", 1)[1]

    delete_information(pw_list, db_socket, delete_key, current_entry)


def delete_information(pw_list, db_socket, delete_key, current_entry):
    """
    Prints password information for the entry that the user wants to view
    :param  delete_key, String with the entry that the user wants to delete
    :param  current_entry, String with last entry that the user has viewed
    :return database length as an int
    """
    clear()
    # if the user entered back to return
    if delete_key.lower() == 'back':
        list_screen(pw_list)
    else:
        del_choice = input("Are you sure you want to delete this password? (y/n) ")

        if del_choice.lower() == 'n' and current_entry == '':
            list_screen(pw_list)
            return
        elif del_choice.lower() == 'n' and current_entry != '':
            # show the view screen again for the entry
            view_information(pw_list, current_entry['entry'])
            return
        elif not delete_key.isnumeric():
            for entry in pw_list:
                if entry['site'] == delete_key:
                    del pw_list[entry['entry'] - 1]
                    break
        else:
            entry = pw_list[int(delete_key) - 1]
            del pw_list[int(delete_key) - 1]

            delete_entry_from_database(db_socket, entry)
            cleanup_database(pw_list)
            list_screen(pw_list)


def delete_entry_from_database(db_socket, delete_entry):
    # structure delete request for microservice
    db_socket.send_json({'action': "delete", 'data': delete_entry})

    # get response back from microservice
    db_socket.recv_json()


def cleanup_database(pw_list):
    """
    Cleans up the database entry numbers after an addition or deletion
    :return None
    """
    new_entry_num = 0
    for entry in pw_list:
        new_entry_num += 1
        entry['entry'] = new_entry_num


def view_screen(pw_list, user_input):
    """
    Gets the entry number that the user wants to view
    :return None
    """
    if user_input.lower() == "view":
        view_entry_num = input("Which login information would you like to view? (enter #) ")
        clear()
    else:
        view_entry_num = user_input.split(" ", 1)[1]

    return view_information(pw_list, view_entry_num)


def view_information(pw_list, view_entry_num):
    """
    Prints password information for the entry that the user wants to view
    :param  view_entry, String with the entry that the user wants to view
    :return key, String that is the dictionary key for the
            entry the user wants to view
    """
    clear()
    # loop through the database
    for entry in pw_list:
        # if the entry number matches, print the user information
        if entry['entry'] == int(view_entry_num):
            print("Website:          " + entry['site'])
            print("User Name:        " + entry['user'])
            print("Password:         ******")
            break

    print_view_options()
    return entry


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


def show_screen(pw_list, entry, encrypt_socket, encrypt_key):
    """
    Gets the entry number that the user wants to view
    :param  key, String with the dictionary key for the password database dictionary
    :return None
    """
    clear()
    print("Website:          " + entry['site'])
    print("User Name:        " + entry['user'])

    # decrypt the password in the database
    password = decrypt_password(encrypt_socket, entry['password'], encrypt_key)
    print("Password:         " + password)
    print()
    input("Press enter to return to view screen... ")

    # show the view screen again for the entry
    view_information(pw_list, entry['entry'])


def rate_password(gen_socket):
    password = input("Type the password you would like to rate: ")
    request = {"operation": "rate_password", "password": password}
    gen_socket.send_json(request)
    response = gen_socket.recv_json()

    print("Your password is " + password + ":")
    print(f'Password Rating: {response["rating"]}')
    print(f'Feedback: {response["feedback"]}')


def exit_program(context):

    context.destroy()
    print("\nExiting passw*rd...")


if __name__ == "__main__":
    main()
