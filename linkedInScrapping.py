# ---------------------------------------------------
# To use this script just input the emails to search in the 
# "input.csv" file and run the script. The result will be 
# automatically saved in the "output.csv" file.
# ---------------------------------------------------
import requests
import csv
import re
from dotenv import load_dotenv
import os


load_dotenv()

# ---------------------------------------------------
# Global Variables
# ---------------------------------------------------
CSV_COLUMNS = ['Email', 'LinkedIn', 'More']
API_KEY = os.getenv('GOOGLE_API_KEY')
SEARCH_ENGINE_ID = os.getenv('SEARCH_ENGINE_ID')
CSV_FILE_IN = "input.csv"
CSV_FILE_OUT = "output.csv"
PERSONAL_PREFIX = ['gmail', 'hotmail', 'yahoo']

# ---------------------------------------------------
# Function to call the custom Google Search on linkedin subdomain
# Input:
# - Email address for lookup
# Output:
# - List of Links found by the google search
# ---------------------------------------------------
def fetchProfile(username:str, company = ""):
    query = username if len(company) == 0 else f'{username} {company}'
    api_url = "https://www.googleapis.com/customsearch/v1?key={}&cx={}&q={}&num=10".format(API_KEY, SEARCH_ENGINE_ID, query)
    
    response = requests.get(api_url).json()
    links = []
    
    print(response['searchInformation'])
    if 'items' in response:
        for item in response['items']:
            if '/in/' in item['formattedUrl']:
                if company in item['pagemap']['metatags'][0]['og:title']:
                    print(item['pagemap']['metatags'][0]['og:title'])
                    links.append(item['formattedUrl'])     
            elif '/company/' in item['formattedUrl']:
                links.append(item['formattedUrl'])
            else:
                continue
    elif 'spelling' in response:
        links = fetchProfile(response['spelling']['correctedQuery'])

    return links
    
# ---------------------------------------------------
# Function to write the resulting data to the output.csv
# Input:
# - Dictionnary of Email with their linkedin links
# Output:
# - "output.csv" file created in the root folder
# ---------------------------------------------------
def writeDataCSV(data):
    try:
        with open(CSV_FILE_OUT, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames= CSV_COLUMNS)
            writer.writeheader()
            for item in data:
                writer.writerow(item)
    except IOError:
        print("I/O Error")

# ---------------------------------------------------
# Function to read the emails to fetch from input.csv
# Input:
# - Input File Name "input.csv"
# Output:
# - List of emails to fetch the call the google search
# ---------------------------------------------------
def readDataCSV(CSV_FILE_IN):
    data = []
    try:
        with open(CSV_FILE_IN, 'r') as f:
            csv_reader = csv.reader(f, delimiter=',')
            line_count = 0
            for row in csv_reader:
                if line_count == 0:
                    print(f'Column names are {", ".join(row)}')
                    line_count += 1
                else:
                    data.append(row[0])
                    line_count += 1
            print(f'Processed {line_count} lines.')
        return data
    except IOError:
        print("I/O Error")


# ---------------------------------------------------
# Main Function to call the functions above
# ---------------------------------------------------
if __name__ == "__main__":
    resultData = []
    # data = readDataCSV(CSV_FILE_IN)
    data = ['jack@advantechcap.com']
    for email in data:
        match = re.match(r'^([a-z0-9_\.-]+)@([\da-z\.-]+)\.([a-z\.]{2,6})$', email)
        if match:
            username = match.group(1)
            company = match.group(2)
            if company in PERSONAL_PREFIX:
                links = links = fetchProfile(username)
            else:
                links = links = fetchProfile(username, company)
            resultData.append({
                'Email': email,
                'LinkedIn': links,
            })
    print(resultData)
    # writeDataCSV(resultData)