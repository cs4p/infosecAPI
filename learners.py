import os
import requests
import logging
from environs import Env

log = logging.Logger(__name__)

env = Env()
env.read_env()  # read .env file, if it exists
# required variables
if not os.environ["api_key"]:
    log.critical("No API key provided. Quitting.")
    exit()
else:
    api_key = os.environ["api_key"]

base_url = "https://securityiq.infosecinstitute.com/api/v2/"
my_headers = {'Authorization' : 'Bearer ' + api_key}


def list_all_users():
    user_list = []
    page = num_of_pages = 1
    while page <= num_of_pages:
        log.debug("Retrieving page %i" % page)
        response = requests.get(base_url + "learners", headers=my_headers, params={'page': page,'limit': 100 })
        response_dict = response.json()
        user_list.extend(response_dict["data"])
        num_of_pages = response_dict["meta"]["pageCount"]
        page += 1
    return user_list

    
def check_for_user(email):
    response = requests.get(base_url + "learners", headers=my_headers, params={'email': email})
    response_dict = response.json()
    if len(response_dict['data']) > 0:
        return True
    else:
        return False
    
    
def add_user(email,first_name,last_name):
    params={
        "email": email,
        "first_name": first_name,
        "last_name": last_name,
        }
    response = requests.post(base_url + "learners", headers=my_headers, params=params)
    return response.json()

