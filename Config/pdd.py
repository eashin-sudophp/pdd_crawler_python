# 立即回复话术
reply_common = "亲您好，在的哦"

# 是否立即回复、循环的间隔秒数
reply_at_one = False
time_sleep = 3

# 定义角色
seller_role = 'mall_cs'
buyer_role = 'user'

# 最近联系人
talk_people_url = "https://mms.pinduoduo.com/plateau/chat/latest_conversations"
# 聊天框的最近聊天内容
talk_list_url = "https://mms.pinduoduo.com/plateau/chat/list"
# 发送聊天消息
send_msg_url = "https://mms.pinduoduo.com/plateau/chat/send_message"

# 上面不同接口请求结果中，主要数据标识
data_mark = {"latest_conversations": "conversations", "list": "messages", "send_message": "msg_id"}