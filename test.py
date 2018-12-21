# -*- coding: utf-8 -*-
import json
import os
import re
import urllib.request
import urllib.parse
import random

from bs4 import BeautifulSoup
from slackclient import SlackClient
from flask import Flask, request, make_response, render_template

app = Flask(__name__)

slack_token = 'xoxb-503049869125-506766686128-5HMofP8PVjartOwuE42OyoN6'
slack_client_id = '503049869125.507496464770'
slack_client_secret = '9962138d7faf1f2bc3040426f0fdd4d5'
slack_verification = '2ghC35AnyEwdvhVbxiobtVWR'
sc = SlackClient(slack_token)


# 크롤링 함수 구현하기
def _crawl_naver_keywords(text):
    keywords = []
    # url = re.search(r'(https?://\S+)', text.split('|')[0]).group(0)
###############################################################################################################################################################


    url_decode = urllib.parse.quote(text)
    url = "https://m.cafe.naver.com/ArticleSearchList.nhn?search.query=" + url_decode + "&search.menuid=&search.searchBy=1&search.sortBy=date&search.clubid=10050146&search.option=0&search.defaultValue=1"


###############################################################################################################################################################

    if "중고나라" in text:
        url = "https://m.cafe.naver.com/joonggonara"


    elif "노트북" in text:
        url = "https://m.cafe.naver.com/ArticleSearchList.nhn?search.query=%EB%85%B8%ED%8A%B8%EB%B6%81&search.menuid=&search.searchBy=0&search.sortBy=date&search.clubid=10050146&search.option=0&search.defaultValue=1"
    elif "코트" in text:
        url = "https://m.cafe.naver.com/ArticleSearchList.nhn?search.query=%EC%BD%94%ED%8A%B8&search.menuid=&search.searchBy=1&search.sortBy=date&search.clubid=10050146&search.option=0&search.defaultValue=1"
    else:
        url = ""


    req = urllib.request.Request(url)
    sourcecode = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(sourcecode, "html.parser")

    # 함수를 구현해 주세요
    # keywords2 = []
    # merge=[]

    if "joong" in url:
        for data in (soup.find_all("strong", class_="tit")):
            if not data.get_text() in keywords:
                if len(keywords) >= 10:
                    break
                keywords.append(data.get_text().strip())

    elif "%EB%85%B8%ED%8A%B8%EB%B6%81" in url:
        for data in (soup.find_all("div", class_="item")):
            if not data.get_text() in keywords:
                if len(keywords) >= 10:
                    break
                keywords.append(data.get_text().strip() + "\n")

    elif "%EC%BD%94%ED%8A%B8" in url:
        for data in (soup.find_all("div", class_="item")):
            if not data.get_text() in keywords:
                if len(keywords) >= 10:
                    break
                keywords.append(data.get_text().strip() + "\n")

    # 한글 지원을 위해 앞에 unicode u를 붙혀준다.
    return u'\n'.join(keywords)


# 이벤트 핸들하는 함수
def _event_handler(event_type, slack_event):
    print(slack_event["event"])

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
    ran = random.randrange(0, 1000)

    slack_event = json.loads(request.data)

    if "challenge" in slack_event:
        return make_response(slack_event["challenge"], 200, {"content_type":
                                                                 "application/json"
                                                             })

    if slack_verification != slack_event.get("token"):
        message = "Invalid Slack verification token: %s" % (slack_event["token"])
        make_response(message, 403, {"X-Slack-No-Retry": 1})

    # if "event" in slack_event:
    #     print("이벤트 발생2!")
    #     event_type = slack_event["event"]["type"]
    #     return _event_handler(event_type, slack_event)

    if "event" in slack_event and slack_event["event"]["type"] == "app_mention":
        event_type = slack_event["event"]["type"]
        print("키워드 발생!")
        send_text = ""
        if "네고" in slack_event["event"]["text"]:
            send_text = "안됩니다."
        elif "비싸" in slack_event["event"]["text"]:
            bissa = ["뭐가 비싸!", "난 땅 파서 장사하니?", "사기 싫으면 사지 마!", "여기서나 팔지, 딴 데 가면 살 수 있냐?", "그렇지 않아도 신경질 나는데...",
                     "나도 지겨워...", "이정도면 싼 거지...", "총만 안 들었지 강도네..."]
            send_text = bissa[ran % len(bissa)]


        elif "도토리 다 판다" in slack_event["event"]["text"]:
            send_text = "도토리를 5전에 샀습니다."

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
    app.run('0.0.0.0', port=8080)
