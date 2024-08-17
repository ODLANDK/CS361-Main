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
    password_db_list = get_pw_data(username)
    socket.send_json(password_db_list)

    while True:
        action, data = read_request(socket)

        if action == 'add':
            #password_db_list = add_to_db(data, password_db_list)
            add_to_db(data, password_db_list)
            response = 'Success'
        elif action == 'delete':
            #password_db_list = delete_from_db(data, password_db_list)
            delete_from_db(data, password_db_list)
            response = 'Success'
        elif action == 'get':
            # data from the socket will be the username
            #password_db_list = get_pw_data(data)
            get_pw_data(data)
            response = password_db_list
        elif action == 'quit':
            break
        else:
            response = 'error'

        # send message back to client
        socket.send_json(response)

    # exit the server program
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
    return password_data


def open_database(user_name):
    # establish a database for password information
    db = shelve.open(user_name, "c", writeback=True)
    return db


def db_to_json(db):
    pw_list = []
    for key in db.keys():
        pw_list.append(db[key])

    return pw_list


def add_to_db(entry, password_db_list):

    entry['entry'] = len(password_db_list) + 1
    password_db_list.append(entry)
    print("Added entry: " + str(entry) + "\n")
    #return password_db_list


def delete_from_db(entry, password_db_list):

    del password_db_list[entry['entry'] - 1]
    cleanup_list(password_db_list)

    print("Deleted entry: " + str(entry) + "\n")
    #return pw_list


def cleanup_list(pw_list):
    """
    Cleans up the database entry numbers after a deletion
    :return pw_list: List of pw_list entries
    """
    new_entry_num = 0
    for entry in pw_list:
        new_entry_num += 1
        entry['entry'] = new_entry_num

    #return pw_list


if __name__ == "__main__":
    main()