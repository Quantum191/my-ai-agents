
# Step 10: Add functionality to fetch and display weather data
import requests

def get_weather(city):
    api_key = 'your_api_key_here'
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        return None

def display_weather(data):
    if data:
        print(f'City: {data["name"]}')
        print(f'Temperature: {data["main"]["temp"]}K')
        print(f'Weather: {data["weather"][0]["description"]}')
    else:
        print('Failed to retrieve weather data')

if __name__ == '__main__':
    city = input('Enter a city name: ')
    weather_data = get_weather(city)
    display_weather(weather_data)