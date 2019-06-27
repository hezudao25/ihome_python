# coding:utf-8

from flask import Blueprint, current_app, make_response
from flask_wtf import csrf


# 提供静态文件的蓝图
html = Blueprint("web_html", __name__)


@html.route("/<re(r'.*'):file_name>")
def get_html(file_name):
    """提供html文件"""
    if not file_name:
        file_name = "index.html"

    if file_name != "favicon.ico":
        file_name = "html/" + file_name

    csrf_token = csrf.generate_csrf()
    # 导入make_response，将返回的静态文件方法的值构建成响应对象
    resp = make_response(current_app.send_static_file(file_name))
    resp.set_cookie("csrf_token", csrf_token)

    return resp