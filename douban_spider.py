from DrissionPage import ChromiumPage
import pandas as pd
import time
import random

def crawl_douban_deep_loop():
    # 初始化浏览器对象（它会自动打开一个真实的 Chrome 浏览器窗口，你可以亲眼看到它在点来点去）
    page = ChromiumPage()
    
    all_books_data = []
    
    # 爬取前10页（这里先以1页做演示，全量跑完改 range(10)）
    for page_num in range(1):
        start_id = page_num * 25
        list_url = f'https://book.douban.com/top250?start={start_id}'
        print(f"\n====== 正在访问第 {page_num + 1} 页列表页 ======")
        
        page.get(list_url)
        time.sleep(2) # 等待列表页加载
        
        # 1. 对应【截图1 & 截图6】：找到当前页面所有图书的条目链接
        # 豆瓣 Top250 的图书标题链接包含在 class 为 pl2 的 div 下的 a 标签里
        book_links = page.eles('xpath://div[@class="pl2"]/a')
        
        # 记录下当前页所有书的跳转 URL，避免页面跳转后节点失效
        urls = [link.attr('href') for link in book_links]
        titles = [link.text for link in book_links]
        
        # 循环点击并穿透每一本书
        for i in range(len(urls)):
            book_title = titles[i].split('\n')[0].strip()
            detail_url = urls[i]
            
            print(f"🚀 正在模拟点击进入: 《{book_title}》...")
            
            # --- 【穿透步骤一：进入详情页】 ---
            page.get(detail_url)
            time.sleep(random.uniform(2.0, 3.5)) # 模拟真人停顿阅读
            
            # 2. 对应【截图2】：提取 id="info" 里的基本数据
            info_element = page.ele('#info')
            isbn = "未知"
            pages = "未知"
            if info_element:
                info_text = info_element.text
                for line in info_text.split('\n'):
                    if 'ISBN:' in line:
                        isbn = line.replace('ISBN:', '').strip()
                    if '页数:' in line:
                        pages = line.replace('页数:', '').strip()
            
            # 3. 对应【截图3】：提取内容简介
            # 优先找展开后的完整简介，找不到则拿常规简介
            intro_element = page.ele('.intro') or page.ele('#link-report')
            intro = intro_element.text.strip() if intro_element else "暂无简介"
            
            # --- 【穿透步骤二：挺进短评页】 ---
            # 4. 对应【截图4 & 截图5】：在页面中寻找“全部短评”的链接并点击跳转
            # 观察截图4，短评区域的头部通常带有 class="mod-hd" 或者可以直接用文本定位
            all_comments_link = page.ele('xpath://div[@id="comments-section"]//h2/span/a')
            
            comments_text_list = []
            if all_comments_link:
                print(f"   ↳ 正在往下滑动，点击进入短评页面...")
                all_comments_link.click() # 模拟真实鼠标点击
                time.sleep(random.uniform(4.0, 5.0))
                
                # 5. 对应【截图5】：提取短评页面中所有带有 class="short" 的用户发言
                comment_spans = page.eles('.short')
                # 收集这一页的前 5 条短评内容
                for span in comment_spans[:5]:
                    comments_text_list.append(span.text.strip())
            else:
                comments_text_list.append("未能成功跳转短评页")
                
            if not comments_text_list:
                all_books_data.append({
                    '书名': book_title,
                    'ISBN': isbn,
                    '页数': pages,
                    '内容简介': intro,
                    '热门短评内容': "暂无短评数据",  # 没评论时填入提示
                    '详情页URL': detail_url
                })
            else:
                # 如果有评论，遍历每一条评论，让它在 Excel 里单独占一行！
                for single_comment in comments_text_list:
                    all_books_data.append({
                        '书名': book_title,
                        'ISBN': isbn,
                        '页数': pages,
                        '内容简介': intro,
                        '热门短评内容': single_comment,  # ✨ 这里每次只填入“单条”评论
                        '详情页URL': detail_url
                    })

            print(f"✅ 《{book_title}》共 {len(comments_text_list)} 条短评平铺抓取完毕。")
            
            # --- 【退回最初界面】 ---
            # 自动化工具不需要像人一样苦哈哈地连点“后退”按钮
            # 每一个大循环开头，我们直接使用 page.get(list_url) 就能瞬间“重置”回最初的列表页！
            
            # 休息一下，防止操作太频繁被系统盯上
            time.sleep(random.uniform(1.5, 3.0))
            
    # 退出浏览器
    page.quit()
    return all_books_data
