# -*-coding:UTF-8-*-
# @Name: 雷神加速器
# @Version: 1.0
# @Author: Ifover
# ===============================
# cron: "0 4 * * *"
# const $ = new Env('雷神加速器')
# 抓包获取 token
# export TokenLeiGod='s*asdasd*asd*****a@b***********bbb', 多账号使用换行或&隔开
# 防止某人用完不关浪费时间，定个时间自动关闭
# ===============================

import requests
import os
import sys
from datetime import datetime

NOTIFY_FLAG = 0  # 【0】只通知重要内容(如CK失效),【1】每次执行后都通知.

# 下面的就别动了
TASK_NAME = "雷神加速器"
CK_NAME = "TokenLeiGod"
AUTH_CK = []
NOTIFY_STR = []
session = requests.session()

ck = os.getenv(CK_NAME)
if ck:
    AUTH_CK += ck.replace("&", "\n").split("\n")


class LeiGod:
    def __init__(self, index, ck):
        self.index = index
        self.user_name = ''
        self.session = requests.session()
        self.headers = {"token": ck, "appId": "nnMobile_d0k3duup", "reqChannel": "1"}
        self.notify_flag = True if NOTIFY_FLAG == 1 else False
        self.account_token = ''

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

    def query_sign(self):
        url = "https://opapi.xxghh.biz/u-mobile/getSpeedWebTokenSign"
        try:
            res = self.session.post(url)
            res_data = res.json()

            if res_data['retCode'] == '100':
                ret_data = res_data['retData']
                self.user_name = ret_data['phone']
                self.print(f"登录成功")
                self.print("============== 检查状态 ==============", {'clear': True})
                self.query_token(ret_data)
            else:
                self.print(res_data['retMsg'], {'notify': True})
        except Exception as e:
            self.print(e, {'notify': True})

    def query_token(self, data):
        url = "https://webapi.xxghh.biz/passport/web/token"
        json = {
            "phone": data['phone'],
            "app_id": data['app_id'],
            "src_channel": data['src_channel'],
            "ts": str(int(data['ts'])),
            "nn_number": data['nn_number'],
            "country_code": data['country_code'],
            "sign": data['sign'],
            "user_id": data['user_id']
        }

        try:
            res = self.session.post(url, json=json)
            res_data = res.json()
            # print(res_data)
            if res_data['code'] == 0:
                self.account_token = res_data['data']['account_token']
                self.query_user_info()
            else:
                self.print(res_data['retMsg'], {'notify': True})
        except Exception as e:
            self.print(e, {'notify': True})

    def query_user_info(self):
        url = "https://webapi.xxghh.biz/api/user/info"
        json = {
            "account_token": self.account_token
        }
        try:
            res = self.session.post(url, json=json)
            res_data = res.json()
            if res_data['code'] == 0:
                if res_data['data']['pause_status'] == '未暂停':
                    self.query_pause()
                else:
                    self.print(f"账号已经停止加速，无需暂停")
            else:
                self.print(res_data['retMsg'], {'notify': True})
        except Exception as e:
            self.print(e, {'notify': True})

    def query_pause(self):
        url = "https://webapi.xxghh.biz/api/user/pause"
        json = {
            "account_token": self.account_token
        }

        try:
            res = self.session.post(url, json=json)
            res_data = res.json()
            if res_data['code'] == 0:
                self.print("暂停成功")
            else:
                self.print(res_data['retMsg'], {'notify': True})

        except Exception as e:
            self.print(e, {'notify': True})

    def start(self):
        self.print(f"\n---------------- 账号[{self.index}] ----------------", {'clear': True})
        self.session.headers.clear()
        self.session.headers.update(self.headers)

        self.query_sign()


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
        LeiGod(index + 1, ck).start()
    exit_now()
