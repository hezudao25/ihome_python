# coding=utf-8
from ihome import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app
from . import constants


class BaseModel(object):
    """模型基类，为每个模型补充创建时间和更新时间"""
    create_time = db.Column(db.DATETIME, default=datetime.now())
    update_time = db.Column(db.DATETIME, default=datetime.now(), onupdate=datetime.now())

    def add_update(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


class User(BaseModel, db.Model):
    """用户"""
    __tablename__= 'ihome_user'
    id = db.Column(db.INTEGER, primary_key=True)
    phone = db.Column(db.String(11), unique=True)
    pwd_hash = db.Column(db.String(200))
    name = db.Column(db.String(30), unique=True)
    avatar_url = db.Column(db.String(100))
    real_name = db.Column(db.String(30))
    real_id_card = db.Column(db.String(18), unique=True)

    houses = db.relationship('House', backref='user')
    orders = db.relationship('Order', backref='user')

    #读
    @property
    def password(self):
        return ''
    #写
    @password.setter
    def password(self, pwd):
        self.pwd_hash = generate_password_hash(pwd)

    #对比
    def check_password(self, pwd):
        return check_password_hash(self.pwd_hash, pwd)

    def to_basic_dict(self):
        return {
            'id': self.id,
            'avatar': current_app.config['QINIU_URL']+self.avatar_url if self.avatar_url else '',
            'name': self.name,
            'phone': self.phone
        }

    def to_dict(self):
        """将对象转换为字典数据"""
        user_dict = {
            "user_id": self.id,
            "name": self.name,
            "mobile": self.phone,
            "avatar": constants.QINIU_URL_DOMAIN + self.avatar_url if self.avatar_url else "",
            "create_time": self.create_time.strftime("%Y-%m-%d %H:%M:%S")
        }
        return user_dict

    def auth_to_dict(self):
        return {
            'real_name': self.real_name,
            'id_card': self.real_id_card
        }


ihome_house_facility = db.Table(
    "ihome_house_facility",
    db.Column("house_id", db.Integer, db.ForeignKey("ihome_house.id"), primary_key=True),  # 房屋编号
    db.Column("facility_id", db.Integer, db.ForeignKey("ihome_facility.id"), primary_key=True)  # 设施编号
)


class House(BaseModel, db.Model):
    """房屋信息"""

    __tablename__ = "ihome_house"

    id = db.Column(db.Integer, primary_key=True)  # 房屋编号
    # 房屋主人的用户编号
    user_id = db.Column(db.Integer, db.ForeignKey("ihome_user.id"), nullable=False)
    # 归属地的区域编号
    area_id = db.Column(db.Integer, db.ForeignKey("ihome_area.id"), nullable=False)
    title = db.Column(db.String(64), nullable=False)  # 标题
    price = db.Column(db.Integer, default=0)  # 单价，单位：分
    address = db.Column(db.String(512), default="")  # 地址
    room_count = db.Column(db.Integer, default=1)  # 房间数目
    acreage = db.Column(db.Integer, default=0)  # 房屋面积
    unit = db.Column(db.String(32), default="")  # 房屋单元， 如几室几厅
    capacity = db.Column(db.Integer, default=1)  # 房屋容纳的人数
    beds = db.Column(db.String(64), default="")  # 房屋床铺的配置
    deposit = db.Column(db.Integer, default=0)  # 房屋押金
    min_days = db.Column(db.Integer, default=1)  # 最少入住天数
    max_days = db.Column(db.Integer, default=0)  # 最多入住天数，0表示不限制
    order_count = db.Column(db.Integer, default=0)  # 预订完成的该房屋的订单数
    index_image_url = db.Column(db.String(256), default="")  # 房屋主图片的路径

    # 房屋的设施
    facilities = db.relationship("Facility", secondary=ihome_house_facility)
    images = db.relationship("HouseImage")  # 房屋的图片
    orders = db.relationship('Order', backref='house')

    def to_basic_dict(self):
        """将基本信息转换为字典数据"""
        house_dict = {
            "house_id": self.id,
            "title": self.title,
            "price": self.price,
            "area_name": self.area.name,
            "img_url": constants.QINIU_URL_DOMAIN + self.index_image_url if self.index_image_url else "",
            "room_count": self.room_count,
            "order_count": self.order_count,
            "address": self.address,
            "user_avatar": constants.QINIU_URL_DOMAIN + self.user.avatar_url if self.user.avatar_url else "",
            "ctime": self.create_time.strftime("%Y-%m-%d")
        }
        return house_dict

    def to_full_dict(self):
        """将详细信息转换为字典数据"""
        house_dict = {
            "hid": self.id,
            "user_id": self.user_id,
            "user_name": self.user.name,
            "user_avatar": constants.QINIU_URL_DOMAIN + self.user.avatar_url if self.user.avatar_url else "",
            "title": self.title,
            "price": self.price,
            "address": self.address,
            "room_count": self.room_count,
            "acreage": self.acreage,
            "unit": self.unit,
            "capacity": self.capacity,
            "beds": self.beds,
            "deposit": self.deposit,
            "min_days": self.min_days,
            "max_days": self.max_days,
        }

        # 房屋图片
        img_urls = []
        for image in self.images:
            img_urls.append(constants.QINIU_URL_DOMAIN + image.url)
        house_dict["img_urls"] = img_urls

        # 房屋设施
        facilities = []
        for facility in self.facilities:
            facilities.append(facility.id)
        house_dict["facilities"] = facilities

        # 评论信息
        comments = []
        orders = Order.query.filter(Order.house_id == self.id, Order.status == "COMPLETE", Order.comment != None) \
            .order_by(Order.update_time.desc()).limit(constants.HOUSE_DETAIL_COMMENT_DISPLAY_COUNTS)
        for order in orders:
            comment = {
                "comment": order.comment,  # 评论的内容
                "user_name": order.user.name if order.user.name != order.user.mobile else "匿名用户",  # 发表评论的用户
                "ctime": order.update_time.strftime("%Y-%m-%d %H:%M:%S")  # 评价的时间
            }
            comments.append(comment)
        house_dict["comments"] = comments
        return house_dict


class HouseImage(BaseModel, db.Model):
    """房屋图片"""

    __tablename__ = "ihome_house_image"

    id = db.Column(db.Integer, primary_key=True)
    # 房屋编号
    house_id = db.Column(db.Integer, db.ForeignKey("ihome_house.id"), nullable=False)
    url = db.Column(db.String(256), nullable=False)  # 图片的路径


class Facility(BaseModel, db.Model):
    """设施信息"""

    __tablename__ = "ihome_facility"

    id = db.Column(db.Integer, primary_key=True)  # 设施编号
    name = db.Column(db.String(32), nullable=False)  # 设施名字
    css = db.Column(db.String(30))  # 设施展示的图标

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'css': self.css
        }

    def to_house_dict(self):
        return {'id': self.id}


