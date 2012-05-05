#! /usr/bin/env python
# coding=utf-8
'''
#=============================================================================
#     FileName: urls.py
#         Desc: 各个url的配置。
#       Author: Alsotang
#        Email: alsotang@gmail.com
#     HomePage: http://tangzhan.li
#      Version: 0.0.1
#   LastChange: 2012-03-15 13:21:32
#      History:
#=============================================================================
'''
from datetime import datetime
import logging
import os
from urllib2 import HTTPError

import web

from weibo1 import APIClient, OAuthToken

from config import APP_KEY, APP_SECRET, LOGIN_URL, CALLBACK_URL
from framework import cache, db
from cronjob import cronjob # 在urls变量里面已经使用

urls = (
    r'/',      'index',
    r'/index', 'index',
    r'/login', 'login',
    #r'/logout', 'logout',
    r'/callback', 'callback', 
    r'/success', 'success',
    r'/backend/cronjob', 'cronjob', 
)

app_root = os.path.dirname(__file__)
templates_root = os.path.join(app_root, 'templates')
render = web.template.render('templates') #, base='base', globals=t_globals)

class index():
    def GET(self):
        return render.index(LOGIN_URL)

class login():
    def GET(self):
        client = APIClient(app_key=APP_KEY, app_secret=APP_SECRET, callback=CALLBACK_URL)
        request_token = client.get_request_token()
        # 保存request_token:
        self.save_request_token(request_token.oauth_token, request_token.oauth_token_secret)
        url = client.get_authorize_url(request_token.oauth_token)
        # redirect to url
        raise web.found(url)
    def save_request_token(self, token, secret):
        # cache them, but first calculate expires time:
        now = datetime.now()
        t = datetime(now.year, now.month, now.day)
        delta = now - t
        exp = 86400 - delta.seconds # makes it expires in midnight (24:00)
        if exp > 3600:
            exp = 3600
        logging.info('fetched and cache for %d seconds.' % exp)
        cache.set(token, secret, exp)


#class logout():
#    def GET(self):
#        web.setcookie('weibouser', 'x', expires=-1)
#        raise web.found('/index')

class callback():
    def GET(self):
        # 获取URL参数:
        oauth_token = web.input().get('oauth_token')
        oauth_verifier = web.input().get('oauth_verifier')
        # 使用oauth_token查表获取上一步保存的oauth_token_secret：
        oauth_token_secret = cache.get(oauth_token.encode('ascii'))
        # 构造完整的request token：
        request_token = OAuthToken(oauth_token, oauth_token_secret, oauth_verifier)
        # 用request token获取access token：
        client = APIClient(app_key=APP_KEY, app_secret=APP_SECRET, token=request_token)
        access_token = client.get_access_token()
        # 通过access token调用一个API获取用户uid信息：
        client = APIClient(APP_KEY, APP_SECRET, access_token)
        account = client.account__verify_credentials()
        uid = str(account.id)
        # 保存uid和access token以后使用：
        self.save_access_token_to_db(uid, access_token.oauth_token, access_token.oauth_token_secret) 
        try:
            # 发表一条授权成功的微博
            client.post.statuses__update(status="本微博帐号已成为一个基于OPENTree0应用的树洞，欢迎大家来此吐槽生活。树洞的使用方法请见OPENTree0主页：http://opentree0.sinaapp.com/")
        except HTTPError:
            logging.error("重复发送微博。")
        raise web.found('/success')


    def save_access_token_to_db(self, uid, token, secret):
        kw = dict(oauth_token=token, oauth_token_secret=secret, join_time=str(datetime.now()))
        # check for update:
        if 0==db.update('account_info', where='user_id=$user_id', vars=dict(user_id=uid), **kw):
            db.insert('account_info', user_id=uid, oauth_token=token, oauth_token_secret=secret)
class success():
    def GET(self):
        return render.success()

app = web.application(urls, globals())

if __name__ == "__main__":
    app.run()
