import requests
from fuzzywuzzy import fuzz
import csv

CSV_COLUMNS = ['Email', 'Data']
PERSONAL_PREFIX = ['gmail', 'hotmail', 'yahoo']
API_KEY = 'AIzaSyA31UZKdSo-5PKef5aSzrJPEsAYk8gcg2M'
SEARCH_ENGINE_ID = '32f5c72abc9ec46da'

def read_data_csv(csv_file:str):
    """
        Helps read data from a given CSV File and returns the data as a List

        - input: csv_file:str name of the csv file to read from
        - output: List of rows in the csv file
    """
    with open(csv_file, mode="r", encoding="utf-8") as csv_file:
        csv_reader = csv.DictReader(csv_file)
        rows = [row for row in csv_reader]
    return rows

def write_data_csv(csv_file:str, rows:list):
    """
        Helps write data to a specific csv file

        - input: 
            - csv_file: str name of the output csv file
            - rows: List of the data to be written to the CSV File
        - output:
            - CSV: File created in the root directory
    """
    fieldnames = ['firstName', 'lastName', 'email', 'url', 'fuzzyAccuracy']
    with open(csv_file, mode="w", newline='', encoding="utf-8") as csv_file:
        csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        csv_writer.writeheader()
        csv_writer.writerows(rows)

def calculate_fuzzy_accuracy(query: str, title: str, description: str, first_name: str, last_name: str, given_first_name: str, given_last_name: str) -> float:
    """
        Calculate the fuzzy Accuracy score between the found results and the given queries
    """
    title_description_score = fuzz.partial_token_sort_ratio(query, title + description)
    first_name_score = fuzz.partial_token_sort_ratio(given_first_name, first_name)
    last_name_score = fuzz.partial_token_sort_ratio(given_last_name, last_name)
    return (title_description_score + first_name_score + last_name_score) / 3

def fetchProfile(query:str, email:str, d_first_name: str, d_last_name:str):
    api_url = "https://www.googleapis.com/customsearch/v1?key={}&cx={}&q={}&num=10".format(API_KEY, SEARCH_ENGINE_ID, query)
    try:
        response = requests.get(api_url).json()
    except requests.exceptions.RequestException:
        return []
    
    if int(response['searchInformation']['totalResults']) == 0:
        return {
            "firstName": d_first_name,
            "lastName": d_last_name,
            "email": email,
            "url": "NOT FOUND",
            "fuzzyAccuracy": 0.00
        }
    
    links = []
    for item in response['items']:
        formatted_url = item['formattedUrl']
        title = item['title'].lower()
        # Snippet not Used for now
        # snippet = item['snippet'].lower()
        if '/in/' in formatted_url:
            first_name = item['pagemap']['metatags'][0]['profile:first_name'].lower()
            last_name = item['pagemap']['metatags'][0]['profile:last_name'].lower()
            description = item['pagemap']['metatags'][0]['og:description'].lower()
            score = calculate_fuzzy_accuracy(query=query, description=description, title=title, first_name=first_name, last_name=last_name, given_first_name=d_first_name, given_last_name=d_last_name)
            links.append({
                "firstName": first_name,
                "lastName": last_name,
                "email": email,
                "url": formatted_url,
                "fuzzyAccuracy": score,
            })
    
    max_item = {
        "firstName": d_first_name,
        "lastName": d_last_name,
        "email": email,
        "url": "NOT FOUND",
        "fuzzyAccuracy": 0.00
    } if len(links) == 0 else max(links, key=lambda x: x['fuzzyAccuracy'])
    return max_item

def main():
    CSV_FILE = 'newInput.csv'
    CSV_OUT = 'alpha.csv'
    result = []
    data = read_data_csv(CSV_FILE)
    # print(data)
    for item in data:
        email = item['email']
        first_name = item['firstName']
        last_name = item['lastName']

        print("version alpha")

        query1 = f'{last_name}@{email.split("@")[1]}'
        links = fetchProfile(query=query1, email=email, d_first_name=first_name, d_last_name=last_name)
            
        query2 = f'{first_name}@{email.split("@")[1]}'
        links2 = fetchProfile(query=query2, email=email, d_first_name=first_name, d_last_name=last_name)
        
        if links['url'] == links2['url']:
            print('MATCHED')
            result.append(links)
        else:
            print("NOT MATCHED")
            max_item = max([links, links2], key=lambda x: x['fuzzyAccuracy'])
            result.append(max_item)

    write_data_csv(csv_file=CSV_OUT, rows=result)

if __name__ == "__main__":
    main()