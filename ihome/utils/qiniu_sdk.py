#coding=utf-8

from qiniu import Auth,put_data
import logging
from flask import jsonify
from .status_code import RET

def put_qiniu(f1):
    access_key = '6vvGPJ08BsHRjN7RRGVU3sEd38502x1TS0_i0x7s'
    secret_key = 'wzgWlHpflABi9DGn9TIb8IBRwqsZTwNJ--KZhosy'
    # 空间名称
    bucket_name = 'xun527'

    try:
        #构建鉴权对象
        q = Auth(access_key, secret_key)
        #生成上传Token
        token = q.upload_token(bucket_name)
        #上传文件数据，ret是字典，键是hash/key,值是新文件名，info是response对象
        ret, info = put_data(token, None, f1)
        return ret.get('key')
    except:
        logging.ERROR(u'访问七牛云出错')
        return jsonify(errno=RET.SERVERERR, errmsg="访问七牛云出错")