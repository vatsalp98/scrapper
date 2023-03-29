# Scrapping scripts for LinkedIN Profile from Emails

## Replacing the API key and Search Engine ID

Get your API_KEY of a google cloud project from here
- [Google Cloud API Key](https://console.cloud.google.com/apis/credentials)
 - [Custom Google Search Engine ID](https://programmablesearchengine.google.com/controlpanel/all)


## Required Packages

`python-dotenv` and `requests` are needed for the script to fun properly and normally.

## Input File

- Create a `input.csv` file with a single row of all the emails to run the script on

## Output File

- The script will generate `output.csv` with all the results compiled together from the link to the title of the individual.

## Google Function

Copy and paste the `googleSheetFunc.js` file into the google sheet appsheets functions space and then you can easily call the same method using a cell in google sheets.

