import pytest

from subprocess import Popen
from subprocess import PIPE


def numerArgs():
    proc = Popen("python3 client.py", stdout=PIPE, shell=True)
    assert proc.wait() == 1
    assert proc.stdout.read().decode(
        'utf-8') == "\nFORMATO INVÁLIDO\nDeverá ser do tipo '$python3 client.py client_id porto'\n"

    proc = Popen("python3 client.py client_id", stdout=PIPE, shell=True)
    assert proc.wait() == 1
    assert proc.stdout.read().decode('utf-8') == "\nFORMATO INVÁLIDO\nDeverá ser do tipo '$python3 client.py client_id porto'\n"
    
    proc = Popen("python3 client.py client_id 127.0.0.1 123 Nothing",
                 stdout=PIPE, shell=True)
    assert proc.wait() == 1
    assert proc.stdout.read().decode('utf-8') == "\nFORMATO INVÁLIDO\nDeverá ser do tipo '$python3 client.py client_id porto'\n"

    print("Testes funcionais(número de argumentos) efetuados com SUCESSO no client")

    proc = Popen("python3 server.py ", stdout=PIPE, shell=True)
    assert proc.wait() == 1
    assert proc.stdout.read().decode('utf-8') == "Usage: server.py Porto\n"

    proc = Popen("python3 server.py 123 456", stdout=PIPE, shell=True)
    assert proc.wait() == 1
    assert proc.stdout.read().decode('utf-8') == "Usage: server.py Porto\n"

    print("Testes funcionais(número de argumentos) efetuados com SUCESSO no server")


def invalidArgs():
    proc = Popen("python3 client.py testing test tested",
                 stdout=PIPE, shell=True)
    assert proc.wait() == 2
    assert proc.stdout.read().decode('utf-8') == "\nVALOR DO PORTO DEVE SER INTEIRO\n"

    proc = Popen("python3 client.py testing -88 127.0.0.1",
                 stdout=PIPE, shell=True)
    assert proc.wait() == 2
    assert proc.stdout.read().decode(
        'utf-8') == "\nVALOR DO PORTO DEVE SER POSITIVO\n"

    proc = Popen("python3 client.py testing 8,8 127.0.0.1",
                 stdout=PIPE, shell=True)
    assert proc.wait() == 2
    assert proc.stdout.read().decode('utf-8') == "\nVALOR DO PORTO DEVE SER INTEIRO\n"

    proc = Popen("python3 client.py testing 123 big", stdout=PIPE, shell=True)
    assert proc.wait() == 2
    assert proc.stdout.read().decode('utf-8') == "\nFORMATO INVÁLIDO\nO formato correto para a máquina terá de ser 'X.X.X.X'\n\n"

    proc = Popen("python3 client.py testing 123 288.0.0.1",
                 stdout=PIPE, shell=True)
    assert proc.wait() == 2
    assert proc.stdout.read().decode(
        'utf-8') == "\nVALOR INVÁLIDO\nValor dos dígitos terá de pertencer ao intervalo [0,255]\n\n"

    print("Testes funcionais(tipo de argumentos) efetuados com SUCESSO no client")

    proc = Popen("python3 server.py -88", stdout=PIPE, shell=True)
    assert proc.wait() == 2
    assert proc.stdout.read().decode(
        'utf-8') == "Porto deve ser um número inteiro positivo\n"

    proc = Popen("python3 server.py mentol", stdout=PIPE, shell=True)
    assert proc.wait() == 2
    assert proc.stdout.read().decode('utf-8') == "Porto deve ser um número inteiro\n"

    print("Testes funcionais(tipo de argumentos) efetuados com SUCESSO no server")


print("TESTES FUNCIONAIS")
numerArgs()
invalidArgs()
