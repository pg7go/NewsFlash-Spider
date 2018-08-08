from urllib.parse import urlencode

import re
import json

from config import *
from pyquery import PyQuery as py
import zhihu_login

session=zhihu_login.session

def get_page(index,count):
    data={
        'include': 'data[*].admin_closed_comment,comment_count, suggest_edit, is_title_image_full_screen, can_comment, upvoted_followees, can_open_tipjar, can_tip, voteup_count, voting, topics, review_info, author.is_following',
        'limit': count,
        'offset': index
    }
    HEADERS = {
        'User-Agent': AGENT
    }

    params=urlencode(data)
    try:
        response=session.get(URL,params=params,headers=HEADERS)
        if response.status_code==200:
            print('成功找到索引页,获取',count,'条文章')
            return  response.text
        print('无法打开此网页 code:',response.status_code,'url:',response.url)
        return None
    except ConnectionError:
        print('无法打开此网页，连接出错')
        return None

def get_detail_page(pageUrl):
    HEADERS = {
        'User-Agent': AGENT
    }
    try:
        response=session.get(pageUrl,headers=HEADERS)
        if response.status_code==200:
            print('成功获取详情页:',response.url)
            return  response.text
        print('无法打开此网页 code:',response.status_code,'url:',response.url,'pageUrl:',pageUrl)
        return None
    except ConnectionError:
        print('无法打开此网页，连接出错')
        return None

def parse_detail_page(html):
    if html:
        doc=py(html)
        #找到关键内容
        doc=doc('.RichText.ztext.Post-RichText')
        #去除图片
        doc=doc.remove('figure')
        #提取文字
        text=doc.text()
        #去除广告
        result=re.match('(新资讯.*?)更多内容请关注',text,re.S)
        if result:
            return result[1]
        else:
            return text
    return None


def parse_page(html):
    if html:
        data=json.loads(html)
        if data and 'data' in data.keys():
            data=data.get('data')
            for item in data:
                result=re.search('.*?(\d+)',item.get('title'))
                if result:
                    yield {
                        'date':result.group(1),
                        'url':item.get('url')
                    }

    return None

def get_one_news(page):
    if page:
        text = parse_detail_page(get_detail_page(page.get('url')))
        if text:
            return {
                'date':page.get('date'),
                'data':text
            }
    return None

def get_latest_news():
    if not zhihu_login.login():
        print('无法爬取！')
        return None
    data = parse_page(get_page(0, 1))
    return get_one_news(next(data))

def get_news(index,count):
    if not zhihu_login.login():
        print('无法爬取！')
        return None
    data = parse_page(get_page(index, count))
    for item in data:
        yield get_one_news(item)


def main():
    for item in get_news(10,10):
        print (item)

if __name__=='__main__':
    main()


