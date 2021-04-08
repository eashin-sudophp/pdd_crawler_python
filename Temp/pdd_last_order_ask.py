from selenium import webdriver
import time
import random

username = '13922453234'
password = '19950215Zwr'

selemiumConfig = {
    'link': "http://127.0.0.1:4444/wd/hub",
    'brower': {
        "browserName": "chrome",
        "version": "",
        "platform": "ANY",
    }
}

pdd_login_url = "https://mms.pinduoduo.com/login"

# xpath 规则
pdd_account_btn = "//div[contains(text(),'账户登录')]"
pdd_user_input = "//input[@id='usernameId']"
pdd_pass_input = "//input[@id='passwordId']"
pdd_login_btn = "//button/span[text()='登录']/.."


def brower():
    """
    :param config: 浏览器配置
    :return:
    """
    seleniumServer = selemiumConfig['link']
    browser = selemiumConfig['brower']
    driver = webdriver.Remote(command_executor=seleniumServer, desired_capabilities=browser)
    return driver


def browerSimple():
    return webdriver.Chrome(executable_path=r'D:\ProgramFiles\selenium-server\chromedriver.exe')


def rand(num=3):
    return int(random.random() * num)+1


# 获取某个节点
def getElement(xpath):
    try:
        return bw.find_element_by_xpath(xpath)
    except:
        return False


# 持续请求直到获取某个节点
def getElementAlive(xpath, sleep_sec=1, max_wait=10):
    wait = 0
    while wait < max_wait:
        ele = getElement(xpath)
        if ele is not False:
            time.sleep(sleep_sec * rand())  # 随机3秒再执行操作
            return ele
        time.sleep(sleep_sec)
        wait += 1
    exit("程序结束，未获取到节点：经过 {} 秒之后仍未获取到 {} 的节点".format(max_wait, xpath))


def main():
    bw.get(pdd_login_url)  # 打开登录页面
    getElementAlive(pdd_account_btn).click()  # 切换到账号密码登录
    getElementAlive(pdd_user_input).send_keys(username)  # 输入账号
    getElementAlive(pdd_pass_input).send_keys(password)  # 输入密码
    getElementAlive(pdd_login_btn).click()  # 点击登录


if __name__ == '__main__':
    bw = brower()
    bw.maximize_window()  # 最大化浏览器窗口
    main()
