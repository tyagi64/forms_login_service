import sys
import requests
from flask import Flask
from flask.globals import request
from flask.wrappers import json
from flask_cors import CORS, cross_origin
from typing import Tuple,Dict


from users.Users import User,Users
from utils.envreader import Read_env
from utils.dict import convert_to_dict

app = Flask(__name__)
cors = CORS(app) # allow CORS for all domains on all routes.
app.config['CORS_HEADERS'] = 'Content-Type'
env:Dict[str,str]
users:Users

@app.route('/signup',methods=['POST'])
@cross_origin()
def signup()->Tuple[str,int]:
    output:Tuple[str,int] = "Something Went Wrong",503
    try:
        data = request.get_json()
        email:str = str(data.get('email'))
        password:str = str(data.get('password'))
        if email == None or password == None:
            raise Exception("Something went wrong")
        else:
            if not users.findUserWithEmail(email):
                users.addUser(user=User(email=email,password=password))
                output:Tuple[str,int] = "User Added Successfully",200
            else:
                output:Tuple[str,int] = "User Already Exists",400
    except:
        output:Tuple[str,int] = "Bad Request",400

    return output

@app.route('/login',methods=['POST'])
@cross_origin()
def login()->Tuple[str,int]:
    output:Tuple[str,int] = "Something Went Wrong",503
    try:
        data = request.get_json()
        email:str = data.get('email')
        password:str = data.get('password')
        if email == None or password == None:
            raise Exception("Something went wrong")
        else:
            if users.findUserWithEmail(email):
                token = users.VeriFy(email=email,password=password)
                if None == token:
                    output:Tuple[str,int] = "Authentication Failed",400
                else:
                    output:Tuple[str,int] = f"{token}",200
            else:
                output:Tuple[str,int] = "User Doesn't Exist",400
    except Exception as e:
        print(e)
        output:Tuple[str,int] = "Bad Request 434",400

    print(output)
    return output

@app.route('/check_session',methods=['POST'])
@cross_origin()
def check_session()->Tuple[str,int]:
    output:Tuple[str,int] = "Something Went Wrong",503
    try:
        data = request.get_json()
        token:str = data.get('token')
        result:Tuple[bool,User|None] = users.check_session(token)
        if result[0] == False:
            output = "Token Expired",400
        else:
            output = "Auth Success",200
    except:
        output:Tuple[str,int] = "Bad Request",400
    return output
@app.route('/get_key',methods=['GET'])
@cross_origin()
def get_key():
    output:Tuple[str,int] = users.get_key(),200
    return output

if __name__ == '__main__':
    if len(sys.argv) == 2:
        fail:bool = False
        env = Read_env(sys.argv[1])
        users = Users()
        if env.get('SERVER_HOSTNAME') != None and env.get('SERVER_PORT') != None:
            response = requests.post(f"http://{env.get('SERVER_HOSTNAME')}:{env.get('SERVER_PORT')}/register",json={'IP':env.get('HOSTNAME'),'PORT':int(env.get('PORT') or '8000'),'SERVICE_NAME':env.get('SERVICE_NAME')},headers={"Content-Type":"application/json"})
            if response.status_code == 200:
                response_content = response.text
                print(f"content : {response_content}")
                response_content = response_content.split(',')
                leader = convert_to_dict(response_content)
                key_response = requests.get(f"http://{leader['IP']}:{leader['PORT']}/get_key")
                if key_response.status_code == 200:
                    key = key_response.text
                    users.put_key(key)
            elif response.status_code == 204:
                users.init_key()
            else:
                fail = True
                print("Something went wrong")
            if fail:
                print("Something Went Wrong")
            else:
                app.run(env.get('HOSTNAME'),int(env.get('PORT') or '8000'))



    else:
        print("Too few Arguments")
