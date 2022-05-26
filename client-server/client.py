#!/usr/bin/python3

import os
import sys
import socket
import json
import base64
from common_comm import send_dict, recv_dict, sendrecv_dict

from Crypto.Cipher import AES

# Função para encriptar valores a enviar em formato json com codificação base64
# return int data encrypted in a 16 bytes binary string coded in base64


def encrypt_intvalue(cipherkey, data):
    cipher = AES.new(cipherkey, AES.MODE_ECB)
    encripted = cipher.encrypt(bytes("%16d" % (data), 'utf-8'))
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
        print("\nIMPOSSÍVEL VALIDAR RESPOSTA\n")
        return False


# process QUIT operation
def quit_action(client_sock):
    quit_request = {'op': "QUIT"}
    response = sendrecv_dict(client_sock, quit_request)

    if validate_response(client_sock, response):
        if response['status']:
            print("\nDESISTÊNCIA APROVADA\n")
        else:
            print("\nDESISTÊNCIA NEGADA\n")

    # else:
    #     print(" ! Não foi possível validar a resposta ! ")

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
cipher = AES.new(cipherkey, AES.MODE_ECB)


def run_client(client_sock, client_id):

    running = True

    userDataEncrypt = False

    while running:

        userCommand = input("Operação : ")
        command = userCommand.upper()

        if command == "START":

            userEncryptInfo = input("Encriptar Dados (Y/N) : ")
            uEI = userEncryptInfo.upper()

            if uEI == "Y":
                userDataEncrypt = True
                request = {"op": "START", "client_id": client_id,
                           "cipher": cipherkey_tosend}
                response = sendrecv_dict(client_sock, request)

                if validate_response(client_sock, response):
                    if response['status'] == False:
                        print("Erro: " + response['error'])

            elif uEI == "N":
                request = {"op": "START",
                           "client_id": client_id, "cipher": None}
                response = sendrecv_dict(client_sock, request)

                if validate_response(client_sock, response):
                    if response['status'] == False:
                        print("Erro: " + response['error'])

            else:
                print("\nRESPOSTA INVÁLIDA\n")
                sys.exit(1)

        if command == "QUIT":
            quit_action(client_sock)

        if command == "NUMBER":

            # (uEI == "Y") indica o caso em que o cliente pretende encriptar os
            # dados enviados ao servidor e (uEI == "N") representa o caso em que
            #  o cliente não pretende encriptar os dados enviados.

            validNum = False
            intNum = False
            num = ""

            while intNum != True or validNum != True:
                validNum = False
                intNum = False

                number = input("Valor (numérico inteiro): ")

                try:
                    num = int(number)
                    intNum = True
                except:
                    print("\nTIPO DE VALOR INÁLIDO\n")
                    continue

                num = int(number)

                if num >= 0:
                    validNum = True
                else:
                    print("\nVALOR INVÁLIDO\n")
                    continue

            if (userDataEncrypt):
                request = {'op': "NUMBER",
                           "number": encrypt_intvalue(cipherkey, num)}
            else:
                request = {'op': "NUMBER", "number": num}

            response = sendrecv_dict(client_sock, request)

            if validate_response(client_sock, response):
                if response['status'] == False:
                    print("Erro: " + response['error'])

        if command == "STOP":
            request = {'op': "STOP"}
            response = sendrecv_dict(client_sock)

            if validate_response(client_sock, response):
                running = False
                continue


# Verificação dos argumentos passados na linha de comandos.
# Variável defaultMachine é True se o utilizador apenas passar
# 2 argumentos e a máquina utilizada será a local '127.0.0.1';
# caso contrário, a variável assumirá o valor False e o máquina
# a utilizar será a indicada pelo utilizador.


def main():
    # validate the number of arguments and eventually print error message and exit with error
    # verify type of arguments and eventually print error message and exit with error

    defaultMachine = True

    if len(sys.argv) != 3:
        if len(sys.argv) == 4:
            defaultMachine = False
        else:
            print(
                "\nFORMATO INVÁLIDO\nDeverá ser do tipo '$python3 client.py client_id porto'\n")
            sys.exit(2)

    try:
        int(sys.argv[2])
    except ValueError:
        print("\nVALOR DO PORTO DEVE SER INTEIRO\n")
        sys.exit(1)

    if int(sys.argv[2]) < 0:
        print("\nVALOR DO PORTO DEVE SER POSITIVO\n")
        sys.exit(1)

    if defaultMachine:
        providedHostname = '127.0.0.1'.split('.')
    else:
        providedHostname = sys.argv[3].split('.')

    # Verificação do número de argumentos da máquina fornecida

    if len(providedHostname) != 4:
        print(
            "\nFORMATO INVÁLIDO\nO formato correto para a máquina terá de ser 'X.X.X.X'\n")
        sys.exit(1)

    # Verificação individual dos dígitos da máquina, sendo que
    # cada um terá de estar no intervalo [0,255].

    for d in providedHostname:
        try:
            int(d)
        except ValueError:
            print(
                "\nVALOR INVÁLIDO\nValor dos dígitos terá de pertencer ao intervalo [0,255]\n")
            sys.exit(1)

        if int(d) > 255 or int(d) < 0:
            print(
                "\nVALOR INVÁLIDO\nValor dos dígitos terá de pertencer ao intervalo [0,255]\n")
            sys.exit(1)

    port = int(sys.argv[2])

    if defaultMachine:
        hostname = '127.0.0.1'
    else:
        hostname = sys.argv[3]

    client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_sock.connect((hostname, port))

    run_client(client_sock, sys.argv[1])

    client_sock.close()
    sys.exit(0)


if __name__ == "__main__":
    main()
