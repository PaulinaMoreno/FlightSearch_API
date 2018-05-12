# FlightSearchAPI

FlightSearchAPI works in conjunction with ScraperAPI(company API)to query each provider(e.g. "Expedia" , "Orbitz" , etc) via HTTP and   returns a merged list containing all of their results.

 The application must:
- Search all providers via HTTP
- Sorted the results by agony
- Used scraper APIs

## Requirements
* Python versions (2.x).
* Tornado [http://www.tornadoweb.org/en/stable/]
* Memcached (Memcached is a high performance multithreaded event-based key/value cache store intended to be used in a distributed system.)[https://github.com/memcached/memcached/wiki/Install]
* Python memcached (Python interface to the memcached memory cache daemon).)[https://pypi.org/project/python-memcached/]
* Download and run ScraperAPI
* Python request module (to run API_test.py)

## Run
--------
1. Clone the template project, replacing my-project with the name of the project you are creating:
    ```
    git clone https://github.com/PaulinaMoreno/FlightSearchAPI.git
    cd my-project
    ```
2. Run memcached on you OS

3. Make sure the scraper API is running 

4. Go to your directory project and type: `python flight_search_api.py`.
    1. Run on port 8000 localhost
    2. Endpoint : /flights/search
                         

## Enpoint
  ### Request
                           
  | Name            | Method        | Description   |
  | -------------   | ------------- | ------------- |
  | /flights/search |   GET         | Search for flight results for all provider, return JSON response |

  
  ### General Search Parameters
  
  | Name            | Data Type     | Required/Optional | Description   |
  | -------------   | ------------- | ------------- |------------- |
  | page |   number  | optional    | Number of page to return |
  | items |   number  | optional    | Number of items per page to return |
  
  
  Example:  
        ```
          http://localhost:8000/flights/search?page=0&items=10
          Return information of the first 10 items
        ```
        
  Example:      
        ```
         http://localhost:8000/flights/search?page=1&items=10
         Return 10 items starting from the 20th item
        ```
   
      
# Background about ScraperAPI

X has a scraper farm that we use to search our partner sites. The name scraper is a legacy holdover from when we actually scraped them. Nowadays, we query their APIs :)

For this problem, the scraper farm will be emulated by a simple HTTP server.

To start it, run `python -m searchrunner.scraperapi`. This should start a server listening on port 9000.

This server exposes exactly one endpoint:

- `GET /scrapers/<provider>` - returns flight results for the specified provider as JSON

Here are the providers that are available:

- Expedia
- Orbitz
- Priceline
- Travelocity
- United

# Testing

1. A basic test script has been included. To use it, make sure both the scraper API and your API are running then simply run `python API_test.py`.
2. I used Postman to test the API endpoint, this is my shared collection: [![Run in Postman](https://run.pstmn.io/button.svg)](https://app.getpostman.com/run-collection/65d64d4552f8f9288ee8)
  
