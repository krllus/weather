#!/usr/bin/env python3

import configparser
import json
import os.path
import requests
import pathlib
from datetime import datetime

PROVIDERS_URL_TEMPLATES = {
    "openweathermap": lambda location, api_key: f"http://api.openweathermap.org/data/2.5/forecast?q={location}&APPID={api_key}",
    "darkskynet": lambda location, api_key: f"https://api.darksky.net/forecast/{api_key}/{location}?units=si&lang=pt&exclude=minutely,hourly,alerts,flags"
}

def get_config_dir():
    user_home = os.path.expanduser('~')
    config_dir = os.path.join(user_home, ".config")
    pathlib.Path(config_dir).mkdir(parents=True, exist_ok=True)
    return config_dir

def get_cache_dir():
    user_home = os.path.expanduser('~')
    cache_dir = os.path.join(user_home, ".cache/weather")
    pathlib.Path(cache_dir).mkdir(parents=True, exist_ok=True)
    return cache_dir

def get_config():
    config_path = os.path.join(get_config_dir(), "weather.ini")
    config = configparser.ConfigParser()
    config.read(config_path)
    return config

def get_api_key(provider):
    config = get_config()
    return config[provider]['api']


def get_api_location(provider):
    config = get_config()
    return config[provider]['location']


def get_weather_url(provider, api_key, location):
    # url = "https://api.openweathermap.org/data/2.5/weather?q={}&APPID={}".format(location, api_key)
    # url = "https://api.openweathermap.org/data/2.5/forecast?id={}&units=metric&appid={}"
    # url = "http://api.openweathermap.org/data/2.5/forecast?q={0}&APPID={1}".format(location, api_key)

    try:
        return PROVIDERS_URL_TEMPLATES[provider](location=location, api_key=api_key)
    except KeyError:
        print("no default url for {0} found".format(provider))
        return ""


def get_weather(provider, api_key, location):
    url = get_weather_url(provider, api_key, location)
    r = requests.get(url)
    return r.json()


def save_weather(provider, weather):
    output_file_name = os.path.join(get_cache_dir(), "weather-{0}.json".format(provider))
    with open(output_file_name, 'w') as output:
        json.dump(weather, output)

def open_weather(provider):
    file_name = os.path.join(get_cache_dir(), "weather-{0}.json".format(provider))    
    with open(file_name) as json_file:
        data = json.load(json_file)
        process_weather(provider, data)

def process_weather(provider, data):
    if provider == "openweathermap":
        for result in data['list']:
            date = result['dt']
            temp = result['main']['temp']
            print("date:{} main:{}".format(date, temp - 273.15))

    if provider == "darkskynet":
        today = data['currently']
        today_date = today['time']
        today_icon = today['icon']
        today_temp = today['temperature']
        today_humidity = today['humidity']
        today_summary = today['summary']
        
        summary = {
            'today_date': get_date(today_date),
            'today_icon': get_icon(today_icon),
            'today_temp': today_temp,
            'today_humidity': today_humidity,
            'today_summary': today_summary,
        }

        days = data['daily']['data']
        for index, day in enumerate(days[0:3], start=1):
            day_time = day['time']
            day_icon = day['icon']
            day_min = day['temperatureMin']
            day_max = day['temperatureMax']

            summary['day_{}_date'.format(index)] = get_date(day_time)
            summary['day_{}_icon'.format(index)] = get_icon(day_icon)
            summary['day_{}_min'.format(index)] = day_min
            summary['day_{}_max'.format(index)] = day_max

        save_summary_to_file(summary)

def get_date(timestamp):
    data = datetime.fromtimestamp(timestamp).strftime('%A')    
    return data

def get_icon(icon):
    if(icon == "clear-day"):
        return "32.png"

    if(icon == "clear-night"):
        return "31.png"

    if(icon == "rain"):
        return "12.png"        

    if(icon == "snow"):
        return "14.png"

    if(icon == "sleet"):
        return "14.png"   

    if(icon == "wind"):
        return "24.png"
    
    if(icon == "fog"):
        return "24.png"                
        
    if(icon == "cloudy"):
        return "28.png"    
        
    if(icon == "partly-cloudy-day"):
        return "30.png"                
        
    if(icon == "partly-cloudy-night"):
        return "29.png"                

    return "3200.png"

def save_summary_to_file(summary):
    # should save file with following format:
    """
    {
        "today_date": 1615242008,
        "today_icon": "cloudy",
        "today_temp": 22.57,
        "today_humidity": 0.82,
        "today_summary": HOT,
        "day_1_time": 1615172400,
        "day_1_icon": "rain",
        "day_1_min": 19.07,
        "day_1_max": 26.6,
        "day_2_time": 1615258800,
        "day_2_icon": "rain",
        "day_2_min": 19.26,
        "day_2_max": 26.41,
        "day_3_time": 1615345200,
        "day_3_icon": "rain",
        "day_3_min": 18.17,
        "day_3_max": 27.55
    }"""    

    output_file_name = os.path.join(get_cache_dir(), "weather.json")
    with open(output_file_name, 'w') as output:
        json.dump(summary, output)    

def main(provider):
    api_key = get_api_key(provider)
    location = get_api_location(provider)

    weather = get_weather(provider, api_key, location)

    save_weather(provider, weather)


if __name__ == '__main__':
    # provider = 'openweathermap'
    p = 'darkskynet'

    main(p)
    open_weather(p)
