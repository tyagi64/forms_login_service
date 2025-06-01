import hashlib
from os import close,path
from cryptography.fernet import Fernet

class Cryptor:
    def __init__(self,keyFile:str):
        self.keyFile = keyFile
        if path.isfile(self.keyFile):
            self.fernet = Fernet(open(self.keyFile,"rb").read())
        else:
            key = Fernet.generate_key()
            file = open(keyFile,"wb")
            file.write(key)
            file.close()
            self.fernet = Fernet(key)

    def encrypt(self,string:str)->bytes:
        return self.fernet.encrypt(string.encode())
    def decrypt(self,string:bytes)->str:
        return self.fernet.decrypt(string).decode()


def encrypt(password:str)->str:
    return hashlib.md5(password.encode()).hexdigest()
