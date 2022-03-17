# Vatglobal Developer Assignment

##  Task

Create a Django based API using the Django REST Framework to allow a user to upload a data file for processing, and to retrieve a list of processed rows. 

The application should expose the two following endpoints: 

### processFile – POST
- Accepts a CSV file
- For each row, validate each of the cell values (date, country, purchase or sale, currency, net and input amounts) so that they are of the correct datatype and format. 
- Store the results of each row in an appropriate data structure. Each cell value should be converted such that the data can be queried in a consistent manner. Be sure to select appropriate data types for each cell value type.
- Only rows for the year of 2020 should be stored.

### retrieveRows – GET
- Takes three query parameters
	- country (ISO 3166 code)
	- date (YYYY/MM/DD)
	- currency (optional) (ISO 4217 code)
- Returns a JSON response containing the rows based on the correct country and date. If the currency is passed in, convert the stored currency to the requested currency by fetching the required rate(s) (if available) from the European Central Bank [https://sdw-wsrest.ecb.europa.eu/help/](https://sdw-wsrest.ecb.europa.eu/help/) 
- Please design this endpoint to scale as gently as possible with the bank API. Please document steps taken towards this goal in the repositories’ README file.
Use query parameters as follows to perform a query: 
```
/retrieveRows?country=DE&date=2020/08/05&currency=GBP
```

### Test data

Use the sample transactions in the test-data folder to validate your solution.


### Scalability

The test data set only includes around 1000 transactions. How would you go about scaling your solution to millions of records?

In the README file, briefly describe how you would build a scalable solution for ingesting very large data sets to ensure reliable and timely processing of the data. Please mention any limitations to your solution.


### Other considerations:
- Use Python 3.9 and Django 4 for this exercise
- Use your choice of dependency management.
- Implement unit tests and comments where appropriate.
- Provide any information needed to run locally in the EADME file of the repository and a .env file location if we need to run migrations etc.
- Please send us a way to view the code: GitHub, Bitbucket, etc.
- Please complete this task within a week of receiving. If you need more time, please let us know.



