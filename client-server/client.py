#!/usr/bin/python3

import os
import sys
import socket
import json
import base64
from telnetlib import SEND_URL
from urllib import response

from numpy import true_divide
from requests import request
from common_comm import send_dict, recv_dict, sendrecv_dict

from Crypto.Cipher import AES

# Função para encriptar valores a enviar em formato json com codificação base64
# return int data encrypted in a 16 bytes binary string coded in base64


def encrypt_intvalue(cipherkey, data):
    cipher = AES.new(cipherkey, AES.MODE_ECB)
    encripted = cipher.encrypt(bytes("%16" % (data), 'utf-8'))
    data_tosend = str(base64.b64encode(encripted), "utf-8")
    return data_tosend


# Função para desencriptar valores recebidos em formato json com codificação base64
# return int data decrypted from a 16 bytes binary strings coded in base64
def decrypt_intvalue(cipherkey, data):
    cipher = AES.new(cipherkey, AES.MODE_ECB)
    data = base64.b64decode(data)
    data = cipher.decrypt(data)
    data = int(str(data, "utf-8"))
    return data


# verify if response from server is valid or is an error message and act accordingly
def validate_response(client_sock, response):
    try:
        op = response['op']
        status = response['status']
        return True

    except:
        print(" ! Não foi possível validar a resposta ! ")
        return False


# process QUIT operation
def quit_action(client_sock):
    quit_request = {'op': "QUIT"}
    response = sendrecv_dict(client_sock, quit_request)

    if validate_response(client_sock, response):
        if response['status']:
            print(" ! Desistência Aprovada ! ")
        else:
            print(" ! Desistência Recusada ! ")
    else:
        print(" ! Não foi possível validar a resposta ! ")

    # return None


# Outcomming message structure:
# { op = "START", client_id, [cipher] }
# { op = "QUIT" }
# { op = "NUMBER", number }
# { op = "STOP" }
#
# Incomming message structure:
# { op = "START", status }
# { op = "QUIT" , status }
# { op = "NUMBER", status }
# { op = "STOP", status, min, max }


#
# Suporte da execução do cliente
#

cipherkey = os.urandom(16)
cipherkey_tosend = str(base64.b64encode(cipherkey), "utf8")


def run_client(client_sock, client_id):

    running = True

    while running:

        userCommand = input("Operação : ")
        command = userCommand.upper()

        if command == "START":

            userEncryptInfo = input("Pretende Encriptar os Dados ? (Y/N)")
            uEI = userEncryptInfo.upper()

            while (uEI != "Y" or uEI != "N"):
                userEncryptInfo = input("Pretende Encriptar os Dados ? (Y/N)")
                uEI = userEncryptInfo.upper()

            if uEI == "Y":
                request = {"op": "START", "client_id": client_id,
                           "cipher": cipherkey_tosend}
                response = sendrecv_dict(client_sock, request)

                if validate_response(client_sock, response):
                    if response['status'] == False:
                        print("Erro: " + response['error'])
                else:
                    print(" ! Não foi possível validar a resposta ! ")

            elif uEI == "N":
                request = {"op": "START",
                           "client_id": client_id, "cipher": None}
                response = sendrecv_dict(client_sock, request)

                if validate_response(client_sock, response):
                    if response['status'] == False:
                        print("Erro: " + response['error'])
                else:
                    print(" ! Não foi possível validar a resposta ! ")

        if command == "QUIT":
            quit_action(client_sock)

        if command == "NUMBER":

            # (uEI == "Y") indica o caso em que o cliente pretende encriptar os
            # dados enviados ao servidor e (uEI == "N") representa o caso em que
            #  o cliente não pretende encriptar os dados enviados.

            number = input("Valor a Adicionar (Numérico Inteiro): ")

            while (number < 0 and type(number) != int):
                print(" ! Valor Introduzido Inválido ! ")
                number = input("Valor a Adicionar : ")

            if (uEI == "Y"):
                request = {'op': "NUMBER",
                           "number": encrypt_intvalue(cipherkey, number)}
            else:
                request = {'op': "NUMBER", "number": number}

            response = sendrecv_dict(client_sock, request)

            if validate_response(client_sock, response):
                if response['status'] == False:
                    print("Erro: " + response['error'])
            else:
                print(" ! Não foi possível validar a resposta ! ")

        if command == "STOP":
            request = {'op': "STOP"}
            response = sendrecv_dict(client_sock, request)

            if validate_response(client_sock, response):
                running = False
                continue

            else:
                print(" ! Não foi possível validar a resposta ! ")

    return None


def main():
    # validate the number of arguments and eventually print error message and exit with error
    # verify type of arguments and eventually print error message and exit with error

    cipher = AES.new(cipherkey, AES.MODE_ECB)

    port = ?
    hostname = ?

    client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_sock.connect((hostname, port))

    run_client(client_sock, sys.argv[1])

    client_sock.close()
    sys.exit(0)


if __name__ == "__main__":
    main()
