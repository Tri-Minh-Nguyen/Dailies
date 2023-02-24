# Import the Canvas class
from canvasapi import Canvas
from dateutil import parser
from datetime import datetime, timedelta
from twilio.rest import Client
import requests
import pytz

def get_key():
    keys = []
    with open("authkey.txt", "r") as f:
        for line in f:
            keys.append(line.strip())
    return keys[0], keys[1], keys[2], keys[3], keys[4], keys[5]

def retrieve_weather(w_key):
    WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather?"
    WEATHER_KEY = w_key
    CITY = "Minneapolis"
    url = WEATHER_URL + "appid=" + WEATHER_KEY + "&q=" + CITY 

    weather = requests.get(url).json()
    temp = {}
    temp['temp'] = int(weather['main']['temp'] * 9/5 - 459.67)
    temp['description'] = weather['weather'][0]['description']
    return temp

def retrieve_canvas(c_key):
    CANVAS_URL = "https://canvas.umn.edu/"
    CANVAS_KEY = c_key

    canvas = Canvas(CANVAS_URL, CANVAS_KEY)
    today = datetime.now().strftime("%Y-%m-%d")
    timezone = pytz.timezone("US/Central") 
    upcoming = []
    urgent = []

    for event in canvas.get_upcoming_events():
        temp = {}
        temp['title'] = event['title']
        temp['due'] = parser.parse(event['end_at']).strftime("%Y-%m-%d")
        temp['time'] = parser.parse(event['end_at']).astimezone(tz=timezone).strftime("%I:%M %p")
        temp['link'] = event['html_url']
        if temp['due'] == today or due_today(temp['due'],temp['time']):
            urgent.append(temp)
        else:
            upcoming.append(temp)
    return urgent, upcoming

def to_string(urgent, upcoming, weather):
    message = "Good morning! Here are your Daillies: \n\n"
    message += "Weather: \n"
    message += "Temperature: " + str(weather['temp']) + " degrees F \n"
    message += weather['description'] + "\n\n"
    message += "Urgent: \n"
    for event in urgent:
        message += event['title'] + "\n"
        message += event['due'] + " " + event['time'] + "\n"
        message += event['link'] + "\n\n"
    message += "Upcoming: \n"
    for event in upcoming:
        message += event['title'] + "\n"
        message += event['due'] + " " + event['time'] + "\n"
        message += event['link'] + "\n\n"
    return message


def send_text(message, a_sid, a_token, m_sid, number):
    account_sid = a_sid 
    auth_token = a_token
    client = Client(account_sid, auth_token) 
 
    message = client.messages.create(  
                                messaging_service_sid=m_sid,
                                body=message,
                                to=number
                            ) 
    print(message.sid)

def due_today(date,time):
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    if date == tomorrow and time == "11:59 PM":
        return True
    return False

if __name__ == "__main__":
    w_key, c_key, account_sid, auth_token, m_sid, number = get_key()
    weather = retrieve_weather(w_key)
    urgent, upcoming = retrieve_canvas(c_key)
    message = to_string(urgent, upcoming, weather)
    send_text(message, account_sid, auth_token, m_sid, number)