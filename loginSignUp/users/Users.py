from datetime import datetime as dtime,timedelta as td
from cryptography.fernet import Fernet
from utils.crypt import encrypt,Cryptor
from typing import List,Tuple
import psycopg2
class User:
    def __init__(self,email,password,flg=False):
        self.email:str = email
        if not flg:
            self.password:str = encrypt(password)
        else:
            self.password:str = password
    def __str__(self):
        return f"USER : {self.email},{self.password}"
    def check_password(self,password:str)->bool:
        return self.password == password
    def get_token(self)->str:
        return self.email+":"+ dtime.now().strftime("%Y-%m-%d %H-%M-%S")

class Users:
    def __init__(self):
        try:
            self.conn=psycopg2.connect(
                host="localhost",
                database="forms",
                user="postgres",
                password="megh1612",
                port="5443"
            )
            self.cur = self.conn.cursor()
        except psycopg2.Error as e:
            print(f"Error connecting to database:{e}")
        self.userList:List[User] = []

    def addUser(self,user:User)->None:
        self.userList.append(user)
        try:
            sql :str = "insert into users(email,pass) values(%s,%s);"
            self.cur.execute(sql,(user.email,user.password))
            self.conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
    def init_key(self)->None:
        self.Crypt:Cryptor = Cryptor(".user")
    def put_key(self,key:str):
        f = open(".user","wb")
        f.write(key.encode())
        f.close()
        self.Crypt:Cryptor = Cryptor(".user")
    def get_key(self)->str:
        f = open(".user","rb")
        out = f.read()
        f.close()
        return out.decode()
    def get_user(self,email:str) -> User|None:
        output:User|None = None
        try:
            sql:str="select email,pass from users where email=%s;"
            self.cur.execute(sql,(email,))
            rows = self.cur.fetchone()
            if rows:
                output = User(rows[0],rows[1],True)
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            return output

    def findUserWithEmail(self,email:str)->bool:
        output:bool = False
        try:
            sql:str="select email from users where email=%s;"
            self.cur.execute(sql,(email,))
            rows = self.cur.fetchone()
            if rows:
                output = True
            else:
                output = False
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            return output

    def VeriFy(self,email:str,password:str)-> str|None:
            user:User|None = self.get_user(email)
            if user == None:
                return None
            else:
                pass_to_check:str = encrypt(password)
                if user.check_password(password=pass_to_check):
                    token:str = self.Crypt.encrypt(user.get_token()).decode()
                    return token
                else:
                    return None

    def check_session(self,token:str)->Tuple[bool,User|None]:
        output:Tuple[bool,User|None] =  False,None
        try:
            result:str = self.Crypt.decrypt(token.encode())
            email,issue_time= result.split(":")
            if self.findUserWithEmail(email):
                current_time = dtime.now()
                issue_time = dtime.strptime(issue_time,"%Y-%m-%d %H-%M-%S")
                if abs(current_time-issue_time) < td(minutes=15):
                    output = True,self.get_user(email)
                else:
                    output:Tuple[bool,None|User] = False,None
        except:
            output:Tuple[bool,None|User] = False,None
        return output
