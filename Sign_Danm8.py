# -*-coding:UTF-8-*-
# @Name: 耽漫吧
# @Version: 1.0.1
# @Author: Ifover
# ===============================
# cron: "0 5 0 * * *"
# const $ = new Env('耽漫吧')
# 网页登录后复制整个Cookie
# export CookieDanm8='71***; 71***; _dx_capt**d...', 多账号使用换行或&隔开
# 没什么得用，一天就20金币左右，一个资源就十几金币了
# ===============================

import requests
import random
import re
import os
import sys
import time
import datetime
from bs4 import BeautifulSoup

# 【0】只通知重要内容(如CK失效),【1】每次执行后都通知.
NOTIFY_FLAG = 0

# 回帖内容 可以自己加
REPLAY_MESSAGE = [
    '感谢楼主分享，顶贴支持～',
    '好东西啊，谢谢楼主分享',
    '绝世好文，不得不顶',
    '收藏了。谢谢楼主分享',
    '谢谢楼主分享',
]

# 下面的就别动了
TASK_NAME = "耽漫吧"
CK_NAME = "CookieDanm8"
AUTH_CK = []
NOTIFY_STR = []

ck = os.getenv(CK_NAME)
if ck:
    AUTH_CK += ck.replace("&", "\n").split("\n")


