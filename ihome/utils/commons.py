# coding:utf-8

from werkzeug.routing import BaseConverter
from flask import session, jsonify, g
from .status_code import RET
import functools


class ReConvert(BaseConverter):
    """定义正则转换器"""
    def __init__(self, url_map, regex):
        super().__init__(url_map)
        self.regex = regex


def login_required(view_func):
    """定义的验证登陆状态的装饰其"""
    @functools.wraps(view_func)  # 引用此装饰其，一面改变被装饰的函数的属性
    def wrapper(*args, **kwargs):
        # 判断用户登陆状态
        user_id = session.get("user_id")
        if user_id is not None:
            g.user_id = user_id  # 使用g对象保存user_id
            return view_func(*args, **kwargs)
        else:
            return jsonify(errno=RET.SESSIONERR, errmsg="用户没有登陆")

    return wrapper