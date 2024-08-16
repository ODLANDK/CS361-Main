# Name: Kyle Odland
# Course: CS361
# A microservice to encrypt or decrypt a string with a given key

import cryptocode
import zmq


def set_up_socket(context):

    # set up a reply socket for the server
    socket = context.socket(zmq.REP)

    port = 5225
    # bind the socket to a port number
    socket.bind("tcp://*:" + str(port))
    print("Server ready to receive at port " + str(port) + "...")
    return socket


def read_request(socket):
    message = socket.recv_json()

    return message['task'], message['target'], message['key']


def main():
    # set up context for ZMQ
    context = zmq.Context()

    socket = set_up_socket(context)

    while True:
        task, target_string, key = read_request(socket)

        if task == 'encrypt':
            response = cryptocode.encrypt(target_string, key)
        elif task == 'decrypt':
            response = cryptocode.decrypt(target_string, key)
        elif task == 'quit':
            break
        else:
            response = 'error'

        # show what the microservice is doing
        if task == 'encrypt':
            print("Decrypted password is: " + target_string)
            print("Encrypted password is: " + response)
        elif task == 'decrypt':
            print("Encrypted password is: " + target_string)
            print("Decrypted password is: " + response)

        # send message back to client
        socket.send_string(response)

    # exit the server program
    context.destroy()


if __name__ == "__main__":
    main()