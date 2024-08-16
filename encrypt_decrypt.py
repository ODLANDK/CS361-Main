# Name: Kyle Odland
# Course: CS361
# A microservice to encrypt or decrypt a string with a given key

import cryptocode
import zmq


def set_up_socket(context):

    # set up a reply socket for the server
    socket = context.socket(zmq.REP)

    port = 5557
    # bind the socket to a port number
    socket.bind("tcp://*:" + str(port))
    print("Server ready to receive at port " + str(port) + "...")
    return socket


def read_request(socket):
    message = socket.recv_json()

    return message['action'], message['target'], message['key']


def main():
    # set up context for ZMQ
    context = zmq.Context()

    socket = set_up_socket(context)

    while True:
        action, target_string, key = read_request(socket)

        if action == 'encrypt':
            response = cryptocode.encrypt(target_string, key)
        elif action == 'decrypt':
            response = cryptocode.decrypt(target_string, key)
        elif action == 'quit':
            break
        else:
            response = 'error'

        # show what the microservice is doing
        if action == 'encrypt':
            print("Decrypted password is: " + target_string)
            print("Encrypted password is: " + response)
            print()
        elif action == 'decrypt':
            print("Encrypted password is: " + target_string)
            print("Decrypted password is: " + response)
            print()

        # send message back to client
        socket.send_string(response)

    # exit the server program
    context.destroy()
    print("Server closed")


if __name__ == "__main__":
    main()