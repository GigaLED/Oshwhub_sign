# Oshwhub_sign
 Automatic check-in for Oshwhub
## How to Run

添加如下环境变量

    OSHW

内容如下

    {"PhoneNumber1": "Password1","PhoneNumber2": "Password2", "PhoneNumbern": "Passwordn"}

还需要ChromeDriver，Windows的安装参考 [这里](https://blog.csdn.net/Z_Lisa/article/details/133307151)
下载地址在 [这里](https://googlechromelabs.github.io/chrome-for-testing/)

Qinglong安装

    apk add chromium
    apk add chromium-chromedriver

然后就可以运行了

还有个notify模块可以推送消息

### 已实现
- [x] 自动签到
- [x] 识别奖励
- [x] 推送消息

### 待修正
- [x] 优惠券识别和计数不正常
- [x] 自动签到次数或天数不准确
- [x] 自动签到不会跳过已签到
