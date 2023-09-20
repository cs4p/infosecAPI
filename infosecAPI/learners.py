import logging
import csv
from infosecAPI.http import api_query


class LearnerQuery(api_query):
    def __init__(self, base_url, api_key, params='', verb='get', proxies=None):
            self._api_url = base_url
            self.base_url = base_url + "learners"
            self.active_url = self.base_url
            self.api_key = api_key
            self.params = params
            self.verb = verb
            self.proxies = proxies
            
    def list_all_learners(self):
        logging.debug("proxies: %s" % self.proxies.__str__())
        learner_list = []
        learner_list_email = []
        page = num_of_pages = 1
        while page <= num_of_pages:
            logging.debug("Retrieving page %s" % str(page))
            response = self.api_query(params={'page': page, 'limit': 100})
            response_dict = response.json()
            for learner in response_dict["data"]:
                learner_list.append({"email": learner["email"], "first_name": learner["first_name"], "last_name": learner["last_name"]})
                learner_list_email.append(learner["email"])
            num_of_pages = response_dict["meta"]["pageCount"]
            page += 1
        return learner_list, learner_list_email
    
    def get_learner_details(self, learner_id):
        self.active_url = '/'.join([self.base_url, learner_id])
        response = self.api_query()
        return response.json()
    
    def get_learner_id_by_email(self, email):
        logging.debug("Checking for leaner with email %s" % email)
        response = self.api_query(params={'email': email})
        response_dict = response.json()
        if len(response_dict['data']) > 0:
            logging.debug("Found leaner with email %s" % email)
            return response_dict['data'][0]["id"]
        else:
            logging.debug("No learner found with email %s" % email)
            return False
    
    def add_learner(self, params):
        user_properties = params.__str__()
        logging.debug("Adding leaner with properties %s" % user_properties)
        response = self.api_query(params=params, verb="post")
        return response.json()
    
    def delete_learner(self, id):
        logging.debug("Deleting leaner with ID %s" % id)
        response = self.api_query(params=id, verb="delete")
        return response.json()
    
    def import_ad_users(self, user_file):
        """
        accepts a csv file generated from your AD and syncs your learner list with it.  Here is a sample AD command to create the file
        Get-ADUser -Filter * -Properties * -SearchBase "OU=OMB,OU=User Accounts,DC=login,DC=omb,DC=gov" | Select @{Name = 'first_name'; Expression = {$_.GivenName}},@{Name = 'last_name'; Expression = {$_.sn}},@{Name = 'email'; Expression = {$_.extensionAttribute3}},@{Name = 'group'; Expression = {"OMB_ALL"}},@{Name = 'title'; Expression = {$_.Title}},@{Name = 'department'; Expression = {$_.Office}},@{Name = 'phone'; Expression = {$_.mobile}},@{Name = 'address1'; Expression = {$_.Division}},@{Name = 'address2'; Expression = {""}},@{Name = 'city'; Expression = {$_.l}},@{Name = 'state'; Expression = {$_.State}},@{Name = 'zip'; Expression = {$_.PostalCode}},@{Name = 'country'; Expression = {$_.Country}},@{Name = 'custom'; Expression = {$_.employeeType}},@{Name = 'manager_name'; Expression = {(get-aduser -property Name $_.manager).Name}},@{Name = 'manager_email'; Expression = {(get-aduser -property extensionattribute3 $_.manager).extensionattribute3}} | ConvertTo-Csv -Delimiter ',' -NoTypeInformation | ForEach-Object -MemberName Replace -ArgumentList '"','' | Set-Content "C:\scripts\InfoSec-Institute\Infosec IQ - CSV to IQ Sync version 1.0.3\Scheduled_CSV\Scheduled_CSV.csv
        :param user_file: location of the csv file
        """
        logging.debug("Attempting to import file %s" % user_file)
        with open(user_file, newline='', encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile)
            ad_user_list = []
            ad_user_list_email = []
            for row in reader:
                if row["email"].strip() != '':
                    ad_user_list.append({"email": row["email"], "first_name": row["first_name"], "last_name": row["last_name"]})
                    ad_user_list_email.append(row["email"])
            logging.debug("%s imported successfully." % user_file)
            return ad_user_list, ad_user_list_email
    
    def sync_ad_with_learners(self,user_file):
        logging.info("Starting AD sync...")
        logging.debug("proxies: %s" % self.proxies.__str__())
        # Check for users to delete
        _ , learners_list_email = self.list_all_learners()
        ad_user_list, ad_user_list_email = self.import_ad_users(user_file)
        # find learners to add
        add_learners = list(set(ad_user_list_email) - set(learners_list_email))
        logging.info("Found %s users to add." % len(add_learners))
        # find learners to delete
        delete_learners = list(set(learners_list_email) - set(ad_user_list_email))
        logging.info("Found %s users to delete." % len(delete_learners))
        # Delete users
        logging.info("Deleting users...")
        for learner in delete_learners:
            learner_id = self.get_learner_id_by_email(learner)
            if learner_id:
                self.delete_learner(learner_id)
                logging.info("Learner with email %s deleted" % learner)
            else:
                logging.critical("Learner with email %s not found" % learner)
        # Add users
        logging.info("Adding users...")
        for learner in add_learners:
            if learner.split('@')[1] == 'omb.eop.gov':
                for user in ad_user_list:
                    if user['email'] == learner:
                        params = {"email": user["email"], "first_name": user["first_name"], "last_name": user["last_name"]}
                        self.add_learner(params)
                        logging.info("Learner with email %s added" % learner)
            else:
                logging.warning("Learner %s is not a valid email address" % learner)
        logging.info("Sync complete.")
