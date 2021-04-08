from Library.PyWeChatSpy import WeChatSpy
from Library.PyWeChatSpy.command import *
from lxml import etree
import time
import logging
from logging.handlers import TimedRotatingFileHandler
from Library.PyWeChatSpy.proto import spy_pb2
import os
import pymysql
import datetime
import shutil
from queue import Queue
from Library.PyWeChatSpy.games.truth_or_dare import TruthOrDare
from Config.wx import *
from Config.database import *


logger = logging.getLogger(__file__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s [%(threadName)s] %(levelname)s: %(message)s')
sh = logging.StreamHandler()
sh.setFormatter(formatter)
sh.setLevel(logging.INFO)
fh = TimedRotatingFileHandler("Logs/spy.log", when="midnight")
fh.setFormatter(formatter)
logger.addHandler(fh)
logger.addHandler(sh)


if not os.path.exists(WECHAT_PROFILE):
    logger.error("请先设置计算机用户名，并完善WECHAT_PROFILE和PATCH_PATH")
    exit()
if os.path.isdir(PATCH_PATH):
    shutil.rmtree(PATCH_PATH)
if not os.path.exists(PATCH_PATH):
    with open(PATCH_PATH, "a") as wf:
        wf.write("")
my_response_queue = Queue()
spy = WeChatSpy(response_queue=my_response_queue, key="ab28d8c4768ab3bc2ba86841313f6e32", logger=logger)
tod = TruthOrDare(spy)


def pop_response():
    while True:
        data = my_response_queue.get()
        handle_response(data)

        if has_login:
            # 微信机器人的核心部分
            robot_list = execute("SELECT id, admin_id, content FROM tb_wx_robot WHERE type = 'j2u' AND is_done = 0")
            for robot in robot_list:
                execute("UPDATE tb_wx_robot SET is_done = 1, update_time = '{}' WHERE id = {}"
                        .format(now_format, robot[0]))
                spy.send_text(admin_list[robot[1]], robot[2])


def handle_response(data):
    if data.type == PROFESSIONAL_KEY:
        if not data.code:
            logger.warning(data.message)
    elif data.type == WECHAT_CONNECTED:  # 微信接入
        print(f"微信客户端已接入 port:{data.port}")
        time.sleep(1)
        # spy.get_login_qrcode()  # 获取登录二维码
    elif data.type == HEART_BEAT:  # 心跳
        pass
    elif data.type == WECHAT_LOGIN:  # 微信登录
        print("微信登录")
        spy.get_account_details()  # 获取登录账号详情
        global has_login
        has_login = True
    elif data.type == WECHAT_LOGOUT:  # 微信登出
        print("微信登出")
    elif data.type == CHAT_MESSAGE:  # 微信消息
        chat_message = spy_pb2.ChatMessage()
        chat_message.ParseFromString(data.bytes)
        for message in chat_message.message:
            _type = message.type  # 消息类型 1.文本|3.图片...自行探索
            _from = message.wxidFrom.str  # 消息发送方
            _to = message.wxidTo.str  # 消息接收方
            content = message.content.str  # 消息内容
            if _type == 1:  # 文本消息
                print(_from, _to, content)
                # if _to == "filehelper":
                #     spy.send_text("wxid_xigdflxwillf21", "Hello PyWeChatSpy3.0 啊哈哈")
                #
                #     spy.send_text("filehelper", "Hello PyWeChatSpy3.0\n" + content)
                #     time.sleep(2)
                #     spy.send_file("filehelper", r"D:\Project\PyWeChatSpy\images\1.jpg")
            elif _type == 49:  # XML报文消息
                # print(_from, _to, message.file)
                xml = etree.XML(content)
                xml_type = xml.xpath("/msg/appmsg/type/text()")[0]
                if xml_type == "57":  # 引用
                    xml_title = xml.xpath("/msg/appmsg/title/text()")[0]  # 输入的内容
                    xml_refer_content = xml.xpath("/msg/appmsg/refermsg/content/text()")[0]  # 被引用内容
                    print(xml_title)
                    # print(xml_refer_content)
                    # 引用回复时，注入机器人任务（自动回复到pdd）
                    robots = execute("SELECT * FROM tb_wx_robot WHERE content = '{}' AND is_done = 1".
                                     format(xml_refer_content))
                    if robots and len(robots) > 0:
                        robot = robots[0]
                        print(robot)
                        execute("INSERT tb_wx_robot (type, admin_id, project_id, content, msg_to, "
                                "create_time, update_time) "
                                "VALUE ('u2j', {}, {}, '{}', '{}', '{}', '{}')"
                                .format(robot[2], robot[3], xml_title, robot[5], now_format, now_format))


# 数据库
def execute(sql):
    db = pymysql.connect(MYSQL['host'], MYSQL['user'], MYSQL['pass'], MYSQL['database'], charset='utf8')
    cursor = db.cursor()
    cursor.execute(sql)
    results = cursor.fetchall()
    db.close()
    return results


if __name__ == '__main__':
    admins = execute("SELECT id, wx_mark FROM tb_admin")
    admin_list = {}
    for i in admins:
        admin_list[i[0]] = i[1]

    now_format = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    has_login = False

    pid = spy.run(wx_exe_path)
    pop_response()
