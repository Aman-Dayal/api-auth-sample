import os
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
import requests
from datetime import datetime
import time
from dotenv import load_dotenv

# For loading environment variables
load_dotenv()

# Global variables initialization for data caching

global weather_dic
weather_dic = []

global newdic
newdic = {}

# Pydantic model schemas for data validation

class data(BaseModel):
    "schema for extracted data from weather api"
    city: str
    temperature: float
    humidity: int
    weather: str
    latitude: float
    longitude: float
    last_updated: str

class weather_response(BaseModel):
    "schema for response from the weather endpoint"
    source: str
    response: data

class task(BaseModel):
    """schema for background task"""
    to_reverse: str

class task_resp(BaseModel):
    """schema for returning task response"""
    result:str

app = FastAPI()


# Mock User data containing api keys and user information
# Use any of the available api keys to get access
api_keys = {
    "e54d4431-5dab-474e-b71a-0db1fcb9e659": "7oDYjo3d9r58EJKYi5x4E8",
    "5f0c7127-3be9-4488-b801-c7b6415b45e9": "mUP7PpTHmFAkxcQLWKMY8t"
}

users = {
    "7oDYjo3d9r58EJKYi5x4E8": {
        "name": "Aman"
    },
    "mUP7PpTHmFAkxcQLWKMY8t": {
        "name": "Shagun"
    },
}

# Helper functions for authorization

def check_api_key(api_key: str):
    return api_key in api_keys

def get_user_from_api_key(api_key: str):
    return users[api_keys[api_key]]

api_key_header = APIKeyHeader(name="X-API-Key")

def get_user(api_key_header: str = Security(api_key_header)):
    if check_api_key(api_key_header):
        user = get_user_from_api_key(api_key_header)
        return user
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Missing or invalid API key"
    )

# index endpoint to validate user and return user info
@app.get("/")
def user(user: dict = Depends(get_user)):
    return user

def reverse_string(inpu:task,id):
    """reverse string"""
    time.sleep(15)
    newstring = inpu.to_reverse[::-1]
    newdic[id]=newstring
    return newstring


@app.post("/background-task")
async def background_task(inp:task,btsk: BackgroundTasks,user: dict = Depends(get_user)):
    """Queue and run task in background"""
    if newdic == {}:
        num = 1
    else:
        num = max(newdic.keys())+1
    btsk.add_task(reverse_string,inp,num)
    return {"taskid":num,"status":"Processing"}


@app.get("/get-results/",response_model=task_resp)
def get_results(taskid: int,user: dict = Depends(get_user)):
    """"Get task results based on task id"""
    try:
        res = newdic.get(taskid)
        if not res:
            return {"result":"Processing"}
        return {"result": res}
    except:
        return {"result": "Not Found"}

@app.get("/get_weather_details")
def get_weather(city:str,user: dict = Depends(get_user)):
    """"Cache and return weather data by using openmap weather api"""
    api_key = os.environ['API_KEY']
    city = city.lower()

    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}"
    print(weather_dic)
    respo = {}
    try:
        for weather_ in weather_dic:
            if city == weather_['response']['city']:
                respo = {"source":"Cached",'response' : weather_}
    except Exception as e:
        print(e)
    try:
        if respo =={}:
            weather = requests.get(url=url)
            response = weather.json()
            last_updated = datetime.now().strftime('%d %m %Y %H:%M:%S')
            rsp_dic={
            "city":city,
            "temperature":float(response['main']['temp']),
            "humidity":int(response['main']["humidity"]),
            "weather":str(response['weather'][0]['description']),
            "latitude":float(response['coord']['lat']),
            "longitude":float(response['coord']['lon']),
            "last_updated": str(last_updated)
            }

            respo = {"source":"API","response" : rsp_dic}
            weather_dic.append({"response":rsp_dic})
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500,detail="Internal Server Error")
    return respo


