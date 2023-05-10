import json
import requests
from fuzzywuzzy import fuzz
import re

CSV_COLUMNS = ['Email', 'Data']
PERSONAL_PREFIX = ['gmail', 'hotmail', 'yahoo']
API_KEY = 'API_KEY'
SEARCH_ENGINE_ID = 'SEARCH_ENGINE'

# words = set(nltk.corpus.words.words() + ["hydra", "ideon", "misty", "evok", "arix-tech", "platform88"])
# word_lengths = set(len(w) for w in words)

# def extractCompany(company:str):
#     """
#         Function to extract the company name from matching to the longest matching english words.

#         Input: 
#             - Company name from the work email of the queried user

#         Output:
#             - Most probable name of the company split appropriately
#     """
#     segmented_words = []
#     i = 0
#     while i < len(company):
#         j = min(len(company), i + max(word_lengths))
#         while j > i:
#             if company[i:j] in words:
#                 segmented_words.append(company[i:j])
#                 i = j
#                 break
#             j -= 1
#         else:
#             segmented_words.append(company[i])
#             i += 1

#     # Print the segmented words
#     return ' '.join(segmented_words)


def fetchProfile(query:str, email:str):
    api_url = "https://www.googleapis.com/customsearch/v1?key={}&cx={}&q={}&num=10".format(API_KEY, SEARCH_ENGINE_ID, query)
    try:
        response = requests.get(api_url).json()
    except requests.exceptions.RequestException:
        return []
    
    links = []
    # print(response['queries']['request'][0]['searchTerms'])
    if int(response['searchInformation']['totalResults']) > 0:
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
                    score1 = fuzz.partial_token_sort_ratio(query, first_name)
                    score2 = fuzz.partial_token_sort_ratio(query, last_name)
                    links.append({
                        "firstName": first_name,
                        "lastName": last_name,
                        "email": email,
                        "url": formatted_url,
                        "fuzzyAccuracy": ((score + score1 + score2) / 3),
                    })
                    
        if len(links) > 0:
            max_item = max(links, key=lambda x: x['fuzzyAccuracy'])
            return max_item
        else:
            return {
                "firstName": query,
                "lastName": query,
                "email": email,
                "url": "NOT FOUND",
                "fuzzyAccuracy": "N/A"
            }
    else:
        return {
            "firstName": query,
            "lastName": query,
            "email": email,
            "url": "NOT FOUND",
            "fuzzyAccuracy": "N/A"
        }

def lambda_handler(event, context):
    result = []
    
    email = event['queryStringParameters']['email']
    first_name = event['queryStringParameters']['firstName']
    last_name = event['queryStringParameters']['lastName']
    version = event['queryStringParameters']['version']
    companyDomain = event['queryStringParameters']['company']
    # match = re.match(r'^([\w\.\-]+)@([\w\-]+\.)?([\w\-]+)\.[\w\-]+$', email)
    if version == "5":
        print("version 5")
        query = f'{first_name} {last_name} {companyDomain}'
        links = fetchProfile(query=query, email=email)
        result.append(links)
    elif version == "6":
        print("version 6")
        query = f'{email}'
        links = fetchProfile(query=query, email=email)
        result.append(links)
    elif version == "1":
        print("version 1")
        query = f'{first_name} {last_name} {companyDomain}'
        links = fetchProfile(query=query, email=email)
        result.append(links)
    elif version == "2":
        print("version 2")
        query = f'{first_name} {companyDomain}'
        links = fetchProfile(query=query, email=email)
        result.append(links)
    elif version == "3":
        print("version 3")
        query = f'{last_name} {companyDomain}'
        links = fetchProfile(query=query, email=email)
        result.append(links)
    elif version == "4" :
        print("version 4")
        query = f'{first_name} {last_name}'
        links = fetchProfile(query=query, email=email)
        result.append(links)
    elif version == "7":
        print("version 7")
        query = f'{last_name} {email.split("@")[1]}'
        links = fetchProfile(query=query, email=email)
        result.append(links)
    
    # TODO implement
    return {
        'statusCode': 200,
        'body': json.dumps(result)
    }