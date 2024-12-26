import json
import matplotlib.pyplot as plt
import requests
import platform
from datetime import datetime, timedelta
import seaborn as sns
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

# 使用streamlit来呈现上面的图表和数据
st.set_page_config(page_title="洗脚大学食堂消费情况", page_icon="🍚", layout="wide")
st.title("洗脚大学食堂消费情况")
st.write("数据来源：洗脚大学食堂")

# 使用cookie存储account和hallticket
if "account" not in st.session_state:
    st.session_state["account"] = ""

if "hallticket" not in st.session_state:
    st.session_state["hallticket"] = ""

if "sdate" not in st.session_state:
    st.session_state["sdate"] = "2024-01-01"

if "edate" not in st.session_state:
    st.session_state["edate"] = "2024-12-31"

def generate_report(account, hallticket, sdate, edate):
    all_data = dict()
    week_data = dict()
    day_data = dict()
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
    try:
        data = json.loads(response.text)["rows"]
    except:
        st.error("消费数据获取失败，请检查账户信息是否正确")
        return 
    
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
    
    st.write(f"总种类数：{len(all_data)}, 总消费次数：{len(data)}, 总消费金额：{round(sum(all_data.values()), 1)}元")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.write(f"""
    ### 最高消费
    - 商户：{max_consumption['MERCNAME']}
    - 金额: {round(max_consumption['TRANAMT'], 1)}元
    ### 最低消费
    - 商户：{min_consumption['MERCNAME']}
    - 金额: {round(min_consumption['TRANAMT'], 1)}元
                 """)
    
    with col2:
        st.write(f"""
    ### 最高天消费
    - 日期：{max(day_data, key=day_data.get)}
    - 金额：{round(max(day_data.values()), 1)}元
    ### 最低天消费
    - 日期：{min(day_data, key=day_data.get)}
    - 金额：{round(min(day_data.values()), 1)}元
                 """)
    
    with col3:
        st.write(f"""
    ### 最高周消费
    - 周一日期：{max(week_data, key=week_data.get)}
    - 金额：{round(max(week_data.values()), 1)}元
    ### 最低周消费
    - 周一日期：{min(week_data, key=week_data.get)}
    - 金额：{round(min(week_data.values()), 1)}元
    """)
    
    with col4:
        st.write(f"""
    ### 最早消费
    - 时间：{earliest_consumption['OCCTIME']} {earliest_consumption['MERCNAME']}
    - 金额：{earliest_consumption['TRANAMT']}元
    ### 最晚消费
    - 时间：{latest_consumption['OCCTIME']} {latest_consumption['MERCNAME']}
    - 金额：{latest_consumption['TRANAMT']}元
    """)
        
    if platform.system() == "Darwin":
        plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']
    elif platform.system() == "Linux":
        plt.rcParams['font.family'] = ['Droid Sans Fallback', 'DejaVu Sans']
    else:
        plt.rcParams['font.sans-serif'] = ['SimHei']
    
    gc1, gc2 = st.columns(2)
    # 绘制图表
    with gc1:
        fig = plt.figure(figsize=(12, len(all_data) / 66 * 18))
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
        st.pyplot(fig)
    
    with gc2:
    
        col1, col2 = st.columns(2)
        colors = ['gold', 'mediumturquoise', 'darkorange']
        with col1:
            # 使用plotly绘制三餐消费次数饼图
            pie_fig = px.pie(values=[bre_lun_din["breakfast_count"], bre_lun_din["lunch_count"], bre_lun_din["dinner_count"]],
                            names=["早餐", "午餐", "晚餐"],
                            title=f"三餐消费次数\n({post_data['sdate']} 至 {post_data['edate']})",)
            pie_fig.update_traces(textinfo='label+percent', insidetextorientation='radial',
                                marker=dict(colors=colors, line=dict(color='#000000', width=2)))
            st.plotly_chart(pie_fig)
        with col2:
            # 使用plotly绘制三餐消费金额饼图
            pie_fig = px.pie(values=[bre_lun_din["breakfast_cost"], bre_lun_din["lunch_cost"], bre_lun_din["dinner_cost"]],
                            names=["早餐", "午餐", "晚餐"],
                            title=f"三餐消费金额（元）\n({post_data['sdate']} 至 {post_data['edate']})")
            pie_fig.update_traces(textinfo='label+percent', insidetextorientation='radial',
                                marker=dict(colors=colors, line=dict(color='#000000', width=2)))
            st.plotly_chart(pie_fig)
        
        # 绘制周消费折线柱状图
        bar_colors = [
        '#A6CEE3',  # 浅蓝色
        '#FDBF6F',  # 浅橙色
        '#B2DF8A',  # 浅绿色
        '#FB9A99',  # 浅红色
        '#CAB2D6',  # 浅紫色
        '#FDD9B5',  # 浅棕色
        '#FCCDE5'   # 浅粉色
        ]
        days = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        values = list(weekdays_consumption.values())
        fig = go.Figure(data=[go.Bar(x=days, y=values, marker_color=bar_colors)])
        fig.add_trace(go.Scatter(x=days, y=values, name='消费趋势', mode='lines+markers', 
                            line=dict(color='#ff7f0e', width=3),  # 橙色线条
                            marker=dict(size=8, color='#ff7f0e')))  # 橙色数据点
        fig.update_layout(title_text=f"周消费统计\n({post_data['sdate']} 至 {post_data['edate']})")
        st.plotly_chart(fig)

def update_info(account, hallticket, sdate, edate):
    st.session_state.account = account
    st.session_state.hallticket = hallticket
    st.session_state.sdate = sdate
    st.session_state.edate = edate
    st.info("个人账户信息已更新")


with st.sidebar:
    st.write(" account 和 hallticket 获取方法：https://github.com/wangerforcs/XJTU-Annual-Eat")
    account = st.text_input("请输入account", value=st.session_state.account)
    hallticket = st.text_input("请输入hallticket", value=st.session_state.hallticket)
    sdate = st.text_input("请输入起始日期", value=st.session_state.sdate)
    edate = st.text_input("请输入结束日期", value=st.session_state.edate)
    st.button("生成报告", on_click=update_info, args=(account, hallticket, sdate, edate))
    
    
    account = st.session_state.account
    hallticket = st.session_state.hallticket
    sdate = st.session_state.sdate
    edate = st.session_state.edate
    
if account == "" or hallticket == "" or sdate == "" or edate == "":
    st.warning("请填写个人账户信息")
    st.stop()
else:
    generate_report(account, hallticket, sdate, edate)
