# coding:utf-8

from . import api
from flask import request, jsonify, current_app, session, json, g
from ihome.utils.status_code import RET
from ihome import redis_store, db
from ihome.models import User, Area, Facility, HouseImage, House, Order
from ihome import constants
from ihome.utils.commons import login_required
from ihome.utils.qiniu_sdk import put_qiniu
import time, os
from datetime import datetime


@api.route("/house/areas")
def get_area_info():
    """城区信息"""
    # 查询数据库，读取城区信息
    try:
        resp_json_str = redis_store.get("area_info")
    except Exception as e:
        current_app.logger.error(e)
    else:
        if resp_json_str is not None:
            current_app.logger.info("hit redis area")
            return resp_json_str, 200, {"Content-Type": "application/json"}

    try:
        area_li = Area.query.all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取地区信息异常")

    area_dict_li = []
    # 将对象庄为[]
    for area in area_li:
        area_dict_li.append(area.to_dict())

    resp_dict = dict(errno=RET.OK, errmsg="OK", data=area_dict_li)
    resp_json_str = json.dumps(resp_dict)
    try:
        redis_store.setex("area_info", constants.AREA_INFO_REDIS_CACHE_EXPIRES, resp_json_str)
    except Exception as e:
        current_app.logger.error(e)

    return resp_json_str, 200, {"Content-Type": "application/json"}


@api.route("/house/facility")
def get_facility_info():
    """获取配套信息"""
    try:
        facilitys = Facility.query.all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取配套信息异常")
    # 获取列表
    facility_list = []
    for facility in facilitys:
        facility_list.append(facility.to_dict())

    return jsonify(errno=RET.OK, errmsg="OK", data=facility_list)



@api.route("/users/houses")
@login_required
def get_my_house():
    """我的房源"""
    user_id = g.user_id
    # 获取房源
    try:
        user = User.query.get(user_id)
        houses = user.houses
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取数据失败")

    # 将查询到的房屋信息转换成字典数据，添加到定义的houses_list列表中
    houses_list = []
    for house in houses:
        houses_list.append(house.to_basic_dict())

    return jsonify(errno=RET.OK, errmsg="OK", data={"houses": houses_list})


@api.route("/house/info", methods=["POST"])
@login_required
def save_house_info():
    """
    保存房源信息
    格式： json
    :return:
    """
    # 获取数据
    user_id = g.user_id
    house_data = request.get_json()

    title = house_data.get("title")  # 房屋名称标题
    price = house_data.get("price")  # 房屋单价
    area_id = house_data.get("area_id")  # 房屋所属城区的编号
    address = house_data.get("address")  # 房屋地址
    room_count = house_data.get("room_count")  # 房屋包含的房间数目
    acreage = house_data.get("acreage")  # 房屋面积
    unit = house_data.get("unit")  # 房屋布局（几室几厅)
    capacity = house_data.get("capacity")  # 房屋容纳人数
    beds = house_data.get("beds")  # 房屋卧床数目
    deposit = house_data.get("deposit")  # 押金
    min_days = house_data.get("min_days")  # 最小入住天数
    max_days = house_data.get("max_days")  # 最大入住天数
    # 校验数据
    if not all(
            [title, price, area_id, address, room_count, acreage, unit, capacity, beds, deposit, min_days, max_days]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不完整")
    # 判断用户输入的房屋单价和押金是否为正确参数，通过存入数据库字段单位分，如果用户输入的值不能转换为float和int类型，说明参数错误
    try:
        price = int(float(price) * 100)
        deposit = int(float(deposit) * 100)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    # 判断区县id是否存在
    try:
        area = Area.query.get(area_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库异常")
    if area is None:
        return jsonify(errno=RET.NODATA, errmsg="区县信息有误")
    # 保存信息

    house = House(
        user_id=user_id,
        title=title,
        price=price,
        area_id=area_id,
        address=address,
        room_count=room_count,
        acreage=acreage,
        unit=unit,
        capacity=capacity,
        beds=beds,
        deposit=deposit,
        min_days=min_days,
        max_days=max_days
    )

    # 获取设备
    facility_ids = house_data.get("facility")
    # 对获取设备设施字段的值进行判断,下判断这个值存不存在，当用户勾选设备设施时，举例facility_ids值为[2,4]
    if facility_ids:
        # 通过Facility类中的id值使用in_方法查询其中的id
        # select * from ih_facility_info where id in facility_ids;
        try:
            facilities = Facility.query.filter(Facility.id.in_(facility_ids)).all()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg="数据库异常")

    if facilities:
        house.facilities = facilities
        try:
            db.session.add(house)
            db.session.commit()
        except Exception as e:
            current_app.logger.error(e)
            db.session.rollback()
            return jsonify(errno=RET.DBERR, errmsg="保存数据异常")
    # 返回结果
    return jsonify(errno=RET.OK, errmsg="OK", data={"house_id": house.id})


@api.route("/house/image", methods=["POST"])
@login_required
def save_house_image():
    """保存房屋图片"""
    image_file = request.files.get("house_image")
    # 获取房源ID
    house_id = request.form.get("house_id")
    if not all([image_file, house_id]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")
    # 判断房屋是否在，存在才上传到七牛，如果不存在就不上传
    try:
        house = House.query.get(house_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库异常")

    if house is None:
        return jsonify(errno=RET.NODATA, errmsg="房屋不存在")

    image_data = image_file.read()

    # try:
    #     file_name = put_qiniu(image_data)
    # except Exception as e:
    #     current_app.logger.error(e)
    #     #return jsonify(errno=RET.THIRDERR, errmsg="上传图片失败")
    # else:
    now = time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))
    os.makedirs(os.path.join(current_app.config["BASE_DIR"], "ihome/static/upload/"), exist_ok=True)
    file_name = now + ".jpg"
    with open(os.path.join(current_app.config["BASE_DIR"], "ihome/static/upload/", file_name), "wb") as f:
        f.write(image_data)

    file_name = "/static/upload/" + file_name
    house_image = HouseImage(house_id=house_id, url=file_name)
    db.session.add(house_image)

    # 当house对象中的index_image_url不存在时，设置网站主页房屋图片
    if not house.index_image_url:
        house.index_image_url = file_name
        db.session.add(house)

    # 提交数据库
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="保存图片异常")

    # 返回结果 constants.QINIU_URL_DOMAIN

    image_url = file_name
    return jsonify(errno=RET.OK, errmsg="OK", data={"image_url": image_url})


