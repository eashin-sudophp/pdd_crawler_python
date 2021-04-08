from Config.database import *
from Config.pdd import *
import datetime
import time
import requests
import json
import pymysql
import redis
import random

# cookie请去tb_project表中添加
cookie = ""
project_id = ""
admin_id = ""
project_type = ""

# sql语句
sql_all_project = "SELECT * FROM tb_project"
sql_project_mark = "SELECT id, login_mark FROM tb_project"
sql_exists_user = "SELECT * FROM tb_user WHERE user_mark = '{}' AND project_id = {}"
sql_insert_user = "INSERT tb_user (type, user_mark, project_id, create_time, update_time) " \
                  "values ('{}', '{}', {}, '{}', '{}')"
sql_exists_warning = "SELECT * FROM tb_warning WHERE content = '{}' AND project_id = {}"
sql_make_warning = "INSERT tb_warning (content, project_id, create_time, update_time) values ('{}', {}, '{}', '{}')"
sql_exists_robot = "SELECT * FROM tb_wx_robot WHERE content = '{}' AND project_id = {}"
sql_add_wx_robot = "INSERT tb_wx_robot (admin_id, content, msg_to, project_id, create_time, update_time) " \
                   "values ({}, '{}', '{}', {}, '{}', '{}')"
sql_need_reply = "SELECT id, project_id, msg_to, content FROM tb_wx_robot WHERE type = 'u2j' AND is_done = 0"
sql_done_robot = "UPDATE tb_wx_robot SET is_done = 1, update_time = '{}' WHERE id = {}"


# todo ############################ 功能函数 ###############################
# 获取header头
def getHeader(data):
    return {
        'Cookie': cookie,
        "content-length": str(getStrNum(data)),
        "Accept-Encoding": "gzip, deflate, br",
        "Content-Type": "application/json",
        "Accept": "*/*",
        "User-Agent": "PostmanRuntime/7.26.8"
    }


# 处理爬虫爬取的数据
def dataHandleRes(res):
    data_dict = json.loads(res)
    # 请求过期，如会话已过期
    if not data_dict['success']:
        raise Exception(data_dict['error_msg'])

    if "result" in data_dict and data_dict['result']:
        result = data_dict['result']
        if "result" in result and result["result"] != "ok":
            raise Exception(result['error'])  # 如“买家回复前，您不能继续发送消息”

        response = result["response"] if result["response"] != "" else "latest_conversations"
        if response not in data_mark:
            raise Exception("异常的response:" + response)

        major_data_mark = data_mark[response]
        if major_data_mark not in result:
            raise Exception("异常的mark:" + major_data_mark)
        return result[major_data_mark]


# 获取最近联系人后的业务处理
def handleLatestTalkPeople(data):
    for i, row in enumerate(data):
        # 记录tb_user
        if row['from']['role'] == buyer_role:
            uid = row['from']['uid']
        elif row['to']['role'] == buyer_role:
            uid = row['to']['uid']
        else:
            uid = ''
        if uid:
            if not execute(sql_exists_user.format(uid, project_id)):
                # 入库tb_user
                execute(sql_insert_user.format(project_type, uid, project_id, now_format, now_format))
                exit()

        # 添加异步消息发送任务
        if row['from']['role'] == buyer_role and row['to']['role'] == seller_role:
            # 第 i+1 个最近联系人等待回复
            ts = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(row['ts'])))
            content = "第{}个最近联系人({})等待回复: {} -- {}".format(i + 1, row['from']['uid'], row['content'], ts)
            make_warning(content, row['from']['uid'])
            if reply_at_one:
                sendTalkMsg(reply_common, row['from']['uid'])

        # 只读10条
        if i >= 9:
            break
    return True


# todo ############################ 爬虫相关 ###############################
# 获取某个用户的聊天内容
def getLatestTalk(uid):
    data = {"data": {"cmd": "list", "list": {"with": {"id": uid}}}, "client": "web"}
    headers = getHeader(data)
    res = requests.post(talk_list_url, data=json.dumps(data), headers=headers).text
    return res


# 获取最近联系人列表
def getLatestTalkPeople():
    data = {"data": {"offset": 0, "size": 50}, "client": 1}
    headers = getHeader(data)
    res = requests.post(talk_people_url, data=json.dumps(data), headers=headers).text
    return res


# 给指定联系人发送消息
def sendTalkMsg(msg, uid):
    data = {
        "data": {
            "cmd": "send_message",
            "message": {
                "content": msg,
                "from": {"role": seller_role},
                "type": 0,
                "to": {"role": buyer_role, "uid": uid},
                "ts": int(time.time())
            }
        },
        "client": "web"
    }
    headers = getHeader(data)
    res = requests.post(send_msg_url, data=json.dumps(data), headers=headers).text
    return res


# todo ############################ 辅助功能 ###############################
# 获取字典的字符数
def getStrNum(dict_str):
    return len(json.dumps(dict_str).replace(' ', ''))


# 获取随机数
def getRandint(big=9):
    return random.randint(0, big)


# 数据库
def execute(sql):
    db = pymysql.connect(MYSQL['host'], MYSQL['user'], MYSQL['pass'], MYSQL['database'], charset='utf8')
    cursor = db.cursor()
    cursor.execute(sql)
    results = cursor.fetchall()
    db.close()
    return results


# redis
def rds(name, value='', p_time=0):
    r = redis.Redis(host=REDIS['host'], port=REDIS['port'], db=0)
    if value == '':
        return r.get(name).decode('utf-8')
    else:
        return r.setex(name, value, p_time)


# todo ############################ 其他 ###############################
# 预警
def make_warning(content, msg_to):
    # todo 发微信消息
    if not execute(sql_exists_robot.format(content, project_id)):
        execute(sql_add_wx_robot.format(admin_id, content, msg_to, project_id, now_format, now_format))
    # todo 发短信
    # todo 发邮件
    if not execute(sql_exists_warning.format(content, project_id)):
        execute(sql_make_warning.format(content, project_id, now_format, now_format))
    return True


def getMarkList():
    marks = execute(sql_project_mark)
    mark_list = {}
    for i in marks:
        mark_list[i[0]] = i[1]
    return mark_list


def makeGlobalData(project):
    global cookie, project_id, admin_id, project_type
    cookie = project[2]
    project_id = project[0]
    admin_id = project[1]
    project_type = project[5]
    return True


def main():
    try:
        mark_list = getMarkList()
        while True:
            # 机器人回复客户
            robot_list = execute(sql_need_reply)
            for robot in robot_list:
                execute(sql_done_robot.format(now_format, robot[0]))
                global cookie
                cookie = mark_list[robot[1]]
                sendTalkMsg(robot[3], robot[2])

            if getRandint() > 7:  # 20%的概率跑以下逻辑
                # 监听最近联系人以获取待回复信息
                projects = execute(sql_all_project)
                for project in projects:
                    makeGlobalData(project)

                    # 跑接口（获取最近联系人）并处理得到结果
                    res_json = getLatestTalkPeople()
                    data = dataHandleRes(res_json)
                    # 业务处理上述结果，发送预警消息
                    handleLatestTalkPeople(data)

            time.sleep(time_sleep)
    except Exception as e:
        # print(e)
        raise e


if __name__ == '__main__':
    now_format = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    main()
