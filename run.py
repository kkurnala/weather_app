import json
import urllib2
#from urllib.request import urlopen
from flask import Flask, render_template, session, redirect, url_for
from flask_script import Manager
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import Required

#------------------------------------------
# Create an application instance
app = Flask(__name__)
app.config['SECRET_KEY'] = 'Your secret key'
app.API_KEY = 'a7aa3d7781f619a0403fa5ae4ffb9111'    


#------------------------------------------
# Create different extension objects
manager = Manager(app)
bootstrap = Bootstrap(app)
moment = Moment(app)


#------------------------------------------
# Create a form for accepting user queries (i.e. zipcodes in our case)
class QueryForm(FlaskForm):
    zipcode = StringField('Zipcode', validators=[Required()])
    submit = SubmitField('Search')


#------------------------------------------
# Customizing Error handlers.... not required for now - can be improved
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


#------------------------------------------
# Main view function.
# app.route decorator registers index() function as the handler that is called whenever the root url (i.e. /) 
# is entered by the client/web browser.
@app.route('/', methods=['GET', 'POST'])
def index():
    form = QueryForm()
    if form.validate_on_submit():
        zipcode = form.zipcode.data
        session['zipcode'] = zipcode
        weather_info = get_weather_info(zipcode)
        print(weather_info)
        session['weather_info'] = weather_info        
        # Post/Redirect/Get pattern to avoid refresh problems        
        return redirect(url_for('index'))
    return render_template('index.html', form=form, zipcode=session.get('zipcode'), weather_info=session.get('weather_info'))


#------------------------------------------
# Helper function for retrieving weather info by making an API call to openweathermap.org
def get_weather_info(zipcode):    
    api_url = 'http://api.openweathermap.org/data/2.5/weather?zip=' + zipcode + '&appid=' + app.API_KEY
    data = urllib2.urlopen(api_url).read()
    data = json.loads(data)
    print(data)
    weather = {}
    weather['city'] = data['name']
    weather['zipcode'] = zipcode
    # Convert temperature to fahrenheit
    weather['temperature'] = data['main']['temp'] * (9./5) - 459.67
    weather['min_temperature'] = data['main']['temp_min'] * (9./5) - 459.67
    weather['max_temperature'] = data['main']['temp_max'] * (9./5) - 459.67
    weather['description'] = data['weather'][0]['description']
    weather['coords'] = [data['coord']['lon'], data['coord']['lat']]
    return weather

#------------------------------------------
# main method
if __name__ == '__main__':
    manager.run()
