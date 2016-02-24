from flask import Flask
import urllib2
import json
import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base


from models import *

engine = create_engine('mysql://root:password@localhost/weather_data?charset=utf8&use_unicode=0')
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

app = Flask(__name__)

def init_db():
    from models import *
    Base.metadata.create_all(bind=engine)



@app.route("/")
def hello():
    return "Hello World!"

@app.route("/<int:zip_code>")
def check_weather(zip_code):
    """
    check if the weather is in the db
    """
    now = datetime.datetime.now()
    one_hour_ago = now - datetime.timedelta(hours=1)
    locale = grab_weather_db(zip_code)
    if locale:
        locale_obj = locale[0]
        if locale_obj.date > one_hour_ago:
            forecast_list = retrieve_forecasts(locale_obj)
            return str(forecast_list)
    parsed_json = grab_weather_api(zip_code)
    days_list = create_days_list(parsed_json)
    weather_list = create_weather_list(parsed_json)
    forecasts = create_forecasts(weather_list)
    locale = refresh_weather_data(zip_code, forecasts)
    forecast_list = retrieve_forecasts(locale)
    return str(forecast_list)

def retrieve_forecasts(locale):
    forecast_list = []
    for i in locale.forecasts:
        forecast_list.append(i.text)
    return forecast_list


def grab_weather_api(zip_code):
    zips = str(zip_code)
    weather_api = '0ff7b51cbfd27331'
    url = 'http://api.wunderground.com/api/' + weather_api + '/forecast/q/' + zips +'.json'
    f = urllib2.urlopen(url)
    json_string = f.read()
    parsed_json = json.loads(json_string)
    f.close()
    return parsed_json

def grab_weather_db(zip_code):
    locale = db_session.query(Locale).filter(Locale.zip_code == zip_code).all()
    return locale

def refresh_weather_data(zip_code, forecasts):
    old_locale = db_session.query(Locale).filter(Locale.zip_code==zip_code).all()
    if old_locale:
        old_entry = old_locale[0]
        db_session.delete(old_entry)
        db_session.commit()
    new_locale = create_locale(zip_code, forecasts)
    return new_locale

def create_locale(zip_code, forecasts_list):
    """
    create a Locale object that has forecasts in forecasts_list
    """
    date = datetime.datetime.now()
    new_locale = Locale(zip_code=zip_code, date=date)
    new_locale.forecasts.extend(forecasts_list)
    db_session.add(new_locale)
    db_session.commit()
    return new_locale


def create_days_list(parsed_json):
    """
    return a list of days from parsed json
    """
    days = []

    for period in parsed_json['forecast']['txt_forecast']['forecastday']:
        days.append(str(period['title']))
    return days

def create_weather_list(parsed_json):
    """
    return a list of weather strings for each day from parsed json
    """
    weather = []
    for period in parsed_json['forecast']['txt_forecast']['forecastday']:
        weather.append(str(period['fcttext']))
    return weather



def create_forecasts(weather_list):
    """
    create a list of forecast objects given list

    """
    forecasts_list = []
    for idx in range(len(weather_list)):
        period = idx
        forecasts_list.append(Forecast(text=weather_list[idx], period=idx))
    return forecasts_list




@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()




if __name__ == "__main__":
    init_db()
    app.run(debug=True)
    # unittest.main()


