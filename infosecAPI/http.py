import json

import requests
import logging
import sys


class api_query(requests.Request):
    
    def __init__(self, base_url, api_key, params=None, verb='get', proxies=None):
        self._api_url = base_url
        self.base_url = base_url
        self.active_url = self.base_url
        self.api_key = api_key
        self.params = params
        self.verb = verb
        self.proxies = proxies
    
    def api_query(self, params=None):
        if self.active_url is None:
            self.active_url = self.base_url
        logging.debug("proxies: %s" % self.proxies.__str__())
        my_headers = {'Authorization': 'Bearer ' + self.api_key}
        ## For testing. Uncomment the following 2 lines.
        ## Start the test server by running 'python test_server.py' from the terminal
        # full_url = "http://localhost:4001"
        # my_headers = {}
        if self.verb == "get":
            response = requests.get(self.active_url, headers=my_headers, params=params, proxies=self.proxies)
        elif self.verb == "post":
            my_headers['Content-Type']= 'application/json'
            my_headers['Accept']= 'application/json'
            params_json = json.dumps(params)
            response = requests.post(self.active_url, headers=my_headers, data=params_json, proxies=self.proxies)
        elif self.verb == "delete":
            response = requests.delete(self.active_url + '/' + params, headers=my_headers, proxies=self.proxies)
        else:
            logging.error("Invalid http verb (%s) provided" % self.verb)
            sys.exit()
        if response.status_code == 200:
            return response
        else:
            logging.error("An error occurred.\n")
            logging.error("query params: %s\n" % params.__str__())
            logging.error("url: %s" % response.url)
            logging.error("verb: %s" % self.verb)
            sys.exit("An error occurred.  Please check the log file for details.")
    
    def multi_page_request(self):
        response_list = []
        page = num_of_pages = 1
        while page <= num_of_pages:
            logging.debug("Retrieving page %s" % str(page))
            response = self.api_query(params={'page': page, 'limit': 100})
            response_dict = response.json()
            response_list.extend(response_dict["data"])
            num_of_pages = response_dict["meta"]["pageCount"]
            page += 1
        return response_list
