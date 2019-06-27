# coding:utf-8

from celery import Celery
from ihome.libs.yuntongxun.SendTemplateSMS import CCP


app = Celery("ihome", broker="redis://127.0.0.1:6379/1")


@app.task
def send_sms(to, datas, tempid):
    """发送短信的异步任务"""
    ccp = CCP()
    ccp.send_sms_code(to, datas, tempid)
    # 使celery 发送短信

