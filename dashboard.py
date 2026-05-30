import streamlit as st
import pandas as pd
import jieba
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import re
from collections import Counter



# 解决中文乱码
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False

st.set_page_config(page_title="豆瓣短评文本挖掘看板", page_icon="💬", layout="wide")

st.title("💬 豆瓣图书短评文本挖掘与分析看板")
st.markdown("---")

# 1. 基础数据读取逻辑
@st.cache_data
def load_data():
    try:
        df = pd.read_excel('豆瓣图书Top250本地数据库.xlsx')
    except FileNotFoundError:
        # 如果用户第一次运行还没有 Excel，先生成一个空表格垫底，防止看板崩溃
        df = pd.DataFrame(columns=['书名', '热门短评内容', '短评字数'])
        
    df['热门短评内容'] = df['热门短评内容'].fillna('').astype(str)
    df['短评字数'] = df['热门短评内容'].apply(len)
    return df

df = load_data()

# 2. 侧边栏及交互控制
st.sidebar.header("🔍 数据筛选中心")

# 筛选书籍下拉菜单
book_list = ["全部书籍"] + list(df['书名'].unique()) if not df.empty else ["暂无书籍"]
selected_book = st.sidebar.selectbox("请选择要分析的图书：", book_list)

if selected_book == "全部书籍" or df.empty:
    filtered_df = df
else:
    filtered_df = df[df['书名'] == selected_book]

# 3. 顶层大盘看板指标
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="📚 当前分析书籍", value=selected_book)
with col2:
    st.metric(label="💬 收集短评总条数", value=f"{len(filtered_df)} 条")
with col3:
    avg_len = filtered_df['短评字数'].mean() if not filtered_df.empty else 0
    st.metric(label="✍️ 平均每条短评字数", value=f"{avg_len:.1f} 字")

st.markdown("---")

# 4. 文本挖掘核心可视化板块
if not filtered_df.empty and len(filtered_df['热门短评内容'].str.cat(sep='')) > 0:
    full_text = "".join(filtered_df['热门短评内容'].astype(str))
    full_text = re.sub(r'[^\w\s]', '', full_text)
    words = jieba.lcut(full_text)
    stop_words = {'的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '一部', '一个', '这', '那', '都', '看', '说', '感觉', '很', '觉得', '暂无短评数据'}
    clean_words = [w for w in words if len(w) > 1 and w not in stop_words]

    left_col, right_col = st.columns(2)
    with left_col:
        st.subheader("🔥 读者短评关键词云")
        if clean_words:
            plt.clf()  # 清空画布
            wc = WordCloud(
                font_path='/usr/share/fonts/truetype/wqy/wqy-microhei.ttc', # Mac 专用黑体
                background_color='white',
                width=600,
                height=400
            ).generate(" ".join(clean_words))
            fig, ax = plt.subplots()
            ax.imshow(wc, interpolation='bilinear')
            ax.axis('off')
            st.pyplot(fig)
        else:
            st.info("暂无足够数据生成词云")

    with right_col:
        st.subheader("📊 读者最常提及的词汇 Top 10")
        if clean_words:
            word_counts = Counter(clean_words)
            top_10 = word_counts.most_common(10)
            top_10_df = pd.DataFrame(top_10, columns=['词汇', '出现次数'])
            st.bar_chart(data=top_10_df, x='词汇', y='出现次数', color="#ff4b4b")
        else:
            st.info("暂无足够数据")
else:
    st.warning("📭 数据库空空如也，请点击左侧控制台按钮，启动爬虫同步数据！")

st.markdown("---")

# 5. 底部原始数据大表
st.subheader("📂 原始短评快照与检索")
search_keyword = st.text_input("💡 输入关键词过滤短评：")

if search_keyword and not filtered_df.empty:
    display_df = filtered_df[filtered_df['热门短评内容'].astype(str).str.contains(search_keyword)]
else:
    display_df = filtered_df

if not display_df.empty:
    st.dataframe(display_df[['书名', '热门短评内容', '短评字数']], use_container_width=True)
else:
    st.write("暂无匹配的数据")