class Danm8:
    def __init__(self, index, ck):
        self.index = index
        self.condition = -1
        self.current = -1
        self.form_hash = ""
        self.user_name = ""
        self.headers = {"Cookie": ck, }
        self.session = requests.session()
        self.notify_flag = True if NOTIFY_FLAG == 1 else False

    @staticmethod
    def time(stamp="%H:%M:%S"):
        xt = datetime.now()
        return xt.strftime(stamp)

    def print(self, msg, options=None):
        if options is None:
            options = {}
        opt = {
            'print': True,
            'notify': self.notify_flag,
            'clear': False
        }
        opt.update(options)

        m = ''
        if not opt['clear']:
            if self.index:
                m += f"账号[{self.index}]"
            if self.user_name:
                m += f"[{self.user_name}]"

        msg = m + msg
        if 'time' in opt and opt['time']:
            fmt = ('fmt' in opt and opt['fmt']) or "%H:%M:%S"
            msg = f"[{self.time(fmt)}]" + msg

        opt['notify'] and NOTIFY_STR.append(msg)
        opt['print'] and print(msg)

    def query_user_info(self):
        url = "http://www.danm8-1.com/home.php"
        params = {
            "mod": "space"
        }

        try:
            res = requests.get(url, params=params, headers=self.headers)
            title_list = re.findall(r"<title>(.*)</title", res.text)
            if len(title_list) == 0:
                self.print("CK已失效", {'notify': True})
                return False
            else:
                # 获取formHash
                form_hash_list = re.findall(r"formhash=(.*)'\)", res.text)
                if len(form_hash_list) > 0:
                    self.form_hash = form_hash_list[0]

                # 获取用户名
                name_list = re.findall(r"^(.*)的个人资料", title_list[0])
                if len(name_list) > 0:
                    self.user_name = name_list[0]
                    self.print(f"登录成功")
                    return True
        except Exception as e:
            print(e)

    def query_check_info(self):
        url = "http://www.danm8-1.com/forum.php"
        try:
            res = requests.get(url, headers=self.headers)
            soup = BeautifulSoup(res.text, "html.parser")
            check_info_list = soup.select('#fx_checkin2_menu .tip_c')

            if len(check_info_list):
                self.print(check_info_list[0].text)
            else:
                self.query_check_in()

        except Exception as e:
            self.print(e, {'notify': True})

    def query_check_in(self):
        url = "http://www.danm8-1.com/plugin.php"
        params = {
            "id": "fx_checkin:checkin",
            "formhash": "5d1eb974",
            "infloat": "yes",
            "handlekey": "fx_checkin",
            "inajax": 1
        }
        try:
            res = requests.get(url, params=params, headers=self.headers)
            dialog_list = re.findall(r"showDialog\('(.*)',\s'", res.text)
            # print(dialog_list)
            if len(dialog_list) > 0:
                self.print(dialog_list[0])

        except Exception as e:
            self.print(e, {'notify': True})

    def query_yaoyaole_info(self):
        url = "http://www.danm8-1.com/plugin.php?id=yinxingfei_zzza:yinxingfei_zzza_hall&yjjs=yes"
        try:
            res = requests.get(url, headers=self.headers)
            if res.text.find('已经摇过') > -1:
                # self.print("已经摇过，明天再来看看吧")
                soup = BeautifulSoup(res.text, "html.parser")
                lis = soup.select('.zzza_hall_top_left_infor ul li')
                for i in range(1, 4):
                    text = lis[i].text.strip().split(':')
                    self.print(f'{text[0].strip()}：{text[1].strip()}')
            else:
                self.query_yaoyaole()

        except Exception as e:
            self.print(e, {'notify': True})

    def query_yaoyaole(self):
        url = "http://www.danm8-1.com/plugin.php?"
        params = {
            "id": "yinxingfei_zzza:yinxingfei_zzza_post"
        }
        data = {
            "formhash": self.form_hash
        }
        try:
            res = requests.post(url, data=data, params=params, headers=self.headers)
            if res.status_code == 200:
                delay = random.randint(10, 15)
                self.print(f'摇一摇成功，等待{delay}s')
                time.sleep(delay)
                self.query_yaoyaole_info()

        except Exception as e:
            self.print(e, {'notify': True})

    def query_home(self):
        url = "http://www.danm8-1.com/home.php"
        params = {
            "mod": "space"
        }
        flag = True
        while True:
            sleep = random.randint(35, 55)
            try:
                res = requests.get(url, params=params, headers=self.headers)
                condition_list = re.findall(r"condition.=.(\d+);", res.text)
                current_list = re.findall(r"current.=.(\d+);", res.text)
                if len(condition_list) > 0 and len(current_list) > 0:
                    self.condition = int(condition_list[0])
                    self.current = int(current_list[0])

                    times_list = re.findall(r"可领取次数：(.*)</span>", res.text)
                    if len(times_list) and flag:
                        self.print(f'可领取次数：[{times_list[0]}]')
                        flag = False

                    minute = int((int(self.condition) - int(self.current)) / 60)
                    second = (int(self.condition) - int(self.current)) % 60
                    if minute < 10:
                        minute = '0' + str(minute)
                    if second < 10:
                        second = '0' + str(second)

                    if int(self.current) > 0 and int(self.condition) > 0:
                        self.print(f'倒计时：[{minute}: {second}]，等待{sleep}s')

                    if self.current >= self.condition:
                        self.query_plugin()
                        flag = True
                else:
                    self.print('今日奖励已领完')
                    break
                    # exit_now()
            except Exception as e:
                self.print(e, {'notify': True})

            time.sleep(sleep)

            if int(self.condition) == -1:
                break

    def query_plugin(self):
        url = "http://www.danm8-1.com/plugin.php"
        params = {
            "id": "gonline:index",
            "action": "award",
            "formhash": self.form_hash
        }

        res = requests.get(url, params=params, headers=self.headers)
        show_right_list = re.findall(r"showRight\(\'(.*)\s\'\)", res.text)
        if len(show_right_list) > 0:
            self.print(show_right_list[0])

    def query_forum_42(self):
        # / reply
        fid = 42
        url = "http://www.danm8-1.com/forum-42-1.html"
        res = requests.get(url, headers=self.headers)
        soup = BeautifulSoup(res.text, "html.parser")
        t_body_list = soup.select('#moderate table tbody')
        for i in range(len(t_body_list)):
            try:
                _id = t_body_list[i]['id']
                if _id.find('normalthread') > -1:
                    _ids = _id.split('_')
                    tid = _ids[1]
                    if i == 10 or i == 20:
                        self.query_replay(fid, tid)
            except Exception as e:
                pass

    def query_replay(self, fid, tid):
        url = "http://www.danm8-1.com/forum.php"
        params = {
            "mod": "post",
            "infloat": "yes",
            "action": "reply",
            "fid": fid,
            "tid": tid,
            "replysubmit": "yes",
            "inajax": 1,
        }
        data = {
            "formhash": self.form_hash,
            "handlekey": "reply",
            "usesig": 1,
            "message": REPLAY_MESSAGE[random.randint(0, len(REPLAY_MESSAGE) - 1)]
        }
        res = requests.post(url, params=params, data=data, headers=self.headers)
        if res.text.find("回复发布成功") > -1:
            delay = random.randint(45, 60)
            self.print(f'[{tid}]回复发布成功，等待{delay}s')
            time.sleep(delay)
        else:
            self.print(f'[{tid}]回复发布失败', {'notify': True})

    def start(self):
        self.print(f"\n---------------- 账号[{self.index}] ----------------", {'clear': True})

        flag = self.query_user_info()
        if flag:
            self.print("============== 每日签到 ==============", {'clear': True})
            self.query_check_info()

            self.print("============== 每日回复 ==============", {'clear': True})
            self.query_forum_42()

            self.print("=============== 摇摇乐 ===============", {'clear': True})
            self.query_yaoyaole_info()

            self.print("============== 在线奖励 ==============", {'clear': True})
            self.query_home()


def exit_now():
    if not len(NOTIFY_STR):
        return

    print("\n============== 推送 ==============")
    NOTIFY_STR.append("\n\n本通知 By：https://github.com/Ifover/TigaScript")
    try:
        from notify import send
        if send:
            send(TASK_NAME, "\n".join(NOTIFY_STR))
    except Exception as e:
        print(f"加载通知服务失败：{e}")
    finally:
        sys.exit()


if __name__ == '__main__':
    if not AUTH_CK:
        print(f"未找到变量，请检查变量{CK_NAME}")
        sys.exit()
    print(f'共找到{len(AUTH_CK)}个账号~')
    for index, ck in enumerate(AUTH_CK):
        Danm8(index + 1, ck).start()
    exit_now()
