#coding: utf8

import re
import time
from urlparse import parse_qsl, urljoin

from urlfetch import *

URL_LOGIN = 'http://3g.sina.com.cn/prog/wapsite/sso/login_submit.php'
TIME_SLEEP = 1 # sec

class Sina(object):

    def __init__(self, username, password):
        self.cookies = None
        self.username = username
        self.password = password

    def login(self):
        response = fetch(URL_LOGIN)
        data = response.body

        vk = re.search(r'''name="vk"\s+?value="(.*?)"''', data).group(1)
        pname = re.search(r'''name="password_(\d+)"''', data).group(1)

        post = {
            'mobile': self.username,
            'password_'+pname: self.password,
            #'capId': capid,
            'vk': vk,
            'remember': 'on',
            'submit': '1'
        }
        response = fetch(URL_LOGIN, data=post)
        data = response.body
        captcha = re.search(r'''captcha/show.php\?cpt=(\w+)''', data)
        if captcha:
            url = '''http://weibo.cn/interface/f/ttt/captcha/show.php?cpt=''' + captcha.group(1)
            print url
            captcha = raw_input("open the url and input the captcha:")
            vk = re.search(r'''name="vk"\s+?value="(.*?)"''', data).group(1)
            pname = re.search(r'''name="password_(\d+)"''', data).group(1)
            capid = re.search(r'''name="capId"\s+?value="(.*?)"''', data).group(1)
            post = {
                'mobile': self.username,
                'password_'+pname: self.password,
                'capId': capid,
                'vk': vk,
                'remember': 'on',
                'submit': '1',
                'code': captcha.strip(),
            }
            response = fetch(URL_LOGIN, data=post)
        self.cookies = response.cookiestring
        print self.cookies
        response = fetch(
            'http://weibo.cn/',
            headers = {'Cookie': self.cookies, 'User-Agent': 'Android'},
        )
        self.uid = re.search(r'''uid=(\d+)''', response.body).group(1)
        print self.uid
        return self.cookies

    def del_tweets(self):
        while True:
            time.sleep(2 * TIME_SLEEP)
            response = fetch(
                'http://weibo.cn/%s/profile' % self.uid,
                headers={'Cookie': self.cookies}
            )
            data = re.findall(r'href="http://weibo.cn/mblog/del\?(.*?)"', response.body)
            if not data:
                break
            for i in data:
                time.sleep(TIME_SLEEP)
                j = parse_qsl(i)
                qs = dict(j)
                qs['act'] = 'delc'
                qs = '&'.join(['='.join(k) for k in qs.items()])
                url = 'http://weibo.cn/mblog/del?' + qs
                try:
                    fetch(
                        url,
                        headers = {'Cookie': self.cookies}
                    )
                    print url
                except:pass

    def unfollow(self):
        while True:
            time.sleep(2 * TIME_SLEEP)
            response = fetch(
                'http://weibo.cn/%s/follow' % self.uid,
                headers={'Cookie': self.cookies}
            )

            data = re.findall(r'href="/attention/del\?(.*?)"', response.body)
            if not data:
                break
            for i in data:
                time.sleep(TIME_SLEEP)
                j = parse_qsl(i)
                qs = dict(j)
                qs['act'] = 'delc'
                qs = '&'.join(['='.join(k) for k in qs.items()])
                url = 'http://weibo.cn/attention/del?' + qs
                try:
                    fetch(
                        url,
                        headers = {'Cookie': self.cookies}
                    )
                    print url
                except:pass

    def remove_followers(self, black=False):
        while True:
            time.sleep(2 * TIME_SLEEP)
            response = fetch(
                'http://weibo.cn/%s/fans' % self.uid,
                headers={'Cookie': self.cookies}
            )

            data = re.findall(r'href="/attention/remove\?(.*?)"', response.body)
            if not data:
                break
            for i in data:
                time.sleep(TIME_SLEEP)
                j = parse_qsl(i)
                qs = dict(j)
                qs['act'] = 'removec'
                if black:
                    qs['black'] = 1
                qs = '&'.join(['='.join(k) for k in qs.items()])
                url = 'http://weibo.cn/attention/remove?' + qs
                try:
                    fetch(
                        url,
                        headers = {'Cookie': self.cookies}
                    )
                    print url
                except:pass

if __name__ == '__main__':
    def sigint():
        def _sigint(a,b):
            print a, b
            import os, sys
            os.kill(0, signal.SIGTERM)
            sys.exit()
        import signal
        signal.signal(signal.SIGINT, _sigint)
    import sys
    sigint()
    username, password = sys.argv[1:]
    sina = Sina(username, password)
    sina.login()
    sina.del_tweets()
    #sina.unfollow()
    #sina.remove_followers()
