#!/usr/bin/python3

from email import header
import sys
import socket
import select
import json
import base64
import csv
import random
from os import path
from common_comm import send_dict, recv_dict, sendrecv_dict

from Crypto.Cipher import AES

# Dicionário com a informação relativa aos clientes
users = {'client_id': [], 'data_lenght': [],
         'min_value': [], 'max_value': [], 'cipher': [], 'sock_id': [], 'number_list': []}

# CSV file header
header = ["client_id", "data_length", "min_value", "max_value"]


# return the client_id of a socket or None

def find_client_id(client_sock):
    peerName = client_sock.getpeername()
    return peerName[1]

# Função para encriptar valores a enviar em formato json com codificação base64
# return int data encrypted in a 16 bytes binary string and coded base64


def encrypt_intvalue(client_id, data):
    for i in range(0, len(users["client_id"])):
        if users["sock_id"][i] == client_id:
            cipherkey = users["cipher"][i]

    cipher = AES.new(cipherkey, AES.MODE_ECB)
    data2 = cipher.encrypt(bytes("%16d" % (data), 'utf8'))
    data_tosend = str(base64.b64encode(data2), 'utf8')
    return data_tosend


# Função para desencriptar valores recebidos em formato json com codificação base64
# return int data decrypted from a 16 bytes binary string and coded base64
def decrypt_intvalue(client_id, data):
    for i in range(0, len(users["client_id"])):
        if users["sock_id"][i] == client_id:
            cipherkey = users["cipher"][i]

    cipher = AES.new(cipherkey, AES.MODE_ECB)
    data = base64.b64decode(data)
    data = cipher.decrypt(data)
    data = int(str(data, 'utf8'))
    return data


# Incomming message structure:
# { op = "START", client_id, [cipher] }
# { op = "QUIT" }
# { op = "NUMBER", number }
# { op = "STOP" }
#
# Outcomming message structure:
# { op = "START", status }
# { op = "QUIT" , status }
# { op = "NUMBER", status }
# { op = "STOP", status, min, max }


#
# Suporte de descodificação da operação pretendida pelo cliente
#
def new_msg(client_sock):
    request = recv_dict(client_sock)
    # print(request)
    if request['op'] == "START":
        new_client(client_sock, request)
    if request['op'] == "QUIT":
        quit_client(client_sock, request)
    if request['op'] == "STOP":
        stop_client(client_sock, request)
    if request['op'] == "NUMBER":
        number_client(client_sock, request)
    return None
# read the client request
# detect the operation requested by the client
# execute the operation and obtain the response (consider also operations not available)
# send the response to the client


#
# Suporte da criação de um novo jogador - operação START
#
def new_client(client_sock, request):
    numbers_list = []
    nome = request['client_id']
    sock_id = find_client_id(client_sock)
    if nome in users["client_id"]:
        answer = {'op': "START", "status": False, "error": "Cliente existente"}
        send_dict(client_sock, answer)
        return False

    else:
        users["client_id"].append(nome)
        users["sock_id"].append(sock_id)
        users["data_lenght"].append(0)
        users["number_list"] += numbers_list
        users["cipher"].append(base64.b64decode(request["cipher"]))
        print(users)
        answer = {"op": "START", "status": True}
        send_dict(client_sock, answer)

        return True


#
# Suporte da eliminação de um cliente
#

def clean_client(client_sock):
    client_id = find_client_id(client_sock)
    print("Nº de Clientes: "+str(len(users["client_id"])))
    for i in range(0, len(users["client_id"])):
        print("Index: "+str(i))
        if users["client_id"][i] == client_id:
            users["client_id"].pop(i)
            users["cipher"].pop(i)
            users["data_lenght"].pop(i)
            users["max_value"].pop(i)
            users["min_value"].pop(i)
            users["sock_id"].pop(i)
            users["number_list"].pop(i)
            return True
    return False
# obtain the client_id from his socket and delete from the dictionary

#
# Suporte do pedido de desistência de um cliente - operação QUIT
#


def quit_client(client_sock, request):
    if find_client_id(client_sock) in users["sock_id"]:
        answer = {"op": "QUIT", "status": True}
        send_dict(client_sock, answer)
        update_file(find_client_id(client_sock))
        clean_client(client_sock)
    else:
        answer = {"op": "QUIT", "status": False,
                  "error": "Cliente inexistente"}
        send_dict(client_sock, answer)
    print("Users" + str(users))

    return None
