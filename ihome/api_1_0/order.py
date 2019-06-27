# coding:utf-8

from . import api
from flask import request, jsonify, current_app, session, json, g
from ihome.utils.status_code import RET
from ihome import redis_store, db
from ihome.models import User, Area, Facility, HouseImage, House, Order
from ihome import constants
from ihome.utils.commons import login_required
from datetime import datetime


@api.route("/orders", methods=["POST"])
@login_required
def save_order():
    """保存用户的订单"""
    user_id = g.user_id
    # 获取参数
    order_data = request.get_json()
    if not order_data:
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    # 获取用户预订的房屋编号，入住时间以及离开时间
    house_id = order_data.get("house_id")
    start_date_str = order_data.get("start_date")
    end_date_str = order_data.get("end_date")
    if not all([house_id, start_date_str, end_date_str]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不完整")

    # 检查日期格式
    try:
        # 将str格式的日期数据转换成datetime格式的日期数据
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
        assert start_date <= end_date  # 使用断言就行判断
        # 计算预订的天数
        days = (end_date - start_date).days + 1
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="日期格式不正确")

    # 查询用户预订的房屋是否存在
    try:
        house = House.query.get(house_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取房屋信息失败")

    if not house:
        return jsonify(errno=RET.NODATA, errmsg="房屋不存在")

    # 判断房东预订的房屋是不是自己的发布的房屋
    if user_id == house.user_id:
        return jsonify(errno=RET.ROLEERR, errmsg="不能预订自己发布的房屋")

    # 检查用户预订的时间内，房屋没有被别人下单
    try:
        # 查询时间冲突的订单数 select count(*) from ih_order_info where ()
        count = Order.query.filter(Order.house_id == house_id, Order.begin_date <= end_date,
                                   Order.end_date >= start_date).count()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="系统繁忙，请稍候重试")

    # 如果查询的订单冲突数大于0，则说明房屋在用户预订时间内，已被他人预订
    if count > 0:
        return jsonify(errno=RET.DATAERR, errmsg="房屋已被预订")

    # 计算订单总额
    amount = house.price * days

    # 保存订单数据
    order = Order(
        house_id=house_id,
        user_id=user_id,
        begin_date=start_date,
        end_date=end_date,
        days=days,
        house_price=house.price,
        amount=amount
    )

    # 提交数据到数据库
    try:
        db.session.add(order)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="保存订单失败")

    # 返回正确响应数据
    return jsonify(errno=RET.OK, errmsg="OK", data={"order_id": order.id})


@api.route("/order/house/<int:house_id>")
def get_order_house(house_id):
    """获取房屋信息"""
    try:
        house = House.query.get(house_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取数据异常")

    if house is None:
        return jsonify(errno=RET.DBERR, errmsg="房屋不存在")

    # 返回
    return jsonify(errno=RET.OK, errmsg="ok", data={"house": house.to_basic_dict()})


# /api/v1.0/user/orders?role=(custom/landlord)
@api.route("/user/orders", methods=["GET"])
@login_required
def get_user_orders():
    """查询用户的订单信息"""
    user_id = g.user_id
    # 获取前端请求数据中角色role,如果没有则默认为空字符串
    role = request.args.get("role", "")

    # 获取订单信息
    try:
        # 以房东的身份在数据库中查询自己发布过的房屋
        if "landlord" == role:
            houses = House.query.filter(House.user_id == user_id).all()
            # 通过列表生成式方式保存房东名下的所有房屋的id
            houses_ids = [house.id for house in houses]
            # 在Order表中查询预定了自己房子的订单,并按照创建订单的时间的倒序排序，也就是在此页面显示最新的订单信息
            orders = Order.query.filter(Order.house_id.in_(houses_ids)).order_by(Order.create_time.desc()).all()

        else:
            # 以房客的身份查询订单，则查询的是我的订单
            orders = Order.query.filter(Order.user_id == user_id).order_by(Order.create_time.desc()).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取订单信息失败")

    # 订单存在则将订单对象orders转换成字典数据
    orders_dict_list = []
    if orders:
        for order in orders:
            orders_dict_list.append(order.to_dict())

    # 返回
    return jsonify(errno=RET.OK, errmsg="OK", data={"orders": orders_dict_list})


@api.route("/orders/<int:order_id>/status", methods=["PUT"])
@login_required
def accept_reject_order(order_id):
    """接单拒单"""
    user_id = g.user_id
    # 获取请求参数
    req_data = request.get_json()
    if not req_data:
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    action = req_data.get("action")
    # 判断action参数的值在不在accept接单和reject拒单之间
    if action not in ("accept", "reject"):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    # 在数据库中根据订单号查询订单状态为等待接单状态的订单
    try:
        order = Order.query.filter(Order.id == order_id, Order.status == "WAIT_ACCEPT").first()
        # 获取order订单对象中的house对象
        house = order.house
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="无法获取订单数据")

    # 如果order对象不存在或者订单中的房屋id不等于用户id 则说明房东在修改不属于自己房屋订单
    if not order or house.user_id != user_id:
        return jsonify(errno=RET.REQERR, errmsg="操作无效")

    # 房东选择接单，则对应订单状态为等待评论，拒单则需房东填写拒单的原因
    if action == "accept":  # 接单
        order.status = "WAIT_PAYMENT"
    elif action == "reject":  # 拒单
        reason = req_data.get("reason")
        if not reason:
            return jsonify(errno=RET.PARAMERR, errmsg="参数错误")
        order.status = "REJECTED"
        order.comment = reason

    # 将订单修改后的对象提交到数据库
    try:
        db.session.add(order)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="操作失败")

    # 返回
    return jsonify(errno=RET.OK, errmsg="OK")



@api.route("/orders/<int:order_id>/comment", methods=["PUT"])
@login_required
def save_order_comment(order_id):
    """保存订单评价信息"""
    user_id = g.user_id
    # 获取数据
    req_data = request.get_json()
    comment = req_data.get("comment")
    if not comment:
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    # 确保用户只能评价自己的订单并且订单处于待评价的状态
    try:
        order = Order.query.filter(Order.id == order_id, Order.user_id == user_id,
                                   Order.status == "WAIT_COMMENT").first()
        house = order.house
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="无法获取订单数据")

    if not order:
        return jsonify(errno=RET.REQERR, errmsg="操作无效")

    # 提交数据库
    try:
        # 将订单的状态设置为已完成
        order.status = "COMPLETE"
        # 保存订单的评价信息
        order.comment = comment
        # 将房屋的完成订单数增加1
        house.order_count += 1
        db.session.add(order)
        db.session.add(house)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="操作失败")

    # 删除redis中该订单对应的房屋的信息
    try:
        redis_store.delete("house_info_%s" % order.house.id)
    except Exception as e:
        current_app.logger.error(e)

    return jsonify(errno=RET.OK, errmsg="OK")




