import scrapy

class collegeSpider(scrapy.Spider):
    name = 'college_spider'

    start_urls = ["https://www.appily.com/colleges/gpa"]

    def parse(self, response):
        '''
        Meant to parse the starting url page with all the GPAs 
        Navigates to the designated page with links to colleges for the specified GPA
        Does not return any data
        '''    
        # URL for the specified GPA page          
        gpa_college_url = [gpa.attrib["href"] for gpa in response.css("div.view-content.view-row-count-1 div.item-list ul li div.views-field.views-field-title span.field-content a")]

        # loops through all GPA page links 
        for link in gpa_college_url:
            url = "https://www.appily.com" + link
            # Yield scrapy.Request using the url for the specified GPA page
            yield scrapy.Request(url, callback = self.parse_stats)


    def parse_stats(self, response):
        '''
        Meant to parse the page for all colleges of a given GPA
        Returns the average GPA and acceptance rate for each college
        '''

        # loops through each college on GPA page
        # scrapes college name, average gpa, acceptance rate, institution type, total number of undergrad
        for college in response.css("article.college-list--card.gpa-result"):  

            college_name = college.css("div.college-list--card-head div.college-list--card-title-wrap div.college-list--card-title div.college-list--card-title-conatiner a::text").get()
            gpa = college.css("div.college-list--card-footer div.college-list--card-outer div.college-list--card-inner div.college-list--card-data-val div.field.average-gpa::text").get()
            acceptance_rate = college.css("div.college-list--card-footer div.college-list--card-outer div.college-list--card-inner div.college-list--card-data-val div.field.acceptance-rate::text").get() 
            
            for match in college.css("div.college-list--card-footer div.college-list--card-outer div.college-list--card-inner"):       

                if match.css("div.college-list--card-data-label::text").get() == "type of institution":
                    type_institution = match.css("div.college-list--card-data-val::text").get()
                    
                if match.css("div.college-list--card-data-label::text").get() == "number of students":
                    num_students = match.css("div.college-list--card-data-val::text").get()
                    num_students = int(num_students.replace(",", ""))

            yield {"College" : college_name, 
                  "GPA" : gpa,
                  "Acceptance Rate" : acceptance_rate,
                  "Type of Institution" : type_institution,
                  "Number of Students" : round(num_students/4)}
            
           