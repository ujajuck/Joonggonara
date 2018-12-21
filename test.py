# -*- coding: utf-8 -*-
import json
import os
import re
import urllib
import urllib.request
import urllib.parse
import random

from bs4 import BeautifulSoup
from slackclient import SlackClient
from flask import Flask, request, make_response, render_template

app = Flask(__name__)

slack_token = ''
slack_client_id = ''
slack_client_secret = ''
slack_verification = ''
sc = SlackClient(slack_token)

even = False
# local = False

# 크롤링 함수 구현하기

def _crawl_naver_keywords(text):
    keywords = []
    keywords2 = []
    merge = []
    url_list = []


    print(text)
    text2 = text.split()[1]
    print(text2)
    # url_decode2 = urllib.parse(text2)
    # print(url_decode2)


    # if "경상" in text:
    #     print("경상")
    #     print(local)
    #     if local == True :
    #         print("직거래 모드")

    # if local is True:
    #     url="https://m.cafe.naver.com/ArticleList.nhn?search.clubid=10050146&search.menuid=1755&search.boardtype=L"


    if "최신"  in text2:
        url = "https://m.cafe.naver.com/joonggonara"
        even = False

    elif "이벤" in text2:
        url = "https://m.cafe.naver.com/joonggonara"
        even = True




    elif "노트북" in text2:
        url = "https://m.cafe.naver.com/ArticleSearchList.nhn?search.query=%EB%85%B8%ED%8A%B8%EB%B6%81&search.menuid=&search.searchBy=0&search.sortBy=date&search.clubid=10050146&search.option=0&search.defaultValue=1"
    elif "코트" in text2:
        url = "https://m.cafe.naver.com/ArticleSearchList.nhn?search.query=%EC%BD%94%ED%8A%B8&search.menuid=&search.searchBy=1&search.sortBy=date&search.clubid=10050146&search.option=0&search.defaultValue=1"
    elif "폰" in text2:
        url = "https://m.cafe.naver.com/ArticleSearchList.nhn?search.query=%ED%9C%B4%EB%8C%80%ED%8F%B0&search.menuid=&search.searchBy=1&search.sortBy=date&search.clubid=10050146&search.option=0&search.defaultValue=1"
    elif "냉장고" in text2:
        url = "https://m.cafe.naver.com/ArticleSearchList.nhn?search.query=%EB%83%89%EC%9E%A5%EA%B3%A0&search.menuid=&search.searchBy=1&search.sortBy=date&search.clubid=10050146&search.option=0&search.defaultValue=1"
    elif "신발" in text2:
        url = "https://m.cafe.naver.com/ArticleSearchList.nhn?search.query=%EC%8B%A0%EB%B0%9C&search.menuid=&search.searchBy=1&search.sortBy=date&search.clubid=10050146&search.option=0&search.defaultValue=1"

    else:
        url = ""

    req = urllib.request.Request(url)
    sourcecode = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(sourcecode, "html.parser")




    def m_cafe_data_crawl():
        #href 링크 가져오기
        for i in soup.find("div", id="articleList").find_all("li"):
            url_list.append("https://m.cafe.naver.com" + i.find("a")["href"] + "\n")

        for data in (soup.find_all("div", class_="item")):
            if not data.get_text() in keywords:
                if len(keywords) >= 15:
                    break
                keywords.append(data.get_text().strip() + "\n")

        for i in range(0, 10):
            merge.append(keywords[i] + url_list[i])

    #중고나라
    if "joong" in url:
        i=0
        #중고나라 최신글
        if even==False:
            for data in (soup.find_all("strong", class_="tit")):
                if not data.get_text() in keywords:
                    i+=1
                    if len(merge) >= 10:
                        break
                    if i>4 :
                        merge.append(data.get_text().strip())
            merge.append("https://m.cafe.naver.com/joonggonara")

        #중고나라 이벤트
        else :
            for data in (soup.find_all("strong", class_="tit")):
                if not data.get_text() in keywords:
                    if len(merge) >= 4:
                        break
                    merge.append(data.get_text().strip())
            merge.append("https://m.cafe.naver.com/ArticleList.nhn?search.clubid=10050146&search.menuid=1785")

    #노트북
    elif "%EB%85%B8%ED%8A%B8%EB%B6%81" in url:
        m_cafe_data_crawl()
    #코트
    elif "%EC%BD%94%ED%8A%B8" in url:
        m_cafe_data_crawl()
    #휴대폰
    elif "%ED%9C%B4%EB%8C%80%ED%8F%B0" in url:
        m_cafe_data_crawl()
    #냉장고
    elif "%EB%83%89%EC%9E%A5%EA%B3%A0" in url:
        m_cafe_data_crawl()
    # 신발
    elif "%EC%8B%A0%EB%B0%9C" in url:
        m_cafe_data_crawl()




    # 한글 지원을 위해 앞에 unicode u를 붙혀준다.
    for m in merge:
        print(m)

    return u'\n'.join(merge)