class Area(BaseModel, db.Model):
    """城区"""

    __tablename__ = "ihome_area"

    id = db.Column(db.Integer, primary_key=True)  # 区域编号
    name = db.Column(db.String(32), nullable=False)  # 区域名字
    houses = db.relationship("House", backref="area")  # 区域的房屋

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name
        }


class Order(BaseModel,db.Model):
    """订单"""

    __tablename__ = "ihome_order"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("ihome_user.id"), nullable=False)
    house_id = db.Column(db.Integer, db.ForeignKey("ihome_house.id"), nullable=False)
    begin_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    days = db.Column(db.Integer, nullable=False)
    house_price = db.Column(db.Integer, nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    status = db.Column(
        db.Enum(
            "WAIT_ACCEPT",  # 待接单,
            "WAIT_PAYMENT",  # 待支付
            "PAID",  # 已支付
            "WAIT_COMMENT",  # 待评价
            "COMPLETE",  # 已完成
            "CANCELED",  # 已取消
            "REJECTED"  # 已拒单
        ),
        default="WAIT_ACCEPT", index=True)
    comment = db.Column(db.Text)
    trade_no = db.Column(db.String(128))  # 交易号

    def to_dict(self):
        """将订单信息转换为字典数据"""
        order_dict = {
            "order_id": self.id,
            "title": self.house.title,
            "img_url": constants.QINIU_URL_DOMAIN + self.house.index_image_url if self.house.index_image_url else "",
            "start_date": self.begin_date.strftime("%Y-%m-%d"),
            "end_date": self.end_date.strftime("%Y-%m-%d"),
            "ctime": self.create_time.strftime("%Y-%m-%d %H:%M:%S"),
            "days": self.days,
            "amount": self.amount,
            "status": self.status,
            "comment": self.comment if self.comment else ""
        }
        return order_dict

