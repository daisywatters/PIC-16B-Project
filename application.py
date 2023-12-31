import pywebio
from pywebio import start_server
from pywebio.input import *
from pywebio.output import *
import numpy as np
import pandas as pd
from plotly import express as px


def Website():
    '''
    Uses pywebio built-in functions to create a functional website where users can input GPA, preferred 
    school type, preferred number of undergraduates in each grade level, and preferred region of study. 
    Website outputs suggestions for schools to apply to in the form of an interactive plotly map and table.
    '''
    put_markdown('### Answer a couple questions and we will tell you where to apply!'), put_markdown('# **Welcome to Your College Application Guide**') # sets website heading and subheading
    with use_scope('scope1'):
        # lets users select their gpa from drop-down menu
        gpa = select("Select your GPA (Round for best approximation)：", ['4.0','3.9','3.8','3.7','3.6','3.5','3.4','3.3','3.2','3.1','3.0','2.9','2.8','2.7','2.6','2.5','2.4','2.3','2.2','2.1','2.0']) 
        gpa = float(gpa)
        # lets users choose preferred type of school via checkbox
        school_type = checkbox("Private vs. Public：", options=['Private', 'Public'])
        # lets users choose preferred number of undergraduates in each grade level via checkbox
        num_undergrads = select("Number of undergraduates per grade：", ['0 to 500 (Very Small)', '500 to 1,000 (Small)', '1,000 to 5,000 (Medium)', '5,000 to 10,000 (Large)', '10,000+ (Very Large)'])
        # shows map of different US regions
        put_image('https://www.mappr.co/wp-content/uploads/2021/12/us-regions-map-census.jpg')
        # lets users choose preferred region of study via checkbox
        location = checkbox("Preferred region of study：", options=['West', 'Midwest', 'Northeast', 'South'])
    
    with use_scope('scope1', clear=True):
        # calls function for creating dataframe of suggested colleges per user inputs
        college_table = college_recs(gpa, school_type, num_undergrads, location)
        # calls function for creating map of suggested colleges per user inputs
        college_map = college_recs_map(college_table)
        # drops Latitude, Longitude, and unwanted index columns so they won't be displayed on website
        college_table = college_table.drop(["Latitude", "Longitude", "index", "level_0"], axis=1)
        
        # converts 'college_map' plotly map to html for website
        college_map_html = college_map.to_html(include_plotlyjs="require", full_html=False)
        pywebio.output.put_html(college_map_html)
        # converts 'college_table' dataframe to html for website
        put_html(college_table.to_html(border=0, render_links=True))
        
def prepare_df(df):
    '''Returns a cleaned data frame
    Parameters: 
        df: the data frame to be cleaned
    Type: 
        df: two dimensional data structure
    Return: a cleaned data frame
    '''
    # selects only the columns we want to look at
    df = df[["geo_point_2d","name", "city", "state", "country", "website"]]
    # renames "name" column to "College" for future data merging purposes
    df = df.rename(columns={"geo_point_2d":"Coordinates", "name": "College", "city":"City", "state":"State", "country":"Country", "website":"Website"})
    
    # turns columns from all caps to having only first letter of each word capitalized
    df["College"] = df["College"].apply(lambda x: x.title())
    df["City"] = df["City"].apply(lambda x: x.title())
    
    # finds index of rows in df where colleges are not in the US
    not_USA_colleges = df[(df['Country'] != 'USA')].index 
    
    # delete these row indexes from dataFrame
    df = df.drop(not_USA_colleges)
    
    # makes every website link https for later user functionality purposes
    new_websites = [] # empty list
    # loops through each website in dataframe
    # if the website does not already start with "https://" this will be added to start of link
    for website in df["Website"]:
        if (website.startswith("https://") == False) and (website.startswith("NOT") == False):
            website = 'https://' + website
            new_websites.append(website)
        else:
            new_websites.append(website)
    # "Website" column of dataframe is updated with https websites
    df["Website"] = new_websites 
    
    return(df)