# 이벤트 핸들하는 함수
def _event_handler(event_type, slack_event):
    #print(slack_event["event"])

    if event_type == "app_mention":
        channel = slack_event["event"]["channel"]
        text = slack_event["event"]["text"]

        keywords = _crawl_naver_keywords(text)
        sc.api_call(
            "chat.postMessage",
            channel=channel,
            text=keywords
        )

        return make_response("App mention message has been sent", 200, )

    # ============= Event Type Not Found! ============= #
    # If the event_type does not have a handler
    message = "You have not added an event handler for the %s" % event_type
    # Return a helpful error message
    return make_response(message, 200, {"X-Slack-No-Retry": 1})


@app.route("/listening", methods=["GET", "POST"])
def hears():
    ran = random.randrange(0, 100)

    slack_event = json.loads(request.data)

    if "challenge" in slack_event:
        return make_response(slack_event["challenge"], 200, {"content_type":
                                                                 "application/json"
                                                             })

    if slack_verification != slack_event.get("token"):
        message = "Invalid Slack verification token: %s" % (slack_event["token"])
        make_response(message, 403, {"X-Slack-No-Retry": 1})

    #봇 호출 이벤트 발생시 반응
    if "event" in slack_event and slack_event["event"]["type"] == "app_mention":
        event_type = slack_event["event"]["type"]
        send_text = ""

        if "네고" in slack_event["event"]["text"]:
            send_text = "안됩니다."

        elif "비싸" in slack_event["event"]["text"]:
            bissa = ["뭐가 비싸!", "난 땅 파서 장사하니?", "사기 싫으면 사지 마!", "여기서나 팔지, 딴 데 가면 살 수 있냐?", "그렇지 않아도 신경질 나는데...", "나도 지겨워...", "이정도면 싼 거지...", "총만 안 들었지 강도네..."]
            send_text = bissa[ran % len(bissa)]

        elif "안비싸" in slack_event["event"]["text"]:
            send_text = "그치? ^^"

        elif "심심"  in slack_event["event"]["text"]:
            simsim = ["난 심심이가 아니야...", "밖에 좀 나가!", "롤 한 판 할래?"]
            send_text = simsim[ran % len(simsim)]

        elif "기능" in slack_event["event"]["text"]:
            send_text = "[중고로운 평화나라]\n\n기능 \n - 최신글 보기   예시)최신\n - 이벤트 보기   예시)이벤트\n - 키워드 검색   예시)노트북\n - 대화하기        예시)비싸"


        elif "도토리 다 판다" in slack_event["event"]["text"]:
            send_text = "도토리를 5전에 샀습니다."


        # elif "직거래" in slack_event["event"]["text"]:
        #     send_text = "지역을 입력해 주세요.  예시)경상 직거래"
        #     if "대구" in slack_event["event"]["text"]:
        #          global local
        #          local=True

        #위 키워드목록에 없으면 크롤링
        else:
            return _event_handler(event_type, slack_event)

        sc.api_call(
            "chat.postMessage",
            channel=slack_event["event"]["channel"],
            text=send_text
        )
        return make_response("App mention message has been sent", 200, )

    # If our bot hears things that are not events we've subscribed to,
    # send a quirky but helpful error response
    return make_response("[NO EVENT IN SLACK REQUEST] These are not the droids\
                         you're looking for.", 404, {"X-Slack-No-Retry": 1})


@app.route("/", methods=["GET"])
def index():
    return "<h1>Server is ready.</h1>"


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000)
