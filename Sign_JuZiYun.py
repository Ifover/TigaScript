# -*- coding: utf-8 -*-
# @Name: 桔子云
# @Version: 1.0
# @Author: Ifover
# ===============================
# cron: "0 5 0 * * *"
# const $ = new Env('桔子云')
# export AccountJuZiYun="123456@qq.com#abcdefg&65432@qq.com#aacc"  多账号使用换行或&隔开
# 自用，签到获取一些流量
# ===============================


import requests
import os
import datetime
import sys

NOTIFY_FLAG = 0  # 【0】只通知重要内容(如CK失效),【1】每次执行后都通知.

# 下面的就别动了
TASK_NAME = "桔子云"
CK_NAME = "AccountJuZiYun"
AUTH_CK = []
NOTIFY_STR = []

ck = os.getenv(CK_NAME)
if ck:
    AUTH_CK += ck.replace("&", "\n").split("\n")


class JuZiYun:

    def __init__(self, index, user):
        self.index = index
        self.user = user
        self.user_name = ''
        self.base_url = os.getenv("URL_JUZIYUN", "https://juzi69.com")
        self.session = requests.session()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest"
        }
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

    def query_login(self):
        url = self.base_url + "/auth/login"
        arr = self.user.split('#')
        if len(arr) == 2:
            data = {
                "email": arr[0],
                "passwd": arr[1],
                "code": ""
            }
            try:
                res = self.session.post(url, data=data, headers=self.headers)
                res_data = res.json()

                if res_data['ret'] == 1:
                    self.user_name = arr[0]
                    self.print(f"登录成功")
                    return True

                else:
                    self.user_name = ''
                    self.print(res_data['msg'], {'notify': True})
                    return False

            except Exception as e:
                self.print(e, {'notify': True})
        else:
            self.print("账号信息错误", {'notify': True})

    def query_check_in(self):
        url = self.base_url + "/user/checkin"
        try:
            res = self.session.post(url, headers=self.headers)
            res_data = res.json()
            if res_data['ret'] == 1 or res_data['ret'] == 0:
                self.print(res_data['msg'])
            else:
                self.print(res_data['msg'], {'notify': True})

        except Exception as e:
            self.print(e, {'notify': True})

    def start(self):
        self.print(f"\n---------------- 账号[{self.index}] ----------------", {'clear': True})
        # self.query_login()
        if self.query_login():
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
    for index, user in enumerate(AUTH_CK):
        JuZiYun(index + 1, user).start()
    exit_now()
