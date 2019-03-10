#!/usr/lib/python3.5

import requests
from bs4 import BeautifulSoup
import time
import datetime as dt

def get_user_session(id):
    url = 'http://student.cnsa.hs.kr/login/dupLoginCheck?loginId=' + id
    res = requests.get(url)
    return str(res.text)


def get_web_session_id(session):
    # header = {
    #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36',
    #     'Upgrade-Insecure-Requests': '1',
    #     'Connection': 'keep-alive',
    #     'Referer': 'https://student.cnsa.hs.kr/home',
    #     'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
    #     'Accept-Encoding': 'gzip, deflate, br'}
    res = session.post('http://student.cnsa.hs.kr/login/userLogin')
    print('WEB Session get : ' + res.cookies.get_dict().get('JSESSIONID'))
    print(res.text)
    return str(res.cookies.get_dict().get('JSESSIONID'))


def set_session(session):
    res = session.get('http://student.cnsa.hs.kr/login/userLogin')
    return str(res.cookies.get_dict().get('JSESSIONID'))


def attempt_login(sess, id, password, session_id):
    header = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36',
              'Upgrade-Insecure-Requests': '1',
              'Origin': 'https://student.cnsa.hs.kr',
              'Connection': 'keep-alive',
              'Host':'student.cnsa.hs.kr',
              'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
              'Referer': 'https://student.cnsa.hs.kr/login/userLogin',
              'Accept-Language':'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
              'Accept-Encoding':'gzip, deflate, br'}
    params = {'loginId' : id, 'loginPw': password, "pwMenuId":"", "pwMenuUrl":"", "trmnlIdntNo":"", "gcmRegId":"", "osKnd":"", "osVer":"", "dpi":"", "rsotnHrzn":"", "rsotnVrtc":"", "modelNo":"", "ipInfo":"" }
    # cookies = {'JSESSIONID': session_id }
    url = 'https://student.cnsa.hs.kr/login/userLogin'
    res = sess.post(url, data=params, headers=header)
    # print(res.text, res.status_code)
    # print(res.text)
    return res.status_code, str(res.cookies.get_dict().get('JSESSIONID'))

# def attempt_login(sess, id, password, session_id):
#     params = {'loginId' : id, 'loginPw': password}
#     # cookies = {'JSESSIONID': session_id }
#     url = 'http://student.cnsa.hs.kr/login/userLogin'
#     # cookie = {'JSESSIONID': session_id}
#     res = sess.post(url, data=params)
#     # print(res.text, res.status_code)
#     print(res.text)
#     return res.status_code, str(res.cookies.get_dict().get('JSESSIONID'))

def connect_to_main_web(sess, session_id):
    # cookies = {'JSESSIONID' : session_id }
    url = 'http://student.cnsa.hs.kr/home'
    res = sess.post(url)
    #print(res.text[:400])


def connect_to_food_table(sess, session_id):
    cookies = {}
    if not sess.cookies.get_dict().get('JSESSIONID'):
        cookies = {'JSESSIONID': session_id }
    url = 'http://student.cnsa.hs.kr/livelihood/meal/listMeal'
    res = sess.post(url, cookies=cookies)
    # print(res.text)
    return res.text

def replace_useless(x):
    x = x.replace('\t', '').replace('\r', '').replace('\n\n\n\n\n\n\n\n\n\n\n\n','\n').replace('\n\n\n\n\n\n\n\n\n\n','\n').replace('\n\n\n\n','')
    return x


