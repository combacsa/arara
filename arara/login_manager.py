# -*- coding: utf-8 -*-

import md5 as hashlib
import datetime

from arara import model

class LoginManager(object):
    '''
    로그인 처리 관련 클래스
    '''
    
    def __init__(self):
        self.session_dic = {}
        
    
    def guest_login(self, guest_ip):
        '''
        guest 로그인 처리를 담당하는 함수
        guest 의 ip를 받은 뒤 guest key를 리턴

        @type  guest_ip: string
        @param guest_ip: Guest IP
        @rtype: string
        @return: True, guest_key
        '''
        hash = hashlib.md5('guest'+''+datetime.datetime.today().__str__()).hexdigest()
        timestamp = datetime.datetime.isoformat(datetime.datetime.now())
        self.session_dic[hash] = {'username': 'guest', 'ip': guest_ip, 'logintime': timestamp}
        return True, hash
    

    def login(self, username, password, user_ip):
        '''
        로그인 처리를 담당하는 함수.
        아이디와 패스워드를 받은 뒤 User Key를 리턴.

        @type  username: string
        @param username: User Username
        @type  password: string
        @param password: User Password
        @type  user_ip: string
        @param user_ip: User IP
        @rtype: string
        @return: 
            1. 로그인 성공 시: True, user_key
            2. 로그인 실패 시
                1. 아이디 존재하지 않음: False, 'WRONG_USERNAME'
                2. 패스워드 불일치: False, 'WRONG_PASSWORD'
                3. 데이터베이스 관련 에러: False, 'DATABASE_ERROR'
        '''

        success, msg = self.member_manager._authenticate(username, password)
        if success:
            session = model.Session()
            blacklist_info = session.query(model.Blacklist).filter_by(
            hash = hashlib.md5(username+password+datetime.datetime.today().__str__()).hexdigest()
            timestamp = datetime.datetime.isoformat(datetime.datetime.now())
            self.session_dic[hash] = {'username': username, 'ip': user_ip, 'logintime': timestamp}
            return True, hash
        return success, msg

    def logout(self, session_key):
        '''
        로그아웃 처리를 담당하는 함수.

        @type  session_key: string
        @param session_key: User Key
        @rtype: string
        @return:
            1. 로그아웃 성공 시: True, 'OK'
            2. 로그아웃 실패 시
                1. 로그인되지 않은 사용자: False, 'NOT_LOGGEDIN'
                2. 데이터베이스 관련 에러: False, 'DATABASE_ERROR'
        '''

        try:
            self.session_dic.pop(session_key)
            return True, 'OK'
        except KeyError:
            return False, 'NOT_LOGGEDIN'

    def _set_member_manager(self, member_manager):
        self.member_manager = member_manager

    def update_session(self, session_key):
        '''
        세션 expire시간을 연장해주는 함수

        @type  session_key: string
        @param session_key: User Key
        @rtype: integer
        @return:
            1. 업데이트 성공 시: True, 'OK'
            2. 업데이트 실패 시
                1. 로그인되지 않은 사용자: False, 'NOT_LOGGEDIN'
                2. 데이터베이스 관련 에러: False, 'DATABASE_ERROR'
        '''

        return False, 'NOT_IMPLEMENTED'

    def get_session(self, session_key):
        '''
        세션 정보를 반환하는 함수

        @type  session_key: string
        @param session_key: User Key
        @rtype: dictionary
        @return:
            1. 로그인 되어있을 경우: True, self.session_dic {username, user_ip, login_time}
            2. 로그인 되어있지 않을 경우: False, 'NOT_LOGGEDIN'
        '''
        try:
            session_info = self.session_dic[session_key]
            return True, session_info
        except KeyError:
            return False, 'NOT_LOGGEDIN'

    def is_logged_in(self, session_key):
        '''
        로그인 여부를 체크하는 함수

        @type  session_key: string
        @param session_key: User Key
        @rtype: boolean
        @return:
            1. 로그인 되어있을 경우: True
            2. 로그인 되어있지 않을 경우: False
        '''

        if session_key in self.session_dic:
            return True
        else:
            return False

# vim: set et ts=8 sw=4 sts=4
