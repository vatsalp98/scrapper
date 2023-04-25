import csv
import os
import re
import nltk
import requests
from dotenv import load_dotenv
from fuzzywuzzy import fuzz
import itertools

load_dotenv()
words = set(nltk.corpus.words.words() + ["hydra", "ideon", "misty"])
word_lengths = set(len(w) for w in words)

def extractCompany(company:str):
    """
        Function to extract the company name from matching to the longest matching english words.

        Input: 
            - Company name from the work email of the queried user

        Output:
            - Most probable name of the company split appropriately
    """
    segmented_words = []
    i = 0
    while i < len(company):
        j = min(len(company), i + max(word_lengths))
        while j > i:
            if company[i:j] in words:
                segmented_words.append(company[i:j])
                i = j
                break
            j -= 1
        else:
            segmented_words.append(company[i])
            i += 1

    # Print the segmented words
    return ' '.join(segmented_words)


def writeDataCSV(data):
    """
        Function to write the resulting data to the output.csv

        Input: 
            - Dictionnary of Emails with their urls

        Output:
            - "output2.csv" file created in the root folder from the dictionnary
    """
    try:
        with open(CSV_FILE_OUT, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames= CSV_COLUMNS)
            writer.writeheader()
            for item in data:
                writer.writerow(item)
    except IOError:
        print("I/O Error")


def readDataCSV(CSV_FILE_IN):
    """
        Function to read data from CSV File
        
        Input Variables:
            - CSV_FILE_IN: str (name of the csv to read from)
        
        Return:
            - data: List of all the rows inside the CSV
    """
    
    data = []
    try:
        with open(CSV_FILE_IN, 'r', encoding='utf-8') as f:
            csv_reader = csv.reader(f, delimiter=',')
            line_count = 0
            for row in csv_reader:
                if line_count == 0:
                    print(f'Column names are {", ".join(row)}')
                    line_count += 1
                else:
                    data.append({
                        "firstName": row[0],
                        "lastName" : row[1],
                        "email" : row[2],
                    })
                    line_count += 1
            print(f'Processed {line_count} lines.')
        return data
    except IOError:
        print("I/O Error")


def fetchProfile(query:str, email:str):
    """
    This function named fetchProfile takes in three arguments: fullName, email,and company.The company argument is optional and defaults to an empty string.

    The function queries the Google Custom Search API using the API_KEY and SEARCH_ENGINE_ID variables. It searches for fullName concatenated with company as the query string.

    If the API call returns a valid response, the function extracts links from the response with /in/ in the URL format. It then extracts the first name and last name from the metadata of each link's webpage using the pagemap dictionary.
    If the extracted first name and last name match 
    fullName, and company is found in the title or snippet of the link, the link is added to the list of links with an accuracy rating of "High". If the first name and last name match fullName, but company is not found in the title or snippet of the link, the link is added to the list of links with an accuracy rating of "Med".

    Finally, the function returns the list of links
    """
    api_url = "https://www.googleapis.com/customsearch/v1?key={}&cx={}&q={}&num=10".format(API_KEY, SEARCH_ENGINE_ID, query)
    
    try:
        response = requests.get(api_url).json()
    except requests.exceptions.RequestException:
        return []
    links = []
    if 'items' in response:
        for item in response['items']:
            formatted_url = item['formattedUrl']
            title = item['title'].lower()
            snippet = item['snippet'].lower()
            if '/in/' in formatted_url:
                first_name = item['pagemap']['metatags'][0]['profile:first_name'].lower()
                last_name = item['pagemap']['metatags'][0]['profile:last_name'].lower()
                description = item['pagemap']['metatags'][0]['og:description'].lower()
                score = fuzz.partial_token_sort_ratio(query, title + description)
                links.append({
                    "firstName": first_name,
                    "lastName": last_name,
                    "url": formatted_url,
                    "email": email,
                    "accuracy": score 
                })
    
    max_item = max(links, key=lambda x: x['accuracy'])
    return max_item

if __name__ == "__main__":
    """
        Global Variables
    """ 
    CSV_COLUMNS = ['firstName', 'lastName', 'url','email', 'accuracy']
    COMMONS = ["gmail", "hotmail", "outlook", "yahoo"]
    API_KEY = os.getenv('GOOGLE_API_KEY')
    SEARCH_ENGINE_ID = os.getenv('SEARCH_ENGINE_ID')
    CSV_FILE_IN = "newInput.csv"
    CSV_FILE_OUT = "output2.csv"
    # Uncomment this like to use a `input.csv` file 
    data = readDataCSV(CSV_FILE_IN)
    final_data = []
    for item in data:
        first_name = item["firstName"].lower()
        last_name = item["lastName"].lower()
        email = item['email']
        match = re.match(r'^([\w\.\-]+)@([\w\-]+\.)?([\w\-]+)\.[\w\-]+$', email)
        temp_data = []
        
        if match:
            company = match.group(3)
            company = extractCompany(match.group(3)) if len(company) > 8 else match.group(3)
            
            queries = [first_name, last_name, company]
            permutations = list(itertools.permutations(queries))
            
            for p in permutations:
                query = ' '.join(p)
                result = fetchProfile(query=query, email=email)
                temp_data.append(result)
                
        
        same_url = all(item['url'] == temp_data[0]['url'] for item in temp_data)
        
        if same_url:
            final_data.append(temp_data[0])

    writeDataCSV(final_data)
            

# Search Combinations
# 1) first, last
# 2) first, last, company
# 3) first, company
# 4) last company
# 5) email
# 6) email, first, last
# 7) email, first, company
# first, last, company1, company2, email
# find all permutations of queries and find the best results from this

# try different searching queries for missing data
# fuzzy matching after results are given out