def parse_food_list():
    user_id = 'codeztree'
    user_pass = 'green37984528'
    with requests.Session() as sess:
        session_id = get_user_session(user_id)
        print("Session ID from CHECK : " + session_id)

        if session_id == '':
            print("Login Attempt")

            session_id = set_session(sess) # 페이지 세션을 받는다
            # exit()
            print("PAGE SESSION : " + session_id)
            request_code, _session_id = attempt_login(sess, user_id, user_pass, session_id)
            print(request_code)
            if request_code != 200:
                print('로그인에 실패하였습니다. 관리자를 불러주세요.')
                exit()

            session_id = get_user_session(user_id)
            print("Login Successful! Session : " + str(session_id))

            # connect_to_main_web(sess, session_id)

        print('\n\n##################################\n\n')

        # 급식 파싱 시작 ---------------
        soup = BeautifulSoup(connect_to_food_table(sess, session_id), 'html.parser')

        # foodList = soup.find_all('td', {'class' : 'day bgToday'})
        # foodList = soup.select('td.bgToday') # 오늘 날짜만 선택

        foodList = soup.select('td.day')
        foodTextList = [data.text for data in foodList]  # 선택된 모든 데이터 파싱. 각 원소는 그날의 급식 정보 소유

        foodTextList = list(map(replace_useless, foodTextList))

        foodListFile = open('foodList.txt', 'w', encoding='utf-8')

        whenList = ['조식', '중식', '석식']
        dayList = ['월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일']
        # now = time.gmtime(time.time())

        now = dt.datetime.now()
        startDay = now + dt.timedelta(days=-now.weekday()) # 월요일 부터 계산 시작
        startFix = startDay

        # tm_year, tm_mon, tm_mday, tm_hour, tm_min,
        # tm_sec, tm_wday, tm_yday, tm_isdst

        # todayStr = time.strftime('%Y / %m / %d  ') + dayList[now.tm_wday]  # now.tm_wday -> 월요일 0 일요일 7

        return_list = []
        for i, food in enumerate(foodTextList):
            if i % 7 == 0: # 7 배수 마다는 다음 월요일 리셋
                startDay = startFix
            else:
                startDay += dt.timedelta(days=1)
            #  + dayList[i % 7]
            return_list.append({'meal_date': startDay.strftime('%Y-%m-%d'), 'meal_txt': food, 'meal_time_part': i // 7}) # i 를 3 나머지로 나누면 그날 요일 나옴 i - 0 1 2 -> 월요일 = 0

        print(return_list)


        return return_list
        # 급식 정보 입력 예시

        # 2018 / 3 / 3  일요일%%조식%%
        # 음식메뉴 1%%중식%%
        # 음식메뉴 2%%석식%%
        # 음식메뉴 3%%

        # 급식 파싱 완료 ---------------!

parse_food_list()

# if __name__ == '__main__':
#     user_id = 'codeztree'
#     user_pass = 'green37984528'
#     with requests.Session() as sess:
#         session_id = get_user_session(user_id)
#         if (session_id == ''):
#             session_id = get_web_session_id(sess)  # Session ID 없으면 페이지에서 받아오고 로그인 시도
#
#         if (attempt_login(sess, user_id, user_pass, session_id) != 200):
#             print('로그인에 실패하였습니다. 관리자를 불러주세요.')
#             exit()
#
#         print('\n\n##################################\n\n')
#
#
#         # 급식 파싱 시작 ---------------
#
#         soup = BeautifulSoup(connect_to_food_table(sess, session_id), 'html.parser')
#
#         # foodList = soup.find_all('td', {'class' : 'day bgToday'})
#         # foodList = soup.select('td.bgToday') # 오늘 날짜만 선택
#
#         foodList = soup.select('td.day')
#         foodTextList = [data.text for data in foodList] # 선택된 모든 데이터 파싱. 각 원소는 그날의 급식 정보 소유
#
#         foodTextList = list(map(replace_useless, foodTextList))
#
#         foodListFile = open('foodList.txt','w', encoding='utf-8')
#
#         whenList = ['조식', '중식', '석식']
#         dayList = ['월요일','화요일','수요일','목요일','금요일','토요일','일요일']
#         now = time.gmtime(time.time())
#
#
#         # tm_year, tm_mon, tm_mday, tm_hour, tm_min,
#         # tm_sec, tm_wday, tm_yday, tm_isdst
#
#         todayStr = time.strftime('%Y / %m / %d  ') + dayList[now.tm_wday] # now.tm_wday -> 월요일 0 일요일 7
#
#         foodListFile.write(todayStr + "%%")
#         # 그날 날짜를 입력한다.
#
#         for i, when in enumerate(whenList):
#             foodListFile.write(whenList[i] + "\n%%" + foodTextList[i] + "%%")
#
#         # 급식 정보 입력 예시
#
#         # 2018 / 3 / 3  일요일%%조식%%
#         # 음식메뉴 1%%중식%%
#         # 음식메뉴 2%%석식%%
#         # 음식메뉴 3%%
#
#         # 급식 파싱 완료 ---------------!
