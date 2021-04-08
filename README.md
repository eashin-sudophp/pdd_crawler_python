### python 同步拼多多客户聊天到微信，并可通过微信回复拼多多待回复消息



##### 启动项目

1. 安装`WeChatSetup-3.0.0.57.exe`；
2. 配置`Config/*.py`，主要是`mysql`、`redis`以及微信的配置信息；
3. 导入`Temp/crawler.sql`，配置`tb_admin`、`tb_project`；
4. 安装项目所需扩展；
5. 启动，双击`boot.bat`

> `tb_admin.wx_mark`字段是微信用户标识，可以通过启动`wx_robot.py`获取；`tb_project.login_mark`是拼多多接口cookie，当前只能在后台登录后手动获取，过期时间大约12 h - 24 h，过期之后需重新手动获取



##### 测试

1. 启动项目之后如下

   <img src=".\Temp\wx_robot_image\1.jpg" alt="" style="zoom: 100%;" />

2. 微信扫码登录微信机器人

   <img src=".\Temp\wx_robot_image\2.jpg" alt="" style="zoom: 100%;" />

3. 找一个拼多多用户，给拼多多店（需在tb_project添加并确保login_mark正确）发测试消息

   <img src=".\Temp\wx_robot_image\3.jpg" alt="" style="zoom: 50%;" />

4. 数秒之后，微信机器人给项目管理员微信发消息（格式及延迟秒数可定义），同时消息入库

   <img src=".\Temp\wx_robot_image\4.jpg" alt="" style="zoom: 100%;" />

   <img src=".\Temp\wx_robot_image\4-1.jpg" alt="" style="zoom: 100%;" />

5. 管理员微信中引用回复上述消息，回复的消息入库

   <img src=".\Temp\wx_robot_image\5.jpg" alt="" style="zoom: 100%;" />

   <img src=".\Temp\wx_robot_image\5-1.jpg" alt="" style="zoom: 100%;" />

6. 拼多多爬虫将回复的消息推送给用户

   <img src=".\Temp\wx_robot_image\6.jpg" alt="" style="zoom: 50%;" />



##### 资源参考：

https://github.com/veikai/PyWeChatSpy           下载WeChatSetup-3.0.0.57.exe也在这里









