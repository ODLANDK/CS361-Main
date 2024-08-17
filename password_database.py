# Name: Kyle Odland
# Course: CS361
# A password manager application that can add, delete and show password
# information. Password database structure: {'entry': number, 'site': website, 'user': username,
#                                           'password': password}

import zmq
import shelve


def main():
    # set up context for ZMQ
    context = zmq.Context()
    socket = set_up_socket(context)

    get_data, username = read_request(socket)
    db, password_db_list = get_pw_data(username)

    # make sure that database is cleaned up before sending to main program
    cleanup_database(db, password_db_list)
    socket.send_json(password_db_list)

    while True:
        action, password_data = read_request(socket)

        if action == 'add':
            add_to_db(db, password_db_list, password_data)
            response = 'Success'
        elif action == 'delete':

            delete_from_db(db, password_db_list, password_data)
            response = 'Success'
        elif action == 'get':
            # data from the socket will be the username
            get_pw_data(password_data)
            response = password_db_list
        elif action == 'quit':
            break
        else:
            response = 'error'

        # send message back to client
        socket.send_json(response)

    # exit the server program
    cleanup_database(db, password_db_list)
    db.sync()
    db.close()
    context.destroy()
    print("Server closed")


def set_up_socket(context):

    # set up a reply socket for the server
    socket = context.socket(zmq.REP)

    port = 5559
    # bind the socket to a port number
    socket.bind("tcp://*:" + str(port))
    print("Server ready to receive at port " + str(port) + "...")
    return socket


def read_request(socket):
    message = socket.recv_json()
    return message['action'], message['data']


def get_pw_data(user_name):
    db = open_database(user_name)
    password_data = db_to_json(db)

    print("Added entry: " + str(password_data) + "\n")

    return db, password_data


def open_database(user_name):
    # establish a database for password information
    db = shelve.open(user_name, "c", writeback=True)
    return db


def db_to_json(db):
    pw_list = []
    for key in db.keys():
        pw_list.append(db[key])

    return pw_list


def add_to_db(db, password_db_list, entry):

    entry['entry'] = len(password_db_list) + 1
    password_db_list.append(entry)
    db[entry['site']] = entry

    print("Added entry: " + str(entry) + "\n")


def delete_from_db(db, password_db_list, entry):

    del password_db_list[entry['entry'] - 1]
    del db[entry['site']]

    cleanup_database(db, password_db_list)

    print("Deleted entry: " + str(entry) + "\n")


def cleanup_database(db, password_db_list):
    """
    Cleans up the database entry numbers after a deletion
    :return pw_list: List of pw_list entries
    """
    new_entry_num = 0
    for entry in password_db_list:
        new_entry_num += 1
        entry['entry'] = new_entry_num

    new_entry_num = 0
    for key in db.keys():
        new_entry_num += 1
        db[key]['entry'] = new_entry_num


if __name__ == "__main__":
    main()