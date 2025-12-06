from flask import Flask, request, render_template
import requests
from datetime import datetime

app = Flask(__name__)


@app.route('/', methods=['GET'])
def home_page():
    """
    Main route for rendering the weather app.
    Handles fetching city input, geocoding, weather data and formatting dates.
    Returns the HTML page with weather forecast or error messages.
    """
    city = request.args.get('city')    # get the city name from URL parameters
    country = ""
    weather_data = None
    error_message = None

    if city:
        # get coordinates from Open-Meteo geocoding, if the city name was given
        geo_url = "https://geocoding-api.open-meteo.com/v1/search"
        geo_params = {"name": city, "count": 1}   # return first match

        try:
            # make requests to Opem-Mateo geocoding API
            geo_response = requests.get(geo_url, params=geo_params, timeout=5)
            geo_response.raise_for_status()  # raise exception if HTTP status != 200
            geo_data = geo_response.json()   # parse JSON response
        except requests.exceptions.RequestException:
            error_message = "Failed to fetch the city coordinates. Please try again."
            return render_template("index.html",
                                   city=city,
                                   country=country,
                                   weather_data=weather_data,
                                   error_message=error_message)

        # if city result are no found -> return not found error
        if not geo_data.get("results"):
            error_message = f"City '{city}' not found"
            return render_template("index.html",
                                   city=city,
                                   country=country,
                                   weather_data=weather_data,
                                   error_message=error_message)
        # extract latitude and longitude from the geo response
        lat = geo_data["results"][0]["latitude"]
        lon = geo_data["results"][0]["longitude"]
        country = geo_data["results"][0]["country"]

        # get the forecast data from the coordinates
        forecast = get_forecast(lat, lon)

        if "error" in forecast:
            # if API returned an error
            error_message = forecast.get("error")
        else:
            # extract the daily forecast data
            weather_data = forecast.get("daily")    # save access
            formatted_dates = []
            for date in weather_data["time"]:
                data_type = datetime.strptime(date, "%Y-%m-%d")    # strptime: from string t datetime
                formatted_dates.append(data_type.strftime("%A %d %b"))   # strftime from datetime to string
            # replace the original time list with the formated dates
            weather_data["time"] = formatted_dates

    # return HTML with city, weather_data or error
    return render_template("index.html",
                           city=city,
                           country=country,
                           weather_data=weather_data,
                           error_message=error_message)

def get_forecast(lat: float, lon: float):
    """ Fetch 7-day forecast data from Open-Mateo API, using latitude and longitude.
     Return a dictionary with daily forecast or an error messages.
     """
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": ["temperature_2m_max", "temperature_2m_min", "relative_humidity_2m_mean"],
        "timezone": "auto"
    }

    try:
        # make request to forecast API
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()   # raise exception if HTTP !=200
        data = response.json()
    except requests.exceptions.RequestException:
        return {"error": "Failed to fetch weather data from API"}

    if "daily" not in data:
        return {"error": "Failed to get weather data"}
    # return forecast dictionary
    return data


if __name__ == '__main__':
    # run the app in debug mode
    app.run(debug=True)



