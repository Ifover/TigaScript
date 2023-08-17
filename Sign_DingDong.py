# -*-coding:UTF-8-*-
# @Name: 叮咚买菜
# @Version: 1.0.1
# @Author: Ifover
# ===============================
# cron: "0 5 0 * * *"
# const $ = new Env('叮咚买菜')
# 抓包获取 Cookie(有DDXQSESSID的)
# export CookieDingDong='DDXQSESSID=aaa*********aaa@DDXQSESSID=bbb*********bbb', 多账号使用换行或&隔开
# 300积分换3元（可以买30根葱）, 每天凌晨跑一次差不多了
# ===============================

import random
import requests
import os
import sys
from datetime import datetime

NOTIFY_FLAG = 0  # 【0】只通知重要内容(如CK失效),【1】每次执行后都通知.

# 下面的就别动了
TASK_NAME = "叮咚买菜"
CK_NAME = "CookieDingDong"
AUTH_CK = []
NOTIFY_STR = []

ck = os.getenv(CK_NAME)
if ck:
    AUTH_CK += ck.replace("&", "\n").split("\n")


class DingDong:
    USER_AGENT = "Mozilla/5.0 (iPhone; CPU iPhone OS 16_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 xzone/10.3.0"

    def __init__(self, index, ck, user_agent=USER_AGENT):
        self.index = index
        self.user_name = ''
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

    def query_user_info(self):
        url = 'https://maicai.api.ddxq.mobi/user/info'
        params = {
            "station_id": ''.join(random.choice('0123456789abcdef') for _ in range(24)),
        }

        res = self.session.get(url, params=params, headers=self.headers)
        res_data = res.json()
        if res_data['code'] == 0:
            self.user_name = res_data['data']['name']
            self.print(f"登录成功")
            return True
        else:
            self.user_name = ''
            self.print(res_data['msg'], {'notify': True})
            return False

    def query_check_in(self):
        url = 'https://sunquan.api.ddxq.mobi/api/v2/user/signin/'
        res = self.session.post(url, headers=self.headers)
        res_data = res.json()

        point_info = self.query_point()
        point_num = point_info['point_num'] if point_info else 'ERROR'
        expire_point = point_info['expire_point_display'] if point_info else 'ERROR'

        if res_data['code'] == 0:
            self.print(f"获得积分：{res_data['data']['point']}个")
            self.print(f"总积分：{point_num}个")
            self.print(f"已连续签到：{res_data['data']['sign_series']}天")
            self.print(expire_point)
        else:
            self.user_name = ''
            self.print(res_data['msg'], {'notify': True})

    def query_point(self):
        url = 'https://maicai.api.ddxq.mobi/point/home'
        params = {
            "station_id": ''.join(random.choice('0123456789abcdef') for _ in range(24)),
        }

        res = self.session.get(url, params=params, headers=self.headers)
        res_data = res.json()
        if res_data['code'] == 0:
            return res_data['data']
        else:
            return False

    def start(self):
        self.print(f"\n---------------- 账号[{self.index}] ----------------", {'clear': True})
        if self.query_user_info():
            self.print("============== 每日签到 ==============", {'clear': True})
            self.query_check_in()


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
        DingDong(index + 1, ck).start()
    exit_now()
