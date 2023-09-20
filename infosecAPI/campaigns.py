from infosecAPI.http import api_query
import logging
from infosecAPI.learners import LearnerQuery


class CampaignQuery(api_query):
    
    def __init__(self, base_url, api_key, params='', verb='get', proxies=None):
        self._api_url = base_url  # maintains the original base url in case you need it to instantiate another class
        self.base_url = base_url + "campaigns"
        self.api_key = api_key
        self.params = params
        self.verb = verb
        self.proxies = proxies
    
    def list_campaigns(self):
        self.active_url = self.base_url
        campaign_list = self.multi_page_request()
        return campaign_list
    
    def list_campaign_runs(self, campaign_id):
        self.active_url = '/'.join([self.base_url, campaign_id, 'runs'])
        campaign_run_list = self.multi_page_request()
        return campaign_run_list
    
    def get_learner_status_in_campaign_run(self, campaign_id, run_id):
        self.active_url = '/'.join([self.base_url, campaign_id, 'runs', run_id, 'learners'])
        learner_status = self.multi_page_request()
        # Get learner details
        l = LearnerQuery(self._api_url, self.api_key)
        for learner in learner_status:
            learner_details = l.get_learner_details(learner['id'])
            learner['details'] = learner_details
        return learner_status
