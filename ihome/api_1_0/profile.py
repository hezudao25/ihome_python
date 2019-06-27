# coding:utf-8

from . import api
from flask import g, current_app, jsonify, request
from ihome.utils.status_code import RET
from ihome.utils.qiniu_sdk import put_qiniu
from ihome.models import User
from ihome import db
from ihome.constants import QINIU_URL_DOMAIN
from ihome.utils.commons import login_required


@api.route("/users/avatar", methods=["POST"])
@login_required
def set_user_avatar():
    """设置用户的头像
    参数： 图片多媒体表单格式
    """
    user_id = g.user_id

    # 获取图片
    image_file = request.files.get("avatar")

    if image_file is None:
        return jsonify(errno=RET.PARAMERR, errmsg="未上床")

    image_data = image_file.read()

    # 调用其牛上床图片
    image_id = put_qiniu(image_data)

    # 保存到数据库
    try:
        User.query.filter_by(id=user_id).update({"avatar_url": image_id})
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="保存图片信息失败")

    return jsonify(errno=RET.OK, errmsg="保存成功", data={"avatar_url": QINIU_URL_DOMAIN+image_id})


@api.route("/users/profile", methods=["GET"])
@login_required
def get_user_profile():
    """获取个人信心"""
    user_id = g.user_id
    # 获取信息
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return jsonify(errno=RET.NODATA, errmsg="无效操作")

    return jsonify(errno=RET.OK, errmsg="ok", user={"avatar": user.avatar_url, "name": user.name, "phone": user.phone})


@api.route("/users/name", methods=["POST"])
@login_required
def update_user_name():
    """更新名字"""
    user_id = g.user_id
    name = request.get_json().get("name")
    if name is None:
        return jsonify(errno=RET.PARAMERR, errmsg="姓名不能为空")
    # 保存到数据库
    try:
        User.query.filter_by(id=user_id).update({"name": name})
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="保存姓名信息失败")

    return jsonify(errno=RET.OK, errmsg="保存成功", data={"name": name})


@api.route("/users/auth", methods=["GET"])
@login_required
def get_user_auth():
    """市民认证"""
    user_id = g.user_id
    try:
        user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取用户实名认证信息失败")
    if user is None:
        return jsonify(errno=RET.NODATA, errmsg="无效操作")

    return jsonify(errno=RET.OK, errmsg="OK", data=user.auth_to_dict())


@api.route("/users/auth", methods=["POST"])
@login_required
def set_user_auth():
    """保存实名认证"""
    user_id = g.user_id
    req_data = request.get_json()
    if not req_data:
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    real_name = req_data.get("real_name")
    id_card = req_data.get("id_card")

    if not all([real_name, id_card]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    try:
        User.query.filter_by(id=user_id, real_name=None, real_id_card=None).update(
            {"real_name": real_name, "real_id_card": id_card})
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="保存用户实名信息失败")

    return jsonify(errno=RET.OK, errmsg="OK")