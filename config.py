# coding:utf-8
import redis
import os


class Config(object):
    """配置信息"""

    SECRET_KEY = "SDFSDFEDFDFDF"
    # 数据库
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:root@127.0.0.1:3306/ihome"
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    # REDIS
    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379

    # flask-session配置
    SESSION_TYPE = "redis"
    SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)
    SESSION_USE_SIGNER = True  # 对cookies中的session_id进行隐藏处理
    PERMANENT_SESSION_LIFETIME = 86400  # session数据的有效期，单位秒

    BASE_DIR = os.path.dirname(__file__)  # 当前文件所在路径


class DevelopmentConfig(Config):
    """开放模式的配置信息"""
    DEBUG = True


class ProdctionConfig(Config):
    """生存环境配置信息"""
    pass


config_map = {
    "develop": DevelopmentConfig,
    "product": ProdctionConfig
}