# obtain the client_id from his socket
# verify the appropriate conditions for executing this operation
# process the report file with the QUIT result
# eliminate client from dictionary
# return response message with or without error message


#
# Suporte da criação de um ficheiro csv com o respectivo cabeçalho
#
def create_file():
    if path.exists("report.csv") == False:
        with open("report.csv", "w") as csvFile:
            w = csv.DictWriter(csvFile, fieldnames=header)
            w.writeheader()
    return None
# create report csv file with header


#
# Suporte da actualização de um ficheiro csv com a informação do cliente e resultado
#

# PRECISA DE SER VERIFICADA!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

def update_file(client_id):  # Falta um parâmetro de entrada
    with open('report.csv', 'a') as csv_file:
        write = csv.DictWriter(csv_file, fieldnames=header)
        for i in range(0, len(users["client_id"])):
            if client_id == users["sock_id"][i]:
                line = {"client_id": users["client_id"][i], "data_lenght": users["data_lenght"]
                        [i], "min_value": min(users["min_value"][i]), "max_value": max(users["max_value"][i])}
        write.writerow(line)
    return None
# update report csv file with the result from the client

#
# Suporte do processamento do número de um cliente - operação NUMBER
#

# PRECISA DE SER VERIFICADA!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


def number_client(client_sock, request):
    if find_client_id(client_sock) in users["sock_id"]:
        inserted_number = decrypt_intvalue(
            find_client_id(client_sock), request['number'])
        answer = {"op": "NUMBER", "status": True}
        send_dict(client_sock, answer)

        for i in range(0, len(users["client_id"])):
            if find_client_id(client_sock) == users["client_id"][i]:
                users.setdefault["number_list", i].append(inserted_number)
                users["data_lenght"][i] = users["data_lenght"][i]+1

    else:
        answer = {"op": "NUMBER", "status": False,
                  "error": "Cliente inexistente"}
        send_dict(client_sock, answer)
    return None
# obtain the client_id from his socket
# verify the appropriate conditions for executing this operation
# return response message with or without error message


#
# Suporte do pedido de terminação de um cliente - operação STOP
#
def stop_client(client_sock, request):
    if find_client_id(client_sock) in users["client_id"]:
        for i in range(0, len(users["client_id"])):
            if find_client_id(client_sock) == users["client_id"][i]:
                answer = {"op": "STOP", "status": True,
                          "min_value": users["min_value"][i], "max_value": users["max_value"][i], "client_id": users["client_id"][i]}
                send_dict(client_sock, answer)
                update_file(client_sock)
        clean_client(client_sock)
    else:
        answer = {"op": "STOP", "status": False,
                  "error": "Cliente inexistente"}
        send_dict(client_sock, answer)
    print("Users: "+str(users))
    return None
# obtain the client_id from his socket
# verify the appropriate conditions for executing this operation
# process the report file with the result
# eliminate client from dictionary
# return response message with result or error message


def main():
    # validate the number of arguments and eventually print error message and exit with error
    # verify type of of arguments and eventually print error message and exit with error
    if len(sys.argv) != 2:
        print("Usage: "+sys.argv[0]+" Porto")
        sys.exit(1)

    try:
        int(sys.argv[1])
    except ValueError:
        print(sys.argv[1]+" não é número inteiro")
        sys.exit(2)
    if int(sys.argv[1]) < 0:
        print(sys.argv[1]+" não é positivo")
        sys.exit(2)

    port = int(sys.argv[1])

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("127.0.0.1", port))
    server_socket.listen(10)

    clients = []
    create_file()

    while True:
        try:
            available = select.select([server_socket] + clients, [], [])[0]
        except ValueError:
            # Sockets may have been closed, check for that
            for client_sock in clients:
                if client_sock.fileno() == -1:
                    client_sock.remove()  # closed
            continue  # Reiterate select

        for client_sock in available:
            # New client?
            if client_sock is server_socket:
                newclient, addr = server_socket.accept()
                clients.append(newclient)
            # Or an existing client
            else:
                # See if client sent a message
                if len(client_sock.recv(1, socket.MSG_PEEK)) != 0:
                    # client socket has a message
                    # print ("server" + str (client_sock))
                    new_msg(client_sock)
                else:  # Or just disconnected
                    clients.remove(client_sock)
                    clean_client(client_sock)
                    client_sock.close()
                    break  # Reiterate select


if __name__ == "__main__":
    main()
