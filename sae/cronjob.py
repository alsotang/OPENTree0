#! /usr/bin/env python
# coding=utf-8
from weibo1 import APIClient, OAuthToken

from framework import cache
from framework import db

from config import APP_KEY, APP_SECRET


class cronjob():
    def POST(self):
        for i in db.select('account_info'):
            client = APIClient(app_key=APP_KEY, app_secret=APP_SECRET, token=OAuthToken(oauth_token=i.oauth_token, oauth_token_secret=i.oauth_token_secret))
            self.process_new_dms(client, i.dm_since_id)

    # 处理新私信的函数
    def process_new_dms(self, client, dm_since_id):
        dms = self.get_new_dms(client, dm_since_id)
        for i in dms:
            self.parse_dm(i.text)
        return 
        
    def get_new_dms(self, client, dm_since_id):
        dms = client.direct_messages()
        return dms

    def parse_dm(self, dm_text):
        print dm_text




    def handle_new_replys(self):
        pass

    def handle_new_rebos(self):
        pass
    
if __name__ == "__main__":
    c = cronjob()
    c.POST()


