# coding:utf-8

from . import api
from ihome.utils.commons import login_required
from ihome.models import Order
from flask import request, jsonify, current_app, session, json, g
import os
from ihome.utils.status_code import RET
from ihome import redis_store, db
from alipay import AliPay
from ihome import constants


@api.route("/orders/<int:order_id>/payment", methods=["POST"])
@login_required
def pay_to(order_id):
    """支付行为"""
    user_id = g.user_id
    # 在数据库中根据订单号查询订单状态为等待支付状态的订单
    try:
        order = Order.query.filter(Order.id == order_id, Order.user_id == user_id, Order.status == "WAIT_PAYMENT").first()

    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="无法获取订单数据")

    if order is None:
        return jsonify(errno=RET.NODATA, errmsg="订单数据有误")
    # 支付宝 初始化
    app_private_key_string = open(os.path.join(os.path.dirname(__file__), "keys/app_private_key.pem")).read()
    alipay_public_key_string = open(os.path.join(os.path.dirname(__file__), "keys/alipay_public_key.pem")).read()

    # 创建支付宝SDK工具对象
    alipay = AliPay(
        appid="2016101100661322",
        app_notify_url=None,  # 默认回调url
        app_private_key_string=app_private_key_string,
        # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
        alipay_public_key_string=alipay_public_key_string,
        sign_type="RSA2",  # RSA 或者 RSA2
        debug=True,  # 默认False
    )
    # 手机网站支付 沙乡王之：https://openapi.alipaydev.com/gateway.do + order_string
    order_string = alipay.api_alipay_trade_wap_pay(
        out_trade_no=order.id,  # 订单编号
        total_amount=str(order.amount/100.0),  # 订单金额
        subject=u"爱家租房 %s" % order.id,  # 订单标题
        return_url="http://192.168.72.147:5000/paycomplete.html",
        notify_url=None  # 可选, 不填则使用默认notify url
    )
    # 构建让用户条状的支付连接地质
    pay_url = constants.ALIPAY_URL_PREFIX + order_string
    return jsonify(errno=RET.OK, errmsg="ok", data={"pay_url": pay_url})


@api.route("/orders/payment", methods=["PUT"])
def save_order_payment_result():
    """保存订单支付结果"""
    data = request.form.to_dict()
    # sign 不能参与签名验证
    signature = data.pop("sign")
    # 支付宝 初始化
    app_private_key_string = open(os.path.join(os.path.dirname(__file__), "keys/app_private_key.pem")).read()
    alipay_public_key_string = open(os.path.join(os.path.dirname(__file__), "keys/alipay_public_key.pem")).read()
    # 创建支付宝SDK工具对象
    alipay = AliPay(
        appid="2016101100661322",
        app_notify_url=None,  # 默认回调url
        app_private_key_string=app_private_key_string,
        # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
        alipay_public_key_string=alipay_public_key_string,
        sign_type="RSA2",  # RSA 或者 RSA2
        debug=True,  # 默认False
    )
    # verify
    success = alipay.verify(data, signature)
    if success:
        order_id = data.get("out_trade_no")
        trade_no = data.get("tarde_no") # 支付宝交易号
        try:
            Order.query.filter_by(id=order_id).update({"status": "WAIT_COMMENT", "trade_no": trade_no})
            db.session.commit()
        except Exception as e:
            current_app.logger.error(e)
            db.session.rollback()

    return jsonify(errno=RET.OK, errmsg="ok")
