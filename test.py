from infosecAPI.campaigns import CampaignQuery
from infosecAPI.learners import LearnerQuery

c = CampaignQuery('https://securityiq.infosecinstitute.com/api/v2/', 'f4921520-f509-436c-a103-48ae79952113')
campaign_list = c.list_campaigns()
campaign_run_list = c.list_campaign_runs('n5YQ')
campaign_id=campaign_list[0]['id']
run_id=campaign_run_list[0]['id']
learner_status = c.get_learner_status_in_campaign_run(campaign_id, run_id)

l = LearnerQuery(c._api_url, c.api_key)
learner_status = c.get_learner_status_in_campaign_run(campaign_id, run_id)
for learner in learner_status:
    if learner['status'] != 'completed':
        print('Learner %s has not completed the campaign' % ' '.join([learner['details']['first_name'], learner['details']['last_name']]))
