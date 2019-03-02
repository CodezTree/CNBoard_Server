#!/usr/lib/python3.5

import requests
from bs4 import BeautifulSoup
import time


def get_user_session(id):
    url = 'http://student.cnsa.hs.kr/login/dupLoginCheck?loginId=' + id
    res = requests.get(url)
    return str(res.text)


def get_web_session_id(session):
    res = session.get('http://student.cnsa.hs.kr/login/userLogin')
    print('WEB Session get : ' + res.cookies.get_dict().get('JSESSIONID'))
    return str(res.cookies.get_dict().get('JSESSIONID'))


def attempt_login(sess, id, password, session_id):
    params = {'loginId' : id, 'loginPw': password}
    cookies = {'JSESSIONID' : session_id }
    url = 'http://student.cnsa.hs.kr/login/userLogin'
    res = sess.post(url, data=params, cookies=cookies)
    # print(res.text, res.status_code)
    return res.status_code

def connect_to_main_web(sess, session_id):
    cookies = {'JSESSIONID' : session_id }
    url = 'http://student.cnsa.hs.kr/home'
    res = sess.post(url, cookies=cookies)
    # print(res.text)

def connect_to_food_table(sess, session_id):
    cookies = {'JSESSIONID' : session_id }
    url = 'http://student.cnsa.hs.kr/livelihood/meal/listMeal'
    res = sess.post(url, cookies=cookies)
    # print(res.text)
    return res.text

def replace_useless(x):
    x = x.replace('\t', '').replace('\r', '').replace('\n\n\n\n\n\n\n\n\n\n\n\n','\n').replace('\n\n\n\n\n\n\n\n\n\n','\n').replace('\n\n\n\n','')
    return x



if __name__ == '__main__':
    user_id = 'codeztree'
    user_pass = 'green37984528'
    with requests.Session() as sess:
        session_id = get_user_session(user_id)
        if (session_id == ''):
            session_id = get_web_session_id(sess)  # Session ID 없으면 페이지에서 받아오고 로그인 시도

        if (attempt_login(sess, user_id, user_pass, session_id) != 200):
            print('로그인에 실패하였습니다. 관리자를 불러주세요.')
            exit()

        print('\n\n##################################\n\n')


        # 급식 파싱 시작 ---------------

        soup = BeautifulSoup(connect_to_food_table(sess, session_id), 'html.parser')

        # foodList = soup.find_all('td', {'class' : 'day bgToday'})
        foodList = soup.select('td.bgToday')
        foodTextList = [data.text for data in foodList]

        foodTextList = list(map(replace_useless, foodTextList))

        foodListFile = open('foodList.txt','w', encoding='utf-8')

        whenList = ['조식', '중식', '석식']
        dayList = ['월요일','화요일','수요일','목요일','금요일','토요일','일요일']
        now = time.gmtime(time.time())


        # tm_year, tm_mon, tm_mday, tm_hour, tm_min,
        # tm_sec, tm_wday, tm_yday, tm_isdst

        todayStr = time.strftime('%Y / %m / %d  ') + dayList[now.tm_wday]

        foodListFile.write(todayStr + "%%")
        # 그날 날짜를 입력한다.

        for i, when in enumerate(whenList):
            foodListFile.write(whenList[i] + "\n%%" + foodTextList[i] + "%%")

        # 급식 정보 입력 예시

        # 2018 / 3 / 3  일요일%%조식%%
        # 음식메뉴 1%%중식%%
        # 음식메뉴 2%%석식%%
        # 음식메뉴 3%%

        # 급식 파싱 완료 ---------------!
