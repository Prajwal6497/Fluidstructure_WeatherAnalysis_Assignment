# weather/views.py
import requests
from .models import WeatherData
from django.utils import timezone
from datetime import timedelta
from django.db.models import Avg
from django.shortcuts import render

def fetch_weather_data(city):
    api_key = '21e28a4f1461fac700078be9c30ffae0' 
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric'
    response = requests.get(url)
    return response.json()

# Function to store the fetched weather data in a DB
def save_weather_data(city):
    data = fetch_weather_data(city)

    temperature = data['main']['temp']  # Temperature in Celsius
    humidity = data['main']['humidity']  # Humidity percentage
    wind_speed = data['wind']['speed']  # Wind speed in m/s
    
    # Save the weather data into the database
    weather = WeatherData(
        city=city,
        temperature=temperature,
        humidity=humidity,
        wind_speed=wind_speed
    )
    weather.save()

# Function to calculate Avg Temp Trend
def calculate_temperature_trend(city):
    now = timezone.now()
    last_24_hours = now - timedelta(hours=24)
    weather_data = WeatherData.objects.filter(city=city, timestamp__gte=last_24_hours)
    avg_temperature = weather_data.aggregate(Avg('temperature'))['temperature__avg']

    return avg_temperature

# Function to calculate Avg Humidity Trend
def calculate_humidity_trend(city):
    now = timezone.now()
    last_24_hours = now - timedelta(hours=24)
    weather_data = WeatherData.objects.filter(city=city, timestamp__gte=last_24_hours)
    avg_humidity = weather_data.aggregate(Avg('humidity'))['humidity__avg']
    
    return avg_humidity

# Function to Show an alert if the weather condition is extreme.
def check_extreme_weather(city):
    weather_data = WeatherData.objects.filter(city=city).latest('timestamp')
    if weather_data.temperature > 35:  # Example threshold for extreme temperature
        return True
    return False

def display_alert(city):
    if check_extreme_weather(city):
        print(f'Alert: Extreme weather conditions in {city}!')

# Dashboard
def home(request):
    if 'city' in request.GET:
         city = request.GET['city']
    else:
         city = 'bangalore'  
    save_weather_data(city)
    avg_temp = calculate_temperature_trend(city)
    avg_humidity = calculate_humidity_trend(city)
    alert = check_extreme_weather(city)

    # Round the values to 1 decimal place
    avg_temp = round(avg_temp, 1) if avg_temp is not None else None
    avg_humidity = round(avg_humidity, 1) if avg_humidity is not None else None

    context = {
        'city': city,
        'avg_temp': avg_temp,
        'avg_humidity': avg_humidity,
        'alert': alert
    }
    return render(request, 'index.html', context)



   