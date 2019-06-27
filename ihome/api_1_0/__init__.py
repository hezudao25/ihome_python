# coding:utf-8

from flask import Blueprint


# 创建蓝图对象
api = Blueprint("api_1_0", __name__)

# 倒入蓝图的视图
from . import demo
from . import verify
from . import passport
from . import profile
from . import houses
from . import order
from . import pay