def college_recs(gpa_input, type_inst_input, size_input, location_input):
    '''
    Input: 
    - gpa input (select one value from 2.0 to 4.0 incremented by 0.1)
    - type of institution input (select one or more from public, private)
    - size input (select one value from 0 to 500, 500 to 1,000, 1,000 to 5,000, 5,000 to 10,000, or 10,000+)
    - location input (select one or more from Northeast, Midwest, South, West)
    
    Output: 
    - data frame with values for gpa, type of institution, size, location corresponding to user's 
    inputted selections
    '''
    
    # pull data from Opendatasoft containing over 6000 colleges in the U.S. and US territories.
    df = pd.read_json("us-colleges-and-universities.json")

    # use prepare_df function to clean the dataframe
    colleges_locations = prepare_df(df)

    # read in colleges.csv from web scraping Appily website 
    colleges_stats = pd.read_csv("colleges.csv")
    colleges_stats["College"] = colleges_stats["College"].apply(lambda x: x.title())

    # Merge dataframes from Opendatasoft and Appily
    data_merge = pd.merge(colleges_locations, colleges_stats, on='College')
    
    # Drop duplicates for Website name
    data_merge = data_merge.drop_duplicates(subset=['Website'])
    
    # Strip whitespace before "Public" and "Private" in the column for "Type of Institution"
    data_merge["Type of Institution"] = data_merge["Type of Institution"].apply(lambda x: x.strip())

    # Reset index for the new merged data frame
    data_merge = data_merge.reset_index()

    # Dictionary containing all the states in a given region
    region_dict = {
        "Northeast": ["PA", "NY", "VT", "ME", "NJ", "CT", "RI", "MA"],
        "Midwest": ["ND", "SD", "NE", "KS", "MN", "IA", "MO", "WI", "IL", "MI", "IN", "OH"],
        "South": ["TX", "OK", "AR", "LA", "MS", "AL", "TN", "KY", "FL", "GA", "SC", "NC", "VA", "WV", "DE", "MD"],
        "West": ["AK", "HI", "WA", "OR", "CA", "AZ", "NM", "NV", "UT", "CO", "ID", "WY", "MT"]
    }
    
    # Dictionary containing the tuples for a given size
    size_dict = {
        "0 to 500 (Very Small)" : (0, 500),
        "500 to 1,000 (Small)" : (500, 1000),
        "1,000 to 5,000 (Medium)" : (1000, 5000),
        "5,000 to 10,000 (Large)" : (5000, 10000),
        "10,000+ (Very Large)" : (10000, 500000)
    }
    
    # list of states in the user's inputted region choice 
    # for loop allows for multiple region selections
    states_in_region = []
    for region in location_input:
        states_in_region = states_in_region + region_dict[region]

    # assign lower size value to first value in size tuple
    # assign upper size value to second value in size tuple
    lowerbound, upperbound = size_dict[size_input]

    # initialize lists for latitude and longitude
    lat = []
    lon = []

    # loop through each row in data_merge data frame and extract the latitude and longitude for each college
    for i in range(0, data_merge.shape[0]):
        for key, value in data_merge["Coordinates"][i].items():
            if key == "lat":
                lat.append(value)
            if key == "lon":
                lon.append(value)

    # Create "Latitude" column and assign latitude for each college to it
    data_merge["Latitude"] = lat

    # Create "Longitude" column and assign longitude for each college to it
    data_merge["Longitude"] = lon
                
    # Drop "Coordinates" column from final data frame
    final_data = data_merge.drop(columns = ["Coordinates"])

    # Output GPA, Type of Institution, State, Number of Students, corresponding to user's 
    # inputted selections in the final data frame
    final_data = final_data[(data_merge["GPA"] <= gpa_input) & 
                            (data_merge["Type of Institution"].isin(type_inst_input)) & 
                            (data_merge["State"].isin(states_in_region)) &
                            (data_merge["Number of Students"] >= lowerbound) & 
                            (data_merge["Number of Students"] < upperbound)]

    # Reset index for final data frame
    final_data = final_data.reset_index()

    # Return final data frame
    return final_data
    
    
def college_recs_map(df):
    '''
    Input: 
    - data frame with user's ideal college recommendations according to their inputted preferences
    
    Output: 
    - map with colleges represented as points at the actual coordinates of the college's 
    location (using Latitude and Longitude) columns of the data frame
    - hovering over each point shows the college's GPA, City, State, Acceptance Rate, and Type of Institution
    '''

    # Create a scatter mapbox using plotly express
    fig = px.scatter_mapbox(df,
                            # Use college's real Latitude and Longitude coordinates
                            lat = "Latitude",
                            lon = "Longitude",
                            hover_name = "College",
                            # Data revealed upon hovering over the college point
                            hover_data = {"Latitude" : False, 
                                          "Longitude" : False, 
                                          "GPA" : True, 
                                          "City" : True, 
                                          "State" : True, 
                                          "Acceptance Rate" : True, 
                                          "Type of Institution" : True, 
                                          "Number of Students" : True},
                            zoom = 2,
                            # Size of point differs by the size of the college
                            size = "Number of Students",
                            size_max = 10,
                            opacity = 0.8,
                            height = 300)

    fig.update_layout(mapbox_style = "carto-positron")
    fig.update_layout(margin = {"r":0, "t":0, "l":0, "b":0})

    # Return map figure
    return fig

if __name__ == '__main__':
    pywebio.start_server(Website)
