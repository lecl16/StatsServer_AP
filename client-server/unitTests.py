import pytest
import base64
import os

from client import encrypt_intvalue, decrypt_intvalue

def test_Encrypt():
	cipherkey = os.urandom(16)
	cipherkey_toSend = str(base64.b64encode(cipherkey), 'utf8')
	assert decrypt_intvalue(cipherkey_toSend, encrypt_intvalue(cipherkey_toSend, 123)) == 123
	print("encrypt, decrypt: PASSOU")

print("TESTES UNITARIOS")
test_Encrypt()