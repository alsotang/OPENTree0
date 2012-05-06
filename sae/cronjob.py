#! /usr/bin/env python
# coding=utf-8
import urllib2
import logging

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
            for rt in reversed(rts): 
                #print '~~~~%s~~~~' % i
                if self.forbidden_tweet(rt): #不符合转发条件的
                    continue
                try:
                    self.parse_rt(rt)
                    return True # 每次循环只转发一次就好了
                except urllib2.HTTPError:
                    continue
            return False
        
    def get_new_rts(self, rt_since_id):
        rts = self.client.statuses__mentions(since_id=rt_since_id, count=20)
        return rts

    def parse_rt(self, rt):
        self.client.post.statuses__repost(id=rt.id, status='//@%s: %s' % (rt.user.screen_name, rt.text.replace(u'''//@广西北海中学:''', '')))
        self.since_id = rt.id

    def forbidden_tweet(self, rt):
        def is_too_many_retweets(rt):
            try:
                tid = str(rt.retweeted_status.id)
            except KeyError:
                logging.debug('-'*80 + 'KeyError' + rt.text)
                tid = str(rt.id)
            #print '----%s----%s----%s' % (rt, rt.retweeted_status.id, (tid))
            times = cache.get(tid)
            if times:
                logging.info("%s: %s times %s" % (tid, times, rt.retweeted_status.text))
                if times > 20:
                    return True
                else:
                    cache.incr(tid)
            else:
                cache.set(tid, '1')
            return False

        def no_comment(rt):
            if rt.text.startswith('//'):
                return True

        if rt.user.id == 1468317623 or is_too_many_retweets(rt) or no_comment(rt): #不符合转发条件的
            return True
        else:
            return False




if __name__ == "__main__":
    c = cronjob()
    c.POST()


