import json
import matplotlib.pyplot as plt
import requests
import platform
from datetime import datetime, timedelta
import seaborn as sns

account = ""
hallticket = ""
sdate = "2024-01-01"
edate = "2024-12-31"
all_data = dict()
week_data = dict()
day_data = dict()

if __name__ == "__main__":
    # 读入账户信息
    try:
        with open("config.json", "r", encoding='utf-8') as f:
            config = json.load(f)
            account = config["account"]
            hallticket = config["hallticket"]
            sdate = config.get("sdate", '2024-01-01')
            edate = config.get("edate", '2024-12-31')
    except Exception as e:
        print("账户信息读取失败，请重新输入")
        account = input("请输入account: ")
        hallticket = input("请输入hallticket: ")
        with open("config.json", "w", encoding='utf-8') as f:
            json.dump({"account": account, "hallticket": hallticket, 'sdate': '2024-01-01', 'edate': '2024-12-31'}, f, indent=4)

    def is_valid_date(date_str):
        """检查日期是否符合YYYY-MM-DD格式且为有效日期"""
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False
    def format_date(date_str):
        """确保日期始终以两位数显示月份和日期"""
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        return date_obj.strftime("%Y-%m-%d")  # 格式化为YYYY-MM-DD

    url = f"http://card.xjtu.edu.cn/Report/GetMyBill"
    cookie = {
        "hallticket": hallticket,
    }
    post_data = {
        "sdate": sdate,
        "edate": edate,
        "account": account,
        "page": "1",
        "rows": "9000",
    }
    response = requests.post(url, cookies=cookie, data=post_data)

    data = json.loads(response.text)["rows"]
    
    # 保存到文件
    # with open("data.json", "w", encoding='utf-8') as f:
    #     json.dump(data, f, indent=4)

    max_consumption = {'MERCNAME': '', 'TRANAMT': 0}
    min_consumption = {'MERCNAME': '', 'TRANAMT': float('inf')}
    earliest_consumption = {'OCCTIME': '2024-01-01 23:59:59', 'MERCNAME': '', 'TRANAMT': float('inf')}
    latest_consumption = {'OCCTIME': '2024-01-01 00:00:00', 'MERCNAME': '', 'TRANAMT': 0}
    weekdays_consumption = {i: 0 for i in range(7)}  # 0: 周一, 6: 周日
    bre_lun_din = {"breakfast_count": 0, "breakfast_cost": 0, "lunch_count": 0, "lunch_cost": 0, "dinner_count": 0, "dinner_cost": 0}
    
    # 整理数据
    # MERNAME: 商户名称 TRANNUM: 交易方式 TRANAMT: 交易金额
    for item in data:
        try:
            if(item["TRANAMT"] < 0):
                tranamt = abs(item["TRANAMT"])
                
                if item["MERCNAME"].strip() in all_data:
                    all_data[item["MERCNAME"].strip()] += tranamt
                else: 
                    all_data[item["MERCNAME"].strip()] = tranamt
                
                time = datetime.strptime(item["OCCTIME"], "%Y-%m-%d %H:%M:%S")
                if time.time() < datetime.strptime("10:00:00", "%H:%M:%S").time():
                    bre_lun_din["breakfast_count"] += 1
                    bre_lun_din["breakfast_cost"] += tranamt
                elif time.time() < datetime.strptime("14:00:00", "%H:%M:%S").time():
                    bre_lun_din["lunch_count"] += 1
                    bre_lun_din["lunch_cost"] += tranamt
                else:
                    bre_lun_din["dinner_count"] += 1
                    bre_lun_din["dinner_cost"] += tranamt
                aligned_time_day = time.strftime('%Y-%m-%d')
                if aligned_time_day in day_data:
                    day_data[aligned_time_day] += tranamt
                else:
                    day_data[aligned_time_day] = tranamt
                
                aligned_time = time - timedelta(days=time.weekday())
                aligned_time_day = aligned_time.strftime('%Y-%m-%d')
                if aligned_time_day in week_data:
                    week_data[aligned_time_day] += tranamt
                else:
                    week_data[aligned_time_day] = tranamt
                
                item["TRANAMT"] = abs(item["TRANAMT"])
                if tranamt > max_consumption['TRANAMT']:
                    max_consumption = item
                if tranamt < min_consumption['TRANAMT']:
                    min_consumption = item
                
                occtime = datetime.strptime(item["OCCTIME"], "%Y-%m-%d %H:%M:%S")
                earliest_occtime = datetime.strptime(earliest_consumption["OCCTIME"], "%Y-%m-%d %H:%M:%S")
                latest_occtime = datetime.strptime(latest_consumption["OCCTIME"], "%Y-%m-%d %H:%M:%S")
                if occtime.time() < earliest_occtime.time():
                    earliest_consumption = item
                if occtime.time() > latest_occtime.time():
                    latest_consumption = item

                weekday = datetime.strptime(item["EFFECTDATE"], "%Y-%m-%d %H:%M:%S").weekday()
                weekdays_consumption[weekday] += tranamt
        except Exception as e:
            print(e)
            pass
    all_data = {k: round(v, 2) for k, v in all_data.items()}
    summary = f"统计总种类数：{len(all_data)}\n总消费次数：{len(data)}\n总消费金额：{round(sum(all_data.values()), 1)}"
    
    # 输出结果
    all_data = dict(sorted(all_data.items(), key=lambda x: x[1], reverse=True))
    # if len(all_data) > 50:
    #     # Get top 40 and bottom 10
    #     bottom_10 = dict(list(all_data.items())[:10])
    #     top_40 = dict(list(all_data.items())[-40:])
    #     # Add a separator between top and bottom groups
    #     middle_values = list(all_data.values())[10:-40]
    #     separator = {"中间部分消费总额": round(sum(middle_values), 2)}  # Sum of middle values
    #     all_data = {**bottom_10, **separator, **top_40}
    
    if platform.system() == "Darwin":
        plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']
    elif platform.system() == "Linux":
        plt.rcParams['font.family'] = ['Droid Sans Fallback', 'DejaVu Sans']
    else:
        plt.rcParams['font.sans-serif'] = ['SimHei']
        
    plt.figure(figsize=(12, len(all_data) / 66 * 18))
    sns.barplot(x=list(all_data.values()), y=list(all_data.keys()), hue=list(all_data.keys()))
    # plt.barh(list(all_data.keys()), list(all_data.values()))
    for index, value in enumerate(list(all_data.values())):
        plt.text(value + 0.01 * max(all_data.values() or [0]),
                index,
                str(value),
                va='center')
        
    # plt.tight_layout()
    plt.xlim(0, 1.2 * max(all_data.values() or [0]))
    plt.title(f"洗脚大学食堂消费情况\n({post_data['sdate']} 至 {post_data['edate']})")
    plt.xlabel("消费金额（元）")
    plt.text(0.8, 0.1, summary, ha='center', va='center', transform=plt.gca().transAxes)
    plt.savefig("result.png",bbox_inches='tight',dpi=300)
    plt.show()
    
    
    
    # 创建Markdown文件
    markdown_content = f"""
# 消费统计报告

## 消费概况
- 总种类数：{len(all_data)}
- 总消费次数：{len(data)}
- 总消费金额：{round(sum(all_data.values()), 1)}元

## 消费分布
- 早餐次数：{bre_lun_din["breakfast_count"]}次
- 早餐消费：{round(bre_lun_din["breakfast_cost"], 1)}元
- 午餐次数：{bre_lun_din["lunch_count"]}次
- 午餐消费：{round(bre_lun_din["lunch_cost"], 1)}元
- 晚餐次数：{bre_lun_din["dinner_count"]}次
- 晚餐消费：{round(bre_lun_din["dinner_cost"], 1)}元

## 最高消费
- 商户：{max_consumption['MERCNAME']}
- 金额: {round(max_consumption['TRANAMT'], 1)}元

## 最低消费
- 商户：{min_consumption['MERCNAME']}
- 金额: {round(min_consumption['TRANAMT'], 1)}元

## 最高天消费
- 日期：{max(day_data, key=day_data.get)}
- 金额：{round(max(day_data.values()), 1)}元

## 最低天消费
- 日期：{min(day_data, key=day_data.get)}
- 金额：{round(min(day_data.values()), 1)}元

## 最高周消费
- 周一日期：{max(week_data, key=week_data.get)}
- 金额：{round(max(week_data.values()), 1)}元

## 最低周消费
- 周一日期：{min(week_data, key=week_data.get)}
- 金额：{round(min(week_data.values()), 1)}元

## 最早消费
- 时间：{earliest_consumption['OCCTIME']}
- 商户：{earliest_consumption['MERCNAME']}
- 金额：{earliest_consumption['TRANAMT']}元

## 最晚消费
- 时间：{latest_consumption['OCCTIME']}
- 商户：{latest_consumption['MERCNAME']}
- 金额：{latest_consumption['TRANAMT']}元

## 周消费统计
| 星期 | 消费金额（元） |
| ---- | ------------ |
"""
    for i, amount in weekdays_consumption.items():
        markdown_content += f"| 周{i+1} | {round(amount, 1)} |\n"
        
    print(markdown_content)

    markdown_content += "\n![消费情况图](result.png)"

    # 写入Markdown文件
    with open("report.md", "w", encoding='utf-8') as f:
        f.write(markdown_content)
        

