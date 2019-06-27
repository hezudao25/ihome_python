# coding:utf-8

from . import api
from flask import request, jsonify, current_app, session
from ihome.utils.status_code import RET
import re
from ihome import redis_store, db
from ihome.models import User
from sqlalchemy.exc import IntegrityError
from ihome import constants


@api.route("/users", methods=["POST"])
def register():
    """注册
    请求的参数： 手机号，短信验证码，密码
    参数格式： json
    """
    req_dict = request.get_json()
    mobile = req_dict.get("mobile")  # 跟前端约定好的
    sms_code = req_dict.get("phonecode")
    password = req_dict.get("password")
    password2 = req_dict.get("password2")

    if not all([mobile, sms_code, password, password2]):
        return jsonify(errno=RET.PARAMERR, errmsg="请求参数不完整")

    # 判断手机号格式
    if not re.match(r"1[34578]\d{9}", mobile):
        return jsonify(errno=RET.PARAMERR, errmsg="手机号码格式错误")

    if password != password2:
        return jsonify(errno=RET.PARAMERR, errmsg="两个密码不一致")

    # 从redis中取出短信验证码
    try:
        real_sms_code = redis_store.get("sms_code_%s" % mobile)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="读取redis中验证码异常")
    if real_sms_code is None:
        return jsonify(errno=RET.NODATA, errmsg="短信验证码已过期")

    # 删除redis中的短信验证码，防止重复使用
    try:
        redis_store.delete("sms_code_%s" % mobile)
    except Exception as e:
        current_app.logger.error(e)

    # 判断短信验证码的正确
    if real_sms_code.decode(encoding='utf-8').lower() != sms_code.lower():
        return jsonify(errno=RET.DATAERR, errmsg="短信验证码错误")

    # 判断手机号是否存在
    # try:
    #     user = User.query.filter_by(mobile=mobile).first()
    # except Exception as e:
    #     current_app.logger.error(e)
    # else:
    #     if user is not None:
    #         # 说明手机号已经存在
    #         return jsonify(errno=RET.DATAEXIST, errmsg="手机号已存在")

    # 将用户信息存入数据库
    user = User(name=mobile, phone=mobile)
    user.password = password  # 设置属性
    try:
        db.session.add(user)
        db.session.commit()
    except IntegrityError as e:
        # 表示手机号出现了重复值
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAEXIST, errmsg="手机号已存在")
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询数据出错")

    # 保存登陆状态到session
    session["name"] = mobile
    session["mobile"] = mobile
    session["user_id"] = user.id

    # 返回结果
    return jsonify(errno=RET.OK, errmsg="注册成功")


@api.route("/login", methods=["POST"])
def login():
    """登陆
    参数： 用户名  密码
    格式： json
    """
    res_data = request.get_json()
    mobile = res_data.get("mobile")
    password = res_data.get("password")

    # 验证参数
    if not all([mobile, password]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不全")

    if not re.match(r"1[345789]\d{9}", mobile):
        return jsonify(errno=RET.PARAMERR, errmsg="手机号码格式错误")

    # 将用户登录的错误次数以用户的IP作为标识，保存到redis数据库中，通过redis数据库来限制时间，如次数超过10分钟内错误登录超过5次
    user_ip = request.remote_addr
    try:
        access_nums = redis_store.get("access_nums_%s" % user_ip)
    except Exception as e:
        current_app.logger.error(e)
    else:
        if access_nums is not None and int(access_nums) >= constants.LOGIN_ERROR_MAX_TIMES:
            return jsonify(errno=RET.REQERR, errmsg="错误次数过多，请稍后重试")

    # 获取用户
    try:
        user = User.query.filter_by(phone=mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取用户信息失败")

    # 验证密码和用户名
    if user is None or user.check_password(password) is False:
        # 验证失败需要记录失败次数，保存到redis数据库中
        try:
            redis_store.incr("access_nums_%s" % user_ip)
            redis_store.expire("access_nums_%s" % user_ip, constants.LOGIN_ERROR_FORBID_TIME)
        except Exception as e:
            current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR, errmsg="用户名或密码错误")

    # 保存session
    session["name"] = user.name
    session["mobile"] = user.phone
    session["user_id"] = user.id
    # 返回结果
    return jsonify(errno=RET.OK, errmsg="登录成功")


@api.route("/loginout", methods=["DELETE"])
def loginout():
    """
    推出登陆
    :return:
    """
    # 在清除session数据时，先从session中获取csrf_token的值
    csrf_token = session.get("csrf_token")
    session.clear()
    # 当session数据清除完后 再设置session中的csrf_token的值，这样可以解决csrf_token缺失的bug
    session["csrf_token"] = csrf_token
    return jsonify(errno=RET.OK, errmsg="ok")


@api.route("/session", methods=["GET"])
def check_login():
    """
    检测登陆状态
    :return:
    """
    name = session.get("name")
    if name is not None:
        return jsonify(errno=RET.OK, errmsg="true", data={"name": name})
    else:
        return jsonify(errno=RET.SESSIONERR, errmsg="false")

