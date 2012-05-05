#! /usr/bin/env python
# coding=utf-8
from weibo1 import APIClient, OAuthToken

from framework import cache
from framework import db

from config import APP_KEY, APP_SECRET


class cronjob():
    def POST(self):
        for i in db.select('account_info'):
            self.client = APIClient(app_key=APP_KEY, app_secret=APP_SECRET, token=OAuthToken(oauth_token=i.oauth_token, oauth_token_secret=i.oauth_token_secret))
            if self.process_new_rts(i.rt_since_id):
                db.update('account_info', where = 'id = %s' % i.id, rt_since_id = self.since_id)
        

    # 处理新转发(retweet)的函数
    def process_new_rts(self, rt_since_id):
        rts = self.get_new_rts(rt_since_id)
        if not rts:
            return False
        else:
            for i in reversed(rts): 
                if i.user.id == 1468317623:
                    continue
                self.parse_rt(i)
                return True # 每次循环只转发一次就好了
            return False
        
    def get_new_rts(self, rt_since_id):
        rts = self.client.statuses__mentions(since_id=rt_since_id, count=20)
        return rts

    def parse_rt(self, rt):
        self.client.post.statuses__repost(id=rt.id, status='//@%s: %s' % (rt.user.screen_name, rt.text.replace(u'''//@广西北海中学: ''', '')))
        self.since_id = rt.id


if __name__ == "__main__":
    c = cronjob()
    c.POST()


