import json
import requests
import csv
import re
from dotenv import load_dotenv
import os

load_dotenv()

# ---------------------------------------------------
# Global Variables
# ---------------------------------------------------
CSV_COLUMNS = ['Email', 'Data']
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
def fetchProfile(username:str, company:str =""):
    query = username if len(company) == 0 else f'{username} {company}'
    api_url = "https://www.googleapis.com/customsearch/v1?key={}&cx={}&q={}&num=10".format(API_KEY, SEARCH_ENGINE_ID, query)
    
    try:
        response = requests.get(api_url).json()
    except requests.exceptions.RequestException:
        return []
    
    print(response)
    links = []
    # print(response['queries']['request'][0]['searchTerms'])
    if 'items' in response:
        for item in response['items']:
            formatted_url = item['formattedUrl']
            title = item['title'].lower()
            snippet = item['snippet'].lower()
            
            if '/in/' in formatted_url:
                first_name = item['pagemap']['metatags'][0]['profile:first_name']
                last_name = item['pagemap']['metatags'][0]['profile:last_name']
                if company in title or company in snippet or username in title or username in snippet:
                    links.append({
                        "url": formatted_url,
                        "title": title,
                        "firstName": first_name,
                        "lastName": last_name
                    })
                    break
                elif len(company) == 3 and 'airport' in title or 'airport' in snippet:
                    links.append({
                        "url": formatted_url,
                        "title": title,
                        "firstName": first_name,
                        "lastName": last_name
                    })
                    break
            elif '/company/' in formatted_url:
                if company in title or company in snippet:
                    links.append({
                        "url": formatted_url,
                        "title": title,
                    })
                    break
            else:
                continue
    elif 'spelling' in response:
        new_query = response['spelling']['correctedQuery']
        links = fetchProfile(" ".join(new_query.split(" ")[:-1]))

    return links


def hello(event, context):
    email = event['queryStringParameters']['email'];
    match = re.match(r'^([a-z0-9_\.-]+)@([\da-z\.-]+)\.([a-z\.]{2,6})$', email)
    result = []
    if match:
        username = match.group(1)
        company = match.group(2)
        username = username.replace(".", " ").replace("_", " ")
        company = company.replace(".", " ").replace("_", " ")
        if company in PERSONAL_PREFIX:
            links = fetchProfile(username)
        else:
            links = fetchProfile(username, company)
        result.append({
            'Email': email,
            'Data': links,
        })

    response = {
        "statusCode": 200,
        "body": json.dumps(result)
    }

    return response

    # Use this code if you don't use the http event with the LAMBDA-PROXY
    # integration
    """
    return {
        "message": "Go Serverless v1.0! Your function executed successfully!",
        "event": event
    }
    """
