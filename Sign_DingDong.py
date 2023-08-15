# -*-coding:UTF-8-*-
# -*- coding: utf-8 -*-
# @Name: 叮咚买菜
# @Version: 1.0
# @Author: Ifover
# ===============================
# cron: "0 5 0 * * *"
# const $ = new Env('叮咚买菜')
# 抓包获取 Cookie(有DDXQSESSID的)
# export CookieDingDong='DDXQSESSID=aaa*********aaa@DDXQSESSID=bbb*********bbb', #多账号使用&或@隔开
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
    AUTH_CK += ck.replace("@", "&").split("&")


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

    def getUserInfo(self):
        url = 'https://maicai.api.ddxq.mobi/user/info'
        params = {
            "station_id": ''.join(random.choice('0123456789abcdef') for _ in range(24)),
        }

        res = self.session.get(url, params=params, headers=self.headers)
        resData = res.json()
        if resData['code'] == 0:
            self.user_name = resData['data']['name']
            self.print(f"登录成功")
            return True
        else:
            self.user_name = ''
            self.print(resData['msg'], {'notify': True})
            return False

    def queryCheckIn(self):
        url = 'https://sunquan.api.ddxq.mobi/api/v2/user/signin/'
        res = self.session.post(url, headers=self.headers)
        resData = res.json()

        pointInfo = self.queryPoint()
        pointNum = pointInfo['point_num'] if pointInfo else 'ERROR'
        expirePoint = pointInfo['expire_point_display'] if pointInfo else 'ERROR'

        if resData['code'] == 0:
            self.print(f"获得积分：{resData['data']['point']}个")
            self.print(f"总积分：{pointNum}个")
            self.print(f"已连续签到：{resData['data']['sign_series']}天")
            self.print(expirePoint)
        else:
            self.user_name = ''
            self.print(resData['msg'], {'notify': True})

    def queryPoint(self):
        url = 'https://maicai.api.ddxq.mobi/point/home'
        params = {
            "station_id": ''.join(random.choice('0123456789abcdef') for _ in range(24)),
        }

        res = self.session.get(url, params=params, headers=self.headers)
        resData = res.json()
        if resData['code'] == 0:
            return resData['data']
        else:
            return False

    def start(self):
        self.print(f"---------------- 账号[{self.index}] ----------------", {'clear': True})
        if self.getUserInfo():
            self.print("============== 每日签到 ==============", {'clear': True})
            self.queryCheckIn()


def exit_now():
    if not len(NOTIFY_STR):
        return

    print("\n============== 推送 ==============")
    NOTIFY_STR.append("\n\n本通知 By：https://github.com/Ifover/TigaScript")
    from notify import send
    if send:
        send(TASK_NAME, "\n".join(NOTIFY_STR))
    sys.exit()


if __name__ == '__main__':
    if not AUTH_CK:
        print(f"未找到变量，请检查变量{CK_NAME}")
        sys.exit()
    print(f'共找到{len(AUTH_CK)}个账号~\n')
    for index, ck in enumerate(AUTH_CK):
        DingDong(index + 1, ck).start()
    exit_now()
