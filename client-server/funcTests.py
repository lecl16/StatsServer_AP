import pytest

from subprocess import Popen
from subprocess import PIPE


def numerArgs():
    proc = Popen("python3 client.py", stdout=PIPE, shell=True)
    assert proc.wait() == 1
    assert proc.stdout.read().decode('utf-8') == "Argumentos: client_id, Porto, DNS\n"

    proc = Popen("python3 client.py client_id", stdout=PIPE, shell=True)
    assert proc.wait() == 1
    assert proc.stdout.read().decode('utf-8') == "Argumentos: client_id, Porto, DNS\n"

    proc = Popen("python3 client.py client_id 127.0.0.1 123 Nothing",
                 stdout=PIPE, shell=True)
    assert proc.wait() == 1
    assert proc.stdout.read().decode('utf-8') == "Argumentos: client_id, Porto, DNS\n"

    print("Testes funcionais(número de argumentos) efetuados com sucesso no client")

    proc = Popen("python3 server.py ", stdout=PIPE, shell=True)
    assert proc.wait() == 1
    assert proc.stdout.read().decode('utf-8') == "Argumentos: Porto\n"

    proc = Popen("python3 server.py 123 456", stdout=PIPE, shell=True)
    assert proc.wait() == 1
    assert proc.stdout.read().decode('utf-8') == "Argumentos: Porto\n"

    print("Testes funcionais(número de argumentos) efetuados com sucesso no server")


def invalidArgs():
    proc = Popen("python3 client.py testing test tested",
                 stdout=PIPE, shell=True)
    assert proc.wait() == 2
    assert proc.stdout.read().decode('utf-8') == "Porto deve ser um número inteiro\n"

    proc = Popen("python3 client.py testing -88 127.0.0.1",
                 stdout=PIPE, shell=True)
    assert proc.wait() == 2
    assert proc.stdout.read().decode(
        'utf-8') == "Porto deve ser um número inteiro positivo\n"

    proc = Popen("python3 client.py testing 8,8 127.0.0.1",
                 stdout=PIPE, shell=True)
    assert proc.wait() == 2
    assert proc.stdout.read().decode('utf-8') == "Porto deve ser um número inteiro\n"

    proc = Popen("python3 client.py testing 123 big", stdout=PIPE, shell=True)
    assert proc.wait() == 2
    assert proc.stdout.read().decode('utf-8') == "Máquina no fromato X.X.X.X\n"

    proc = Popen("python3 client.py testing 123 288.0.0.1",
                 stdout=PIPE, shell=True)
    assert proc.wait() == 2
    assert proc.stdout.read().decode(
        'utf-8') == "Máquina no fromato X.X.X.X e 0 < X < 255\n"
    
    print("Testes funcionais(tipo de argumentos) efetuados com sucesso no client")
    print("Testes funcionais(tipo de argumentos) efetuados com sucesso no server")

print("----FUNCTIONAL TESTS----")
numerArgs()
invalidArgs()
