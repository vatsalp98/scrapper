/***
 * Functions used on the google App Script project.
 * 
 * ***/


/**
 * Function to create the Custom Script Menu to manually call the saveData function if needed at any point by 
 * the user.
 * @customfunction
 */
function onOpen() {
    const ui = SpreadsheetApp.getUi();
    ui.createMenu('Custom Scripts')
        .addItem('Save Data','saveData')
        .addToUi();
}
  
/**
 * Find the url of a Linkedin profile
 *
 * @param {firstName} firstName The firstName of the person
 * @param {lastName} lastName The last Name of the person
 * @param {email} email the email of the person
 * @param {company} company the company from the work email domain
 * @param {version} version Use a different combination depending on the request (1 to 6)
 * @return if found, the Link and the accuracy of the match
 * @customfunction
 */
function LINKEDINPROFILE(firstName, lastName, email, company, version) {

    const urlQuery =
        `https://curwoafr75.execute-api.ca-central-1.amazonaws.com/default/linkedInScrapper?firstName=${firstName}&lastName=${lastName}&email=${email}&version=${version}&company=${company}`;

    const response = UrlFetchApp.fetch(urlQuery);
    try {
        const res = JSON.parse(response.toString());
        item = res[0];
        return item['url'] + ";" + item['fuzzyAccuracy'];
    }
    catch (err) {
        throw new Error (err)
    }
}

/**
 * Find the url of a Linkedin profile
 * @param {email} email the email of the person
 * @return the domain registration details of the work server so we can get the organization Name
 * @customfunction
 */
function GETCOMPANYFROMDOMAIN(email) {
    const api_key = "at_kpvvON8oj5ExdJg6AgwFb3UcAvjpl";
    const url = `https://www.whoisxmlapi.com/whoisserver/WhoisService?apiKey=${api_key}&domainName=${email}&outputFormat=JSON`;
    var options = {
        'method' : 'POST',
    };
    const response = UrlFetchApp.fetch(url, options);
    try {
        const result = JSON.parse(response.getContentText());
        if (email.includes("com")){
        return result['WhoisRecord']['registrant']['organization'];
        }
        else {
        return result['WhoisRecord']['registryData']['registrant']['name'].toString();
        }
    } catch (err) {
        throw new Error(err);
    }
}

/**
 * Replace all the data on the sheet into static to avoid recalling the api endpoints if user refreshes the 
 * spreadsheet.
 * Suggested to use at the end of the session after all the profiles have been found to save them for next 
 * time.
 * @customfunction
 */
function saveData() {
    var sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("MVP");
    const lastRow = sheet.getLastRow();
    const lastCol = sheet.getLastColumn();
    const data = sheet.getRange(1,1, lastRow, lastCol).getValues();
    sheet.clearContents();
    for(let row of data){
        sheet.appendRow(row);
    }
}
  
  