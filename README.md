# PIC-16B-Project: College Application Guide

## Names of group members: 
Daisy Watters and Michelle Li

## Short description of this project: 
In this project, we will be creating a college application guide such that high school students can input their GPA and college preferences, and we will provide them with a list of suggestions on where to apply.

## List of Python packages used and their versions:
- Scrapy 2.8.0
- Numpy 1.24.4
- Pandas 2.0.3
- Plotly 5.9.0
- PyWebIO 1.8.3

## How to complete project for yourself:

### Data Collection via Web Scraping
#### TO DO:
1. Download `colleges` file from git main
2. Open terminal and navigate to where the `colleges` file exists on your machine
3. Run `college_spider.py` in terminal with `scrapy crawl college_spider -o colleges.csv` to create your own csv file of college statistical data scraped from [appily](https://www.appily.com/colleges/gpa) OR download `colleges.csv` from git main

#### How it works:
###### `parse` function
1. Parses the starting url page that contains GPAs from 2.0 to 4.0, and navigates to the designated page for each GPA (each of these GPA pages contains a list of colleges you would qualify for with the given GPA, and it also includes some of their statistics)
2. Loops through all GPA page links and yields scrapy.Request using the url for the specified GPA page which calls `parse_stats` method

###### `parse_stats` function
1. Scrapes college name, average GPA, acceptance rate, institution type, and total number of undergraduate students for each college on each GPA page
2. Yields dictionary of college's statistics

### Website Design and Functionality 
#### TO DO:
1. Download second data set from [opendatasoft](https://public.opendatasoft.com/explore/dataset/us-colleges-and-universities/table/?flg=en-us)
2. Download `applications.py` file from git main
3. Run `applications.py` in terminal with `python applications.py`

#### How it works:
###### `Website` function
Uses pywebio built-in functions to create a functional website where users can input GPA, preferred school type, preferred number of undergraduates in each grade level, and preferred region of study. Website outputs suggestions for schools to apply to in the form of an interactive plotly map and table.

1. Aesthetic and functional features of website are created, including headings, clickable drop down menus
2. `college_recs` function is called with user inputs to make data frame of suggested colleges called `college_table`
3. `college_recs_map` function is called with `college_table` to create map of suggested colleges called `college_map`
4. Data frame and map are converted to html in order to be displayed on website

###### `prepare_df` function
Cleans data frame for future merging and website display purposes

1. Takes in data frame
2. Removes unwanted columns and rows with colleges outside of the USA
3. Converts urls to https web addresses so they will be clickable links when displayed on website
4. Returns cleaned data frame

###### `college_recs` function
Creates data frame of recommended colleges and their average unweighted GPA, acceptance rate, type of institution, location, website, and approximate number of students per grade level based on user input.

1. Reads in data from [opendatasoft](https://public.opendatasoft.com/explore/dataset/us-colleges-and-universities/table/?flg=en-us), a website with a ready made data frame containing over 6000 colleges in the U.S. and US territories, as a new data frame called `colleges_locations`
2. `prepare_df` function is called with `colleges_locations` data frame
3. `colleges.csv` that was created using web scraping is read in as a new data frame `colleges_stats`, with the college names adjusted to match `colleges_locations`
4. `colleges_locations` and `colleges_stats` are merged
3. U.S. States are divided into West, Midwest, Northeast, and South regions
4. Lowerbounds and upperbounds of the different college sizes are set
5. `Longitude` and `Latitude` column are created based on location data from `colleges_locations`
6. Final college recommendations are outputed based on user GPA, preferred type of institution, prefereed size of grade levels, and preferred location based on region

###### `college_recs_map` function
Creates `Plotly map` of recommended colleges and their stats using data frame of recommended colleges.

1. Creates `scatter_mapbox` where point size is based on size of school, and hover data includes average unweighted GPA, location, acceptance rate, type of institution, and number of students per grade level
