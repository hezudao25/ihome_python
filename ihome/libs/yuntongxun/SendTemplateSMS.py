#coding=utf-8

from .CCPRestSDK import REST

#主帐号
accountSid = '8a216da86b652116016b73a681c70b96'

#主帐号Token
accountToken = '80145772af7e4e1f99458765fe5c61a7'

#应用Id
appId = '8a216da86b652116016b73a682230b9d';

#请求地址，格式如下，不需要写http://
serverIP = 'app.cloopen.com'

#请求端口 
serverPort = '8883'

#REST版本号
softVersion = '2013-12-26'


# 发送模板短信
# @param to 手机号码
# @param datas 内容数据 格式为数组 例如：{'12','34'}，如不需替换请填 ''
# @param $tempId 模板Id
class CCP(object):
    """自己封装的发送短信的辅助类"""
    instance = None

    def __new__(cls):
        # 判度CCP类有没有已经创造好的对象
        if cls.instance is None:
            obj = super().__new__(cls)
            # 初始化REST SDK
            obj.rest = REST(serverIP, serverPort, softVersion)
            obj.rest.setAccount(accountSid, accountToken)
            obj.rest.setAppId(appId)
            cls.instance = obj

        return cls.instance

    def send_sms_code(self, to, datas, temp_Id):
        """"""
        result = self.rest.sendTemplateSMS(to, datas, temp_Id)

        # for k, v in result.items():
        #
        #     if k == 'templateSMS':
        #             for k, s in v.items():
        #                 print('%s:%s' % (k, s))
        #     else:
        #         print('%s:%s' % (k, v))
        return result.get('statusCode')

   
#sendTemplateSMS(手机号码,内容数据,模板Id)


