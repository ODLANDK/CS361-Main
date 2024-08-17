# Name: Kyle Odland
# Course: CS361
# A microservice to authenticate users of the P*ssw*rd app, and to add new users
# user database structure: {'user_id': number, 'user': username,
#                                            'password': password}

import zmq
import shelve


def set_up_socket(context):

    # set up a reply socket for the server
    socket = context.socket(zmq.REP)

    port = 5558
    # bind the socket to a port number
    socket.bind("tcp://*:" + str(port))
    print("Server ready to receive at port " + str(port) + "...")
    return socket


def read_request(socket):
    message = socket.recv_json()

    return message['action'], message['username'], message['password']


def open_database():
    # establish a database for password information
    db = shelve.open("users", "c", writeback=True)
    return db


def add_user(db, user, pw):
    if user in db:
        return False
    else:
        db[user] = {'user_id': len(db) + 1, 'username': user, 'password': pw}
        db.sync()
        return True


def authenticate_user(db, check_username, check_password):
    for key in db.keys():
        if check_username == db[key]['username'] and check_password == db[key]['password']:
            print("Logged in successfully")
            return True

    print("Login failed...")
    return False


def main():
    # set up context for ZMQ
    context = zmq.Context()

    socket = set_up_socket(context)
    db = open_database()

    while True:
        action, username, password = read_request(socket)

        # show what the microservice is doing
        if action == 'check':
            print("Authenticating " + username + "\n")
        elif action == 'add':
            print("Adding new user " + username + "\n")

        if action == 'add':
            response = add_user(db, username, password)
        elif action == 'check':
            response = authenticate_user(db, username, password)
        elif action == 'quit':
            break
        else:
            response = False



        # send message back to client
        socket.send_string(str(response))

    db.sync()
    db.close()
    # exit the server program
    context.destroy()
    print("Server closed")


if __name__ == "__main__":
    main()