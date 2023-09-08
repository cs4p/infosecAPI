import os
import requests
import logging
from environs import Env
import csv

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
my_headers = {'Authorization': 'Bearer ' + api_key}


def list_all_learner_emails():
    learner_list = []
    page = num_of_pages = 1
    while page <= num_of_pages:
        log.debug("Retrieving page %i" % page)
        response = requests.get(base_url + "learners", headers=my_headers, params={'page': page, 'limit': 100})
        response_dict = response.json()
        for learner in response_dict["data"]:
            learner_list.append({"email":learner["email"],"first_name":learner["first_name"],"last_name":learner["last_name"]})
        num_of_pages = response_dict["meta"]["pageCount"]
        page += 1
    return learner_list


def check_for_learner_by_email(email):
    response = requests.get(base_url + "learners", headers=my_headers, params={'email': email})
    response_dict = response.json()
    if len(response_dict['data']) > 0:
        return True
    else:
        return False


def get_learner_id_by_email(email):
    response = requests.get(base_url + "learners", headers=my_headers, params={'email': email})
    response_dict = response.json()
    if len(response_dict['data']) > 0:
        return response_dict['data']["id"]
    else:
        return False


def add_learner(params):
    response = requests.post(base_url + "learners", headers=my_headers, params=params)
    return response.json()


def delete_learner(id):
    params = {"id": id}
    response = requests.delete(base_url + "learners", headers=my_headers, params=params)
    return response.json()


def import_ad_users(user_file):
    """
    accepts a csv file generated from your AD and syncs your learner list with it.  Here is a sample AD command to create the file
    Get-ADUser -Filter * -Properties * -SearchBase "OU=OMB,OU=User Accounts,DC=login,DC=omb,DC=gov" | Select @{Name = 'first_name'; Expression = {$_.GivenName}},@{Name = 'last_name'; Expression = {$_.sn}},@{Name = 'email'; Expression = {$_.extensionAttribute3}},@{Name = 'group'; Expression = {"OMB_ALL"}},@{Name = 'title'; Expression = {$_.Title}},@{Name = 'department'; Expression = {$_.Office}},@{Name = 'phone'; Expression = {$_.mobile}},@{Name = 'address1'; Expression = {$_.Division}},@{Name = 'address2'; Expression = {""}},@{Name = 'city'; Expression = {$_.l}},@{Name = 'state'; Expression = {$_.State}},@{Name = 'zip'; Expression = {$_.PostalCode}},@{Name = 'country'; Expression = {$_.Country}},@{Name = 'custom'; Expression = {$_.employeeType}},@{Name = 'manager_name'; Expression = {(get-aduser -property Name $_.manager).Name}},@{Name = 'manager_email'; Expression = {(get-aduser -property extensionattribute3 $_.manager).extensionattribute3}} | ConvertTo-Csv -Delimiter ',' -NoTypeInformation | ForEach-Object -MemberName Replace -ArgumentList '"','' | Set-Content "C:\scripts\InfoSec-Institute\Infosec IQ - CSV to IQ Sync version 1.0.3\Scheduled_CSV\Scheduled_CSV.csv
    :param user_file: location of the csv file
    """
    with open(user_file, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        ad_user_list = []
        for row in reader:
            # check to see if the user exists
            ad_user_list.append({"email": row["email"], "first_name": row["first_name"], "last_name": row["last_name"]})
        return ad_user_list


def sync_ad_with_learners(user_file):
    # Check for users to delete
    learners_list = list_all_learner_emails()
    ad_user_list = import_ad_users(user_file)
    # find learners to add
    add_learners = list(set(ad_user_list) - set(learners_list))
    # find learners to delete
    delete_learners = list(set(learners_list) - set(ad_user_list))
    for learner in delete_learners:
        learner_id = get_learner_id_by_email(learner)
        if learner_id:
            delete_learner(learner_id)
        else:
            log.critical("Learner with email %s not found" % learner)
    for learner in add_learners:
        params = {
            "email": learner["email"],
            "first_name": learner["first_name"],
            "last_name": learner["last_name"],
            }
        add_learner(params)
