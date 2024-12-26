# XJTU-Annual-Eat

一年过去了，你在洗脚食堂里花的钱都花在哪儿了？

## 项目简介

> 项目的 idea 来源于 [Rose-max111](https://github.com/Rose-max111)。
> 

本项目是一个用于统计洗脚大学学生校园卡消费情况的脚本。通过模拟登录大学校园卡网站，获取学生的校园卡消费记录，并通过数据可视化的方式展示。

本项目参考[THU-Annual-Eat](https://github.com/leverimmy/THU-Annual-Eat)，[PKU-Annual-Eat](https://github.com/zhuohaoyu/PKU-Annual-Eat)，感谢原作者的贡献。

![demo](./demo.png)

## 使用方法

### 0. 获取account和hallticket

首先，登录校园卡账号后，在[洗脚大学校园卡网站](http://card.xjtu.edu.cn/User/User)获取你的`account`和`hallticket`。方法如下：

![card](./card.png)

主页进入[个人中心](http://card.xjtu.edu.cn/)

点击`账号管理`，在弹出的页面中找到`账号`，复制其值。

![account](./account.png)

在我的账单页按`F12` 或者右键检查，打开开发者工具，切换到`Network`标签页，然后`Ctrl+R`刷新页面，找到 `GetMyBill` 这个请求，进入`Cookies`选项卡，复制其中`hallticket`字段的**value**，后面会用到。

![hallticket](./hallticket.png)

为方便大家使用，在服务器上部署了一个网页端供大伙点击即用：[洗脚大学食堂消费情况](http://39.100.102.17:8501/)  

如果要独立运行，参考以下两种方式

### 网页模式

基于streamlit实现的网页可视化，推荐 python 版本：`>=3.10`

#### 1. 安装依赖

```shell
pip install -r requirements_st.txt
```

#### 2. 运行页面

```shell
streamlit run app.py
```

#### 3. 填写个人信息生成报告

在侧边栏填入前面获取到的`account`和`hallticket`，点击生成报告按钮生成。
![](./st_page.jpg)

### 本地模式

#### 1. 安装依赖

本项目依赖于 `requests`、`matplotlib`，请确保你的 Python 环境中已经安装了这些库。

```bash
pip install -r requirements.txt
```

#### 2. 修改配置

项目根目录下新建 `config.json` 文件，内容如下，主要修改`account`或者`hallticket`，以及计算的起始和截止时间。

```json
{
    "account": "******",
    "hallticket": "*********",
    "sdate": "2024-01-01",
    "edate": "2024-12-31"
}
```

#### 3. 运行脚本

```bash
python main.py
```

#### 4. 查看结果
在result.png中显示了消费情况图，report.md中显示了较详细的消费统计报告(也可以在输出中查看)。
python运行时的图可能出现字体重叠和图片大小不合适的问题，建议直接看导出的result.png。

## LICENSE

除非另有说明，本仓库的内容采用 [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) 许可协议。在遵守许可协议的前提下，您可以自由地分享、修改本文档的内容，但不得用于商业目的。

如果您认为文档的部分内容侵犯了您的合法权益，请联系项目维护者，我们会尽快删除相关内容。
