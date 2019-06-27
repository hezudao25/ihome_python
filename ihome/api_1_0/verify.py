# coding:utf-8

from . import api
from ihome.utils.captcha.captcha import captcha
from ihome import redis_store
from ihome import constants
from flask import current_app, jsonify, make_response, request
from ihome.utils.status_code import RET
from ihome.models import User
import random
# from ihome.libs.yuntongxun.SendTemplateSMS import CCP
from ihome.tasks.task_sms import send_sms

# GET 120.0.0.1/api/v1/image_codes/<image_code_id>
@api.route("/image_codes/<image_code_id>")
def get_image_code(image_code_id):
    """
    获取图片验证码
    : params image_code_id:  图片验证码编号
    :return:
    """
    # 业务逻辑处理
    # 生存验证码图片
    name, text, image_data = captcha.generate_captcha()
    # 将验证码值与编码存入redis
    try:
        redis_store.setex("image_code_%s" % image_code_id,constants.IMAGE_CODE_REDIS_EXPIRES, text)
    except Exception as e:
        # 记录日至
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="保存图片验证码失败")
    # 返回值
    resp = make_response(image_data)
    resp.headers["Content-Type"] = "image/jpg"
    return resp


# GEET 127.0.0.1/api/v1/sms_codes/<mobile>?image_code=xxxx&image_code_id=xxx
@api.route("/sms_codes/<mobile>")
def get_sms_code(mobile):
    """获取短信"""
    # 获取 参数
    image_code = request.args.get("image_code")
    image_code_id = request.args.get("image_code_id")

    # 验证参数
    if not all([image_code_id, image_code]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不完整")

    # 业务处理 从redis数据库u取出验证码进行对比
    try:
        redis_image_code = redis_store.get("image_code_%s" % image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR, errmsg="redis数据库出错")
    # 验证验证码是否过期
    if redis_image_code is None:
        return jsonify(errno=RET.DATAERR, errmsg="验证码已过期")

    # 删除redis中的图片验证码，防止用户使用同一验证码验证多次
    try:
        redis_store.delete("image_code_%s" % image_code_id)
    except Exception as e:
        current_app.logger.error(e)
    # 进行对比
    if redis_image_code.decode(encoding='utf-8').lower() != image_code.lower():

        return jsonify(errno=RET.DATAERR, errmsg="图片验证码错误")
    # 判断这个手机号的操作，在60秒内也没有以前的记录
    try:
        send_flag = redis_store.get("send_sms_code_%s" % mobile)
    except Exception as e:
        current_app.logger.error(e)
    else:
        if send_flag is not None:
            # 表示60内有记录
            return jsonify(errno=RET.REQERR, errmsg="请求频繁，清在60秒后再试")
    # 判断手机号是否存在
    try:
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        current_app.logger.error(e)
    else:
        if user is not None:
            # 说明手机号已经存在
            return jsonify(errno=RET.DATAEXIST, errmsg="手机号已存在")

    # 生成随机6位数验证码
    sms_code = "%06d" % random.randint(0, 999999)
    # 保存验证码
    try:
        redis_store.setex("sms_code_%s" % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
        # 保存发送给这个手机号的记录，防止用户在60S内再次发送
        redis_store.setex("send_sms_code_%s" % mobile, constants.SEND_SMS_CODE_INTERVAL, 1)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="保存验证码异常")

    # 使用celery异步发送短信
    send_sms.delay(mobile, [sms_code, int(constants.SMS_CODE_REDIS_EXPIRES / 60)], 1)
    # 发送短信
    # try:
    #     ccp = CCP()
    #     res = ccp.send_sms_code(mobile, [sms_code, int(constants.IMAGE_CODE_REDIS_EXPIRES/60)], 1)
    # except Exception as e:
    #     current_app.logger.error(e)
    #     return jsonify(errno=RET.THIRDERR, errmsg="短信发送异常")
    #
    # if res == "000000":
    #     return jsonify(errno=RET.OK, errmsg="发送短信成功")
    # else:
    #     return jsonify(errno=RET.THIRDERR, errmsg="发送短信失败")
    return jsonify(errno=RET.OK, errmsg="发送短信成功")