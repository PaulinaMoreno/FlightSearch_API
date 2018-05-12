import json
import operator
import memcache
from tornado import gen, ioloop, web, httpserver, httpclient
from tornado.httpclient import AsyncHTTPClient, HTTPClient

# memcached Client host = 127.0.0.1 port=11211
mc = memcache.Client(['127.0.0.1:11211'], debug=0)
# Providers flights List
providers_list = ['Orbitz', 'Expedia', 'Priceline', 'Travelocity', 'United']
# Scraper API url
url_scraperapi = "http://localhost:9000/scrapers/"

'''
Pagination class is used to paginate the results to make
responses easier to handle, the result of a request could be a massive 
response with hundreds of thousands of fligths.
'''


class Pagination:

    def __init__(self, page, items, total_fligths):
        """
        __init__ Pagination method

        Args:
           page (int): Number of page
           items (int): Items per page
           total_fligths (int): Total of flights in the response
        """
        self.page = page
        self.items = items
        self.total_fligths = total_fligths

    def get_startIndex(self):
        """
            Get start index for pagination process
            if page argument no given, the start index is equal to 0
            else, start index is equal to page * items per page

            Returns:
                int. start index for pagination
        """
        if self.page == -1:
            return 0
        else:
            if self.page * self.items >= self.total_fligths:
                return self.total_fligths
            else:
                return self.page * self.items

    def get_endIndex(self, startIndex):
        """
            Get last index for pagination process
            if page >=0, the last index is equal to star index + items per page
            else, last index is equal to total of flights in the response

            Args:
               startIndex (int): Start index pagination
            Returns:
                int. last index for pagination
        """
        if self.page == -1:
            return self.total_fligths
        else:
            if startIndex + self.items >= self.total_fligths:
                return self.total_fligths
            else:
                return startIndex + self.items


class FlightSearchApiHandler(web.RequestHandler):
    SUPPORTED_METHODS = ("GET")   # support for GET only
    
    @gen.coroutine
    def get(self):
        """
            Tornado coroutine, asynchronous get method to retrieve 
            ScraperAPI information using pythom memcached to avoid 
            recomputing data to provide a great performance,
            this cache store the flights information of all providers.

            The cache could store information about Pagination but not 
            implemented for simplicity

            Query parameters:
                page: number of page ,
                e.g.: http://localhost:8888/flights/search?page=1
                items : number of items per page,
                e.g.: http://localhost:8888/flights/search?page=1&items=10

        """
        # Verify for page and items query arguments
        n_page = self.get_argument('page', -1)   # if no given page , set default value to -1
        items = self.get_argument('items', 20)   # if no given items , set default value to 20
        # Ask for memcache data
        mc_results = mc.get('allFligthsData')
        startIndex = 0
        endIndex = 0
        # If memcache is empty , request information from ScraperAPI
        if mc_results is None:
           
            # urls list of each provider, e.g.: [http://localhost:9000/scrapers/<provide1>,http://localhost:9000/scrapers/<provide2>,...]
            urls = []
            for provider in providers_list:
                # Append to urls list, e.g: "http://localhost:9000/scrapers/" + "United" -> http://localhost:9000/scrapers/United
                    urls.append(url_scraperapi + provider)
            """
            Waits for all the Futures in parallel, the coroutine yielding the entire list
            until the results from the request are available.
            """
            futures_list = []
            for url in urls:
                futures_list.append(self.url_get(url))
            yield futures_list
            """
            We need to merge the information from all the Futures retrieved, we need to iterate to the **futures_list**
            and save the data per Future in **results_list**, then we need to sort the list by agony

            """
            results_list = []

            for future in futures_list:
                results_list.extend(future.result())
            results_list = sorted(results_list, key=lambda k: k['agony'])
            # Total of flights in results_list
            total_fligths = len(results_list)
            """
            Create a Pagination object and get the start and end index for pagination
            if page parameter was not specified, then we just retrieve informatiion from
            ***results_list*** from index 0 to total of elements in the list
            """
            page = Pagination(int(n_page), int(items), total_fligths)
            startIndex = page.get_startIndex()
            endIndex = page.get_endIndex(startIndex)
            """
            Set allFligthsData into memcache, 180 value: expiration time in seconds for the key in memcache
            You could change this value for testing
            """
            mc.set("allFligthsData", results_list, 180)
            json_result = json.dumps({'results': [result for result in results_list[startIndex:endIndex]]})
        # Get memcache information
        else:
            """
            Information already in memcache

            Create a Pagination object and get the start and end index for pagination
            if page parameter was not specified, then we just retrieve informatiion from
            ***results_list*** from index 0 to total of elements in the ***memcache***
            """
            page = Pagination(int(n_page), int(items), len(mc_results))
            startIndex = page.get_startIndex()
            endIndex = page.get_endIndex(startIndex)
            # mc_results cache
            json_result = json.dumps({'results': [result for result in mc_results[startIndex:endIndex]]})
        self.write(json_result)
        self.set_status(200)
        self.finish()

    @gen.coroutine
    def url_get(self, url):
        """
            Fetch an url
            Args:
               url (str): API Url + provider,
               e.g.:"http://localhost:9000/scrapers/" + "United" -> http://localhost:9000/scrapers/United
            Returns:
                Flight information of the provider
        """
        request = AsyncHTTPClient()
        resp = yield request.fetch(url)
        results = json.loads(resp.body)
        results_list = []
        for result in results['results']:
            results_list.append(result)
        raise gen.Return(results_list)

application = web.Application([
         (r"/flights/search", FlightSearchApiHandler),

], debug=True)


if __name__ == "__main__":
    port = 8000

    print("Listening at port {0}".format(port))
    application.listen(port)
    ioloop.IOLoop.instance().start()
