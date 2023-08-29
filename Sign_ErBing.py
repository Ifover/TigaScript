# -*-coding:UTF-8-*-
# @Name: 二饼
# @Version: 1.0
# @Author: Ifover
# ===============================
# cron: "5 0 * * *"
# const $ = new Env('二饼')
# 我的主页下拉刷新获取URL https://v2.diershoubing.com/user/info
# session, remember_token, ms_session在Cookie里，auth在url地址参数里
# 其实复制整个Cookie就行, 但是后面要跟上auth, 还有别忘记加上分号分割
# export CookieErBing='session=xxx;remember_token=xxx;ms_session=xxx;auth=xxx', 多账号使用换行或&隔开
# 自用
# ===============================

import requests
import os
import sys
from datetime import datetime, timedelta

NOTIFY_FLAG = 0  # 【0】只通知重要内容(如CK失效),【1】每次执行后都通知.

# 下面的就别动了
TASK_NAME = "二饼"
CK_NAME = "CookieErBing"
AUTH_CK = []
NOTIFY_STR = []

ck = os.getenv(CK_NAME)
if ck:
    AUTH_CK += ck.replace("&", "\n").split("\n")


class ErBing:
    USER_AGENT = "erbinghd/9.58 (com.diershoubing.erbing; build:192; iOS 16.1.0) Alamofire/5.7.1"

    def __init__(self, index, ck, user_agent=USER_AGENT):
        self.index = index
        self.user_name = ''
        self.user_id = 0
        self.auth = ''
        self.session = requests.session()
        self.headers = {"Cookie": ck, "User-Agent": user_agent}
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

    def init_user_info(self):
        cks = self.headers['Cookie'].split(';')
        ck_opt = {}
        for item in cks:
            arr = item.split('=')
            if len(arr) == 2:
                key = arr[0].strip()
                ck_opt[key] = arr[1]

        check_list = ['session', 'auth', 'remember_token', 'ms_session']
        for item in check_list:
            if not (item in ck_opt):
                self.print(f'变量缺少{item}字段，请检查变量', {'notify': True})
                return False

        ck_opt['ms_remember_token'] = ck_opt['remember_token']
        # ck_opt['ms_session'] = ck_opt['session']

        self.auth = ck_opt['auth']
        d = ck_opt['remember_token'].split('|')
        if len(d) == 2:
            self.user_id = d[0]

        ck_arr = []
        for key in ck_opt:
            # if key == 'auth':
            #     continue
            ck_arr.append(f'{key}={ck_opt[key]}')
        self.headers['Cookie'] = ';'.join(ck_arr)
        return True

    def query_user_info(self):
        u = f'https://v2.diershoubing.com/user/info/v2/{self.user_id}'
        try:
            r = self.session.get(url=u, headers=self.headers)
            res = r.json()
            if res['ret'] == 0:
                self.user_name = res['info']['sname']
                self.print(f"登录成功")
            # else:
            #     self.print('登录失败，请确认ck是否过期', {'notify': True})
        except Exception as e:
            self.print(e, {'notify': True})

    def query_check_in(self):
        # Ck里有id都能签到成功 session错的都没事，
        # 反过来说至少每日签到不会失效
        u = 'https://v2.diershoubing.com/user/checkin/'
        try:
            r = self.session.get(url=u, headers=self.headers)
            res = r.json()

            if res['ret'] == 0:
                self.print(res['message'])
            elif res['ret'] == 2:
                self.print('今日已签到')
            # else:
            #     raise SystemExit
        except Exception as e:
            self.print(e, {'notify': True})

    def query_check_in_ad(self):
        u = 'https://mallapi.diershoubing.com:5000/task/video_ad_callback/?src=ios'
        d = {
            "p": "OA0fvJf7mC1zsnvuDYf7AhvYu5aTX3iozfzvcrjTJ4TP4FVOSqzC32",
            "time": 1693153081.004962
        }

        try:
            r = self.session.post(url=u, data=d, headers=self.headers)
            res = r.json()

            if res['ret'] == 0 and res['score'] > 0:
                self.print(f"观看签到视频成功，获得{res['score']}积分")
            elif res['ret'] == 0 and res['score'] == 0:
                self.print('今日已观看过签到视频')
            else:
                self.print('观看签到视频失败，msg：' + res['msg'], {'notify': True})
                return True
        except Exception as e:
            self.print(e, {'notify': True})

        return False

    def query_video_ad(self):
        u = 'https://mallapi.diershoubing.com:5000/task/video_ad_callback/?src=ios'
        d = {
            "p": "QzXHkafqzCX9S32uqXfoVuXnh5Qu2XhY8SQmcP6uwGC61CLbtrNTGx",
            "time": 1693135359.366708
        }

        try:
            r = self.session.post(url=u, data=d, headers=self.headers)
            res = r.json()

            if res['ret'] == 0 and res['score'] > 0:
                self.print(f"观看每日视频成功，获得{res['score']}积分")
            elif res['ret'] == 0 and res['score'] == 0:
                self.print('今日已观看过每日视频')
            else:
                self.print('观看每日视频失败，msg：' + res['msg'], {'notify': True})
        except Exception as e:
            self.print(e, {'notify': True})

    def query_share(self):
        u = 'https://v2.diershoubing.com/common/share_count/1/114893/?channel=wx_session'

        try:
            r = self.session.get(url=u, headers=self.headers)
            res = r.json()
            # print(res)
            if res['ret'] == 0:
                if 'msg' in res:
                    self.print(res['msg'])
                else:
                    self.print('今日已分享')
            else:
                self.print(res['message'], {'notify': True})
        except Exception as e:
            self.print(e, {'notify': True})

    def query_score(self):
        u = 'https://v2.diershoubing.com/user/score/transaction'
        p = {
            "src": "ios",
            "version": 9.58
        }

        try:
            r = self.session.get(url=u, params=p, headers=self.headers)
            res = r.json()

            day = datetime.now().day
            if res['ret'] == 0:
                transaction = res['transaction']
                for item in transaction:
                    gmt_time = datetime.strptime(item['last_update_time'], '%a, %d %b %Y %H:%M:%S GMT')
                    local_time = (gmt_time + timedelta(hours=8)).strftime("%H:%M:%S")
                    local_time_day = (gmt_time + timedelta(hours=8)).strftime("%d").strip()
                    if int(day) == int(local_time_day):
                        self.print(f"[{local_time}]{item['content']}")
        except Exception as e:
            self.print(e, {'notify': True})

    def query_status(self):
        u = 'https://mallapi.diershoubing.com:5000/task/status/'
        p = {
            "src": "ios",
            "dev_num": self.auth
        }
        try:
            r = self.session.get(url=u, params=p, headers=self.headers)
            res = r.json()

            if res['ret'] == 0:
                self.print(f"连续签到{res['check_in_con_num']}天")
                self.print(f"可用积分:{res['score']}")
        except Exception as e:
            self.print(e, {'notify': True})

    def start(self):
        self.print(f"\n---------------- 账号[{self.index}] ----------------", {'clear': True})

        if not self.init_user_info():
            return

        self.query_user_info()

        self.print("============== 每日签到 ==============", {'clear': True})
        self.query_check_in()

        self.print("============== 签到视频 ==============", {'clear': True})
        if self.query_check_in_ad():
            return

        self.print("============== 每日视频 ==============", {'clear': True})
        self.query_video_ad()

        self.print("============== 每日分享 ==============", {'clear': True})
        self.query_share()

        self.print("\n============== 今日汇总 ==============", {'clear': True})
        self.query_status()
        self.query_score()


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
        ErBing(index + 1, ck).start()
    exit_now()