@api.route("/houses")
def get_house_list():
    """房源页房屋列表信息"""
    # 获取请求参数
    start_date = request.args.get("sd", "")  # 用户入住日期
    end_date = request.args.get("ed", "")  # 用户离开日期
    area_id = request.args.get("aid", "")  # 入住区县
    sort_key = request.args.get("sk", "new")  # 排序关键字,当未选择排序条件时，默认按最新排序，这个new关键字根据前端定义走的
    page = request.args.get("p")  # 页数

    redis_key = "house_%s_%s_%s_%s" % (start_date, end_date, area_id, sort_key)
    # 判断 有没有缓存
    try:
        resp_json = redis_store.hget(redis_key, page)
    except Exception as e:
        current_app.logger.error(e)
    else:
        if resp_json:
            return resp_json, 200, {"Content-Type": "application/json"}

    # 处理日期 用户可能选择入住日期或者是离开日期，所以要一一进行判断
    try:
        if start_date:
            start_date = datetime.strptime(start_date, "%Y-%m-%d")

        if end_date:
            end_date = datetime.strptime(end_date, "%Y-%m-%d")
        # 当用户两者都选择情况下，需要进行判断，入住日期肯定是小于或等于离开日期的
        if start_date and end_date:
            assert start_date <= end_date
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="日期参数有误")

    # 判断区县id
    if area_id:
        try:
            area = Area.query.get(area_id)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.PARAMERR, errmsg="区县参数有误")

    # 处理页数
    try:
        page = int(page)
    except Exception as e:
        # 如果出现异常则使page=1
        page = 1
        current_app.logger.error(e)

    # 定义过滤条件的参数列表容器以及存放冲突订单对象
    filter_params = []
    conflict_orders = None

    #在数据库中查询订单表中的冲突订单，
    # 这里稍微比较绕，就是以什么条件来筛选订单中冲突的订单，
    # 其实简单一句就是用户不管选择的入住日期或者是离开日期又或者是入住以及离开日期，
    # 这三种情况中任一情况的日期都不能在Order表中订单起始日期begin_date与end_date结束日期这范围内，
    # 即作出以下逻辑判断
    try:
        if start_date and end_date:
            # 查询冲突的订单所有对象
            conflict_orders = Order.query.filter(Order.begin_date <= end_date, Order.end_date >= start_date).all()
        elif start_date:
            # 用户只选择入住日期
            conflict_orders = Order.query.filter(Order.end_date >= start_date).all()
        elif end_date:
            # 用户只选择离开日期
            conflict_orders = Order.query.filter(Order.begin_date <= end_date).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库异常")

    #  当获取的冲突订单对象存在时，获取冲突房屋的id，如果冲突的房屋id不为空，则向查询参数中添加条件
    if conflict_orders:
        # 从订单中获取冲突的房屋id
        conflict_house_ids = [order.house_id for order in conflict_orders]  # 使用列表生成式进行简写操作

        # 如果冲突的房屋id不为空，向查询参数中添加条件
        if conflict_house_ids:
            filter_params.append(House.id.notin_(conflict_house_ids))

    if area_id:
        filter_params.append(House.area_id == area_id)

    # 根据过滤参数列表，查询数据库，并进行条件排序
    if sort_key == "booking":  # 入住做多
        house_query = House.query.filter(*filter_params).order_by(House.order_count.desc())
    elif sort_key == "price-inc":  # 价格低-高
        house_query = House.query.filter(*filter_params).order_by(House.price.asc())
    elif sort_key == "price-des":  # 价格高-低
        house_query = House.query.filter(*filter_params).order_by(House.price.desc())
    else:
        # 如果用户什么都没选择，则按照最新排序（数据库字段创建时间）
        house_query = House.query.filter(*filter_params).order_by(House.id.desc())

    # 分页处理 paginate方法需传递三个参数，page:分页页数 per_page:每页显示多少条数据 error_out: 错误输出
    try:
        page_obj = house_query.paginate(page=page, per_page=constants.HOUSE_LIST_PAGE_CAPACITY, error_out=False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库异常")

    # 获取分页页面数据
    houses = []
    house_list = page_obj.items
    for house in house_list:
        houses.append(house.to_basic_dict())

    # 获取总页数，并返回正确响应数据
    total_page = page_obj.pages

    #  将响应数据构建成json格式数据
    resp_dict = dict(errno=RET.OK, errmsg="OK", data={"houses": houses, "total_page": total_page, "current_page": page})
    resp_json = json.dumps(resp_dict)
    # 设置redis数据库的key
    redis_key = "house_%s_%s_%s_%s" % (start_date, end_date, area_id, sort_key)

    try:

        # 创建redis pipeline 管道对象，可以一次性执行多条语句
        pipeline = redis_store.pipeline()
        # 开启多个语句的记录
        pipeline.multi()
        # 使用管道对象管理多条语句
        pipeline.hset(redis_key, page, resp_json)  # 将数据存入redis数据
        pipeline.expire(redis_key, constants.HOUES_LIST_PAGE_REDIS_CACHE_EXPIRES)  # 设置有效期
        # 执行语句
        pipeline.execute()
    except Exception as e:
        current_app.logger.error(e)

    return resp_json, 200, {"Content-Type": "application/json"}


@api.route("/house/index", methods=["GET"])
def get_house_index():
    """
    首页
    :return:
    """
    name = session.get("name")
    houses = House.query.order_by(House.capacity.desc()).limit(5)
    house_list = []
    for house in houses:
        house_list.append(house.to_basic_dict())

    if name is not None:
        return jsonify(errno=RET.OK, errmsg="true", data={"name": name, "hlist": house_list})
    else:
        return jsonify(errno=RET.SESSIONERR, errmsg="false")


@api.route("/house/<int:house_id>", methods=["GET"])
def get_house_detail(house_id):
    """
    获取房屋详情
    :param house_id:
    :return:
    """
    user_id = session.get("user_id", "-1")

    # 尝试从redis数据库中获取房屋详情信息, 出现异常则使ret为None，
    # 所以需要在进入函数后，那么需要从去数据库中获取房屋详情信息
    try:
        ret = redis_store.get("house_info_%s" % house_id)
    except Exception as e:
        current_app.logger.error(e)
        ret = None
    if ret:
        current_app.logger.info("house info from redis")
        return '{"errno":"0", "errmsg":"OK", "data":{"user_id":%s, "house":%s}}' % (user_id, ret.decode(encoding='utf-8')), 200, {
            "Content-Type": "application/json"}

    if not house_id:
        return jsonify(errno=RET.PARAMERR, errmsg="参数缺失")

    # 获取房屋对象
    try:
        house = House.query.get(house_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询数据失败")
    if not house:
        return jsonify(errno=RET.NODATA, errmsg="房屋不存在")

    # 将查询到的房屋对象转换成字典
    try:
        house_data = house.to_full_dict()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR, errmsg="数据错误")

    json_houses = json.dumps(house_data)
    try:
        redis_store.setex("house_info_%s" % house_id, constants.HOUSE_DETAIL_REDIS_EXPIRE_SECOND, json_houses)
    except Exception as e:
        current_app.logger.error(e)
    print(json_houses)
    # 返回
    resp = '{"errno":"0", "errmsg":"OK", "data":{"user_id":%s, "house":%s}}' % (user_id, json_houses), 200, {
        "Content-Type": "application/json"}
    return resp
