import pickle, time, sys, os, re, random
from bs4 import BeautifulSoup
import logging 
from telegm import ServerLogger
import requests
from urllib.request import urlretrieve 
import json

main_page = "https://www.v2ex.com"
login_page = "https://www.v2ex.com/signin"
cookie = 'cookie_v2ss.pkl'

def _log():
    logging.basicConfig(level=logging.DEBUG,
                        filename='V2EX.log',
                        format='[%(levelname)s]: [%(asctime)s]: %(message)s',
                        datefmt='%d-%b-%Y %H:%M:%S')
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('[%(levelname)s-%(asctime)s]: %(message)s')
    handler.setFormatter(formatter)
    logging.getLogger('').addHandler(handler)
    return logging


class V2ex():
    def __init__(self, username, password):
        self.s = requests.Session()
        self.headers = {'User-Agent': ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36"
                    ),
        'Origin': 'https://www.v2ex.com',
        'Referer': 'https://www.v2ex.com/signin',
        'Host': 'www.v2ex.com'
        }
        self.username = username
        self.password = password
        self.log = _log()



    def login(self):
        if os.path.exists(cookie):
            # with open(cookie, 'rb') as f:
            for c in json.load(open('cookie.json', 'r')):
                self.s.cookies.set(c['name'], c['value'])
                # self.s.cookies.update
            if 'signout' in self.s.get(main_page, headers=self.headers).text:
                self.log.info('cookie remains valid')
                return 

        soup = BeautifulSoup(self.s.get(login_page, headers=self.headers).text, 'lxml')

        userid = soup.find('input', {'placeholder':'用户名或电子邮箱地址'}).get('name')
        passid = soup.find('input', {'type':'password'}).get('name')
        capthaid = soup.find('input', {'placeholder':'请输入上图中的验证码'}).get('name')
        once = soup.find('input', {'name':'once'}).get('value')
        captcha_link = main_page + '/_captcha?once=' + once
        captcha_value = ''
            
        t = self.s.get(captcha_link, headers=self.headers)
        with open("captcha.jpg","wb") as f:
            f.write(t.content)
            f.close()

        from PIL import Image
        try:
            im = Image.open('captcha.jpg')
            im.show()
            captcha_value = input("captcha value >")                
            im.close()
        except:
            print('close failed')

        params = {userid:self.username, passid:self.password, capthaid:captcha_value, 'once':once, 'next':'/'}
        self.log.info(params)

        res = self.s.post('https://www.v2ex.com/signin', data=params, headers=self.headers)
        print(res.text)
        if 'signout' in self.s.get(main_page).text:
            self.log.info('LOGIN SUCCEED.')
            with open(cookie, 'wb') as f:
                pickle.dump(self.s.cookies, f)
        else:
            self.log.info('LOGIN FAILED.')
                
    def balance(self):
        balance = self.s.get('https://www.v2ex.com/balance', headers={'Referer': 'https://www.v2ex.com/balance'}).text
        today_gold = re.findall(r'>(\d+.+的每日.+)</span', balance)[0]
        return today_gold


    def daily(self):
        daily_url = 'https://www.v2ex.com/mission/daily'
        soup = BeautifulSoup(self.s.get(daily_url, headers=self.headers).text, 'lxml')
        u = soup.find('input', {"type": 'button'})['onclick'].split('\'')[1]
        
        sign_url = 'https://www.v2ex.com' + u    # 签到 url
        res = self.s.get(sign_url, headers={'Referer': 'https://www.v2ex.com/mission/daily'})
        des = self.balance()
        self.log.info(des)
        ServerLogger().alertGreco('v2ex 签到@' + des)
        if res.text.find(u'已成功领取每日登录奖励') > 0:
            self.log.info('小手一抖，金币到手。')
        else:
            self.log.info('已经领取过每日登录奖励。')

    def post_status(self):
        self.s.post('https://www.v2ex.com/t/mentions', data={'status': 'supreme.........'}, headers=self.headers)

if __name__ == '__main__':
    vv = V2ex('username', 'password')
    while True:
        try:
            vv.login()
            vv.daily()
        except Exception as e:
            print(e)

        time.sleep(600)



