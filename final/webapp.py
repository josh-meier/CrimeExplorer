import flask
from flask import render_template, request, redirect
import json
import sys
from api import *
from url import *
from city_state_list import *

app = flask.Flask(__name__)

violent_crime_types = ["murder_and_nnm","rape","robbery","aggravated_assault"]
property_crime_types = ["burglary","larceny_theft","motor_vehicle_theft","arson"]


#helper functions

# creating crime type count lists for bar charts
def get_violent_crime_count(location):
    violent_crime_counts = []
    for crime_type in violent_crime_types:
        result = api.num_of_crime_type_committed(crime_type, location)
        if result != None:
            result = result[0][0]
            violent_crime_counts.append(result)
    return violent_crime_counts
    

def get_property_crime_counts(location):
    property_crime_counts = []
    for crime_type in property_crime_types:
        result = api.num_of_crime_type_committed(crime_type, location)
        if result != None:
            result = result[0][0]
            property_crime_counts.append(result)
    return property_crime_counts



# store the highest and lowest cities
def get_city_with_highest_crime_rate(state):
    result = api.find_area_with_highest_crime_rate_among("City", state)
    city_highest_CR = result[0][0]
    return city_highest_CR

def get_city_with_lowest_crime_rate(state):
    result = api.find_area_with_lowest_crime_rate_among("City", state)
    city_lowest_CR = result[0][0]
    return city_lowest_CR

# url stuff for embedded maps
def get_heat_map_url(state):
    return heat_map_URls[state]

def get_US_map():
    return heat_map_URls["US"]

# store the crime rate and ranking of the state
def get_CR_and_ranking(location):
    result = api.get_crime_rate_and_ranking_for(location)
    
    if ", " in location:
        if result != None:
            ranking = result[0][3]
            crime_rate = result[0][2]
            population = result[0][4]
            return crime_rate, round(ranking,2), population
        else:
            return result, result, result
    else:
        if result != None:
            ranking = result[0][2]
            crime_rate = result[0][1]
            return crime_rate, ranking
        else:
            return result, result
# rotate the pie chart if the larceny_theft is more than 70% so the labels of the chart don't over lap with the header
def rotate_pie(location):
    prop = api.proportion_of_crime_type_committed("larceny_theft", location)
    rotation = 0
    if float(prop[0][0]) > 0.7:
        rotation = -90
    return rotation

def get_highest_or_lowest_city_url(state, city):
    url = "/city_result/" + state + "/"+city.replace(" ", "_") + "#results"
    return url

# This line tells the web browser to *not* cache any of the files.
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

@app.route('/', methods=["POST", "GET"])
def home():
    US_map = get_US_map()
    valid_search_input = True

    if request.method == "POST":
        input = request.form['location']
        if input not in valid_searchbar_locations:
            valid_search_input = False
        else:
            if "," in input:
                city, state = input.split(", ")
                url = "/city_result/" + state.replace(" ", "_") + "/" + city.replace(" ", "_") + "/#results"
                return redirect(url)
            else:  
                url = "/state_result/" + input.replace(" ", "_") + "/#results"
                return redirect(url)

    return render_template('home.html', US_map = US_map, valid_searchbar_locations=valid_searchbar_locations, valid_search_input=valid_search_input)

@app.route('/about')
def about_the_data():
    return render_template('about_this_data.html')

@app.route('/state_result/<state>/', methods=["POST", "GET"])
def state_results(state):
    '''
    The user query we implemented is the user wanting to find the crime statistic 
    information for the state of Iowa. They do this by clicking the Iowa link in the left
    navigation.
    '''
    state = state.replace("_", " ")


    violent_crime_counts = get_violent_crime_count(state)
    property_crime_counts = get_property_crime_counts(state)
    
    crime_type_values = property_crime_counts + violent_crime_counts

    city_highest_CR = get_city_with_highest_crime_rate(state)
    city_lowest_CR = get_city_with_lowest_crime_rate(state)

    heat_map_url = get_heat_map_url(state)
    US_map = get_US_map()

    state_CR, state_ranking = get_CR_and_ranking(state)

    city_highest_URL = get_highest_or_lowest_city_url(state, city_highest_CR)
    city_lowest_URL = get_highest_or_lowest_city_url(state, city_lowest_CR)



    rotation = rotate_pie(state)


    
    valid_search_input = True

    if request.method == "POST":
        input = request.form['location']
        if input not in valid_searchbar_locations:
            valid_search_input = False
        else:
            if "," in input:
                city, state = input.split(", ")
                url = "/city_result/" + state.replace(" ", "_") + "/" + city.replace(" ", "_") + "/#results"
                return redirect(url)
            else: 
                url = "/state_result/" + input.replace(" ", "_") + "/#results"
                return redirect(url)
    return render_template('state_results.html', 
        state=state, 
        heat_map_url=heat_map_url, 
        US_map = US_map, 
        city_highest_CR=city_highest_CR,
        city_lowest_CR=city_lowest_CR,
        crime_type_values=crime_type_values, 
        property_crime_counts=property_crime_counts, 
        violent_crime_counts=violent_crime_counts,
        state_CR = state_CR,
        state_ranking = state_ranking,
        city_highest_URL=city_highest_URL,
        city_lowest_URL=city_lowest_URL,
        valid_searchbar_locations=valid_searchbar_locations,
        rotation = rotation,
        valid_search_input=valid_search_input,
        )

@app.route('/city_result/<state>/<city>/',  methods=["POST", "GET"])
def city_results(state, city):
    '''
    (city) has the format of <city>, <state>
    '''
    only_city=city
    state = state.replace("_", " ")
    city = city.replace("_", " ") + ", " + state

    violent_crime_counts = get_violent_crime_count(city)
    property_crime_counts = get_property_crime_counts(city)
    crime_type_values = property_crime_counts + violent_crime_counts
    city_CR, city_ranking, city_population = get_CR_and_ranking(city)
    US_map = get_US_map()
    heat_map_url = get_heat_map_url(state)

    rotation = rotate_pie(city)

    city_google_search = "https://www.google.com/maps/place/" + city 

    valid_search_input = True

    if request.method == "POST":
        input = request.form['location']
        if input not in valid_searchbar_locations:
            valid_search_input = False
        else:
            if "," in input:
                city, state = input.split(", ")
                url = "/city_result/" + state.replace(" ", "_") + "/" + city.replace(" ", "_") + "/#results"
                return redirect(url)
            else:  
                url = "/state_result/" + input.replace(" ", "_") + "/#results"
                return redirect(url)
            
    return render_template('city_results.html',
        city = city,
        only_city=only_city,
        state = state,
        US_map = US_map, 
        heat_map_url=heat_map_url, 
        crime_type_values=crime_type_values, 
        property_crime_counts=property_crime_counts, 
        violent_crime_counts=violent_crime_counts,
        city_CR = city_CR,
        city_ranking =city_ranking,
        city_population = city_population,
        city_google_search=city_google_search,
        valid_searchbar_locations=valid_searchbar_locations,
        rotation = rotation,
        valid_search_input=valid_search_input
        )


'''
Run the program by typing 'python3 localhost [port]', where [port] is one of 
the port numbers you were sent by my earlier this term.
'''
if __name__ == '__main__':
    api = CrimeDataAPI()

    if len(sys.argv) != 3:
        print('Usage: {0} host port'.format(sys.argv[0]), file=sys.stderr)
        exit()

    host = sys.argv[1]
    port = sys.argv[2]
    app.run(host=host, port=port)
