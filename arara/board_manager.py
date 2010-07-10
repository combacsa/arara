# -*- coding: utf-8 -*-
from sqlalchemy.exceptions import InvalidRequestError, IntegrityError
from arara import model
from arara.util import filter_dict, require_login
from arara.util import log_method_call_with_source, log_method_call_with_source_important
from arara.util import smart_unicode

from arara_thrift.ttypes import *

log_method_call = log_method_call_with_source('board_manager')
log_method_call_important = log_method_call_with_source_important('board_manager')

BOARD_MANAGER_WHITELIST = ('board_name', 'board_description', 'read_only', 'hide', 'id', 'headings')

class BoardManager(object):
    '''
    보드 추가 삭제 및 관리 관련 클래스
    '''

    def __init__(self, engine):
        self.engine = engine
        # Internal Cache!
        self.all_board_list = None
        self.all_board_dict = None
        self.all_board_and_heading_list = None
        self.all_board_and_heading_dict = None
        self.cache_board_list()

    def _get_dict(self, item, whitelist=None):
        item_dict = item.__dict__
        if whitelist:
            filtered_dict = filter_dict(item_dict, whitelist)
        else:
            filtered_dict = item_dict
        return filtered_dict

    def _get_dict_list(self, raw_list, whitelist=None):
        return_list = []
        for item in raw_list:
            filtered_dict = self._get_dict(item, whitelist)
            return_list.append(filtered_dict)
        return return_list

    def _is_sysop(self, session_key):
        if not self.engine.member_manager.is_sysop(session_key):
            raise InvalidOperation('no permission')

    @require_login
    @log_method_call_important
    def add_board(self, session_key, board_name, board_description, heading_list = []):
        '''
        보드를 신설한다.

        @type  session_key: string
        @param session_key: User Key (must be SYSOP)
        @type  board_name: string
        @param board_name: 개설할 Board Name
        @type  board_description: string
        @param board_description: 보드에 대한 한줄 설명
        @type  heading_list: list of string
        @param heading_list: 보드에 존재할 말머리 목록 (초기값 : [] 아무 말머리 없음)
        @rtype: boolean, string 
        @return:
            1. 성공: None
            2. 실패:
                1. 로그인되지 않은 유저: 'NOT_LOGGEDIN'
                2. 시샵이 아닌 경우: 'no permission'
                3. 존재하는 게시판: 'board already exist'
                4. 데이터베이스 오류: 'DATABASE_ERROR'

        '''
        self._is_sysop(session_key)
        session = model.Session()
        board_to_add = model.Board(smart_unicode(board_name), board_description)
        try:
            session.add(board_to_add)
            # Board Heading 들도 추가한다.
            # TODO: heading 에 대한 중복 검사가 필요하다. (지금은 따로 없다)
            for heading in heading_list:
                board_heading = model.BoardHeading(board_to_add, smart_unicode(heading))
                session.add(board_heading)

            session.commit()
            session.close()
            # 보드에 변경이 발생하므로 캐시 초기화
            self.cache_board_list()
        except IntegrityError:
            session.rollback()
            session.close()
            raise InvalidOperation('already added')

    def _get_board(self, board_name):
        try:
            return self.all_board_dict[board_name]
        except KeyError:
            raise InvalidOperation('board does not exist')
        return board

    def _get_board_from_session(self, session, board_name):
        try:
            board = session.query(model.Board).filter_by(board_name=smart_unicode(board_name)).one()
        except InvalidRequestError:
            session.close()
            raise InvalidOperation('board does not exist')
        return board

    @log_method_call
    def get_board(self, board_name):
        return self._get_board(board_name)

    @log_method_call
    def get_board_id(self, board_name):
        return self._get_board(board_name).id

    @log_method_call
    def get_board_heading_list_fromid(self, board_id):
        '''
        주어진 board의 heading 의 목록을 가져온다. 단 board_id 를 이용한다.

        @type  board_id: int
        @param board_id: heading 을 가져올 보드의 id
        @rtype : list of string
        @return: heading 의 목록
        '''
        session = model.Session()
        board_heading_list = []
        heading_query = session.query(model.BoardHeading).filter_by(board_id=board_id)
        heading_result = heading_query.all()

        for board_heading in heading_result:
            board_heading_list.append(board_heading.heading)
        session.close()

        return board_heading_list

    @log_method_call
    def get_board_heading_list(self, board_name):
        '''
        주어진 board의 heading 의 목록을 가져온다.
        주의 : internal cache 에 영향을 받으므로 internal cache 를 생성하는 중에는 사용하면 안 된다.

        @type  board_name: string
        @param board_name: heading 을 가져올 보드의 이름
        @rtype : list of string
        @return: heading 의 목록
        '''
        board_id = self.get_board_id(board_name)
        return self.get_board_heading_list_fromid(board_id)

    def cache_board_list(self):
        # Board 의 목록을 DB 로부터 memory 로 옮겨 둔다.
        session = model.Session()
        boards = session.query(model.Board).filter_by(deleted=False).all()
        board_dict_list = self._get_dict_list(boards, BOARD_MANAGER_WHITELIST)
        session.close()
        # Board Heading 도 전부 가져온다.
        for each_board in board_dict_list:
            each_board['headings'] = self.get_board_heading_list_fromid(each_board['id'])
        # all_board_list 와 all_board_dict 로 만든다. 
        self.all_board_list = [Board(**d) for d in board_dict_list]
        self.all_board_dict = {}
        for board in self.all_board_list:
            self.all_board_dict[board.board_name] = board

    @log_method_call
    def get_board_list(self):
        if self.all_board_list == None:
            self.cache_board_list()
        return self.all_board_list

    @require_login
    @log_method_call_important
    def add_read_only_board(self, session_key, board_name):
        '''
        보드를 읽기 전용으로 변경해주는 함수

        @type  session_key: string
        @param session_key: User Key
        @type  board_name: string
        @param board_name: Board Name
        @rtype: boolean, string 
        @return:
            1. 읽기전용 성공: True, 'OK' 
            2. 실패:
                1. 로그인되지 않은 유저: False, 'NOT_LOGGEDIN'
                2. 시샵이 아닌 경우: False, 'no permission'
                3. 존재하지 않는 게시판: False, 'board does not exist'
                4. 이미 읽기전용인 보드의 경우: False, 'ALEARDY_READ_ONLY_BOARD'
                5. 데이터베이스 오류: False, 'DATABASE_ERROR'
        '''

        self._is_sysop(session_key)
        session = model.Session()
        board = self._get_board_from_session(session, board_name)
        if board.read_only:
            session.close()
            raise InvalidOperation('aleardy read only board')
        board.read_only = True
        session.commit()
        session.close()
        # 보드에 변경이 발생하므로 캐시 초기화
        self.cache_board_list()

    @require_login
    @log_method_call_important
    def return_read_only_board(self, session_key, board_name):
        '''
        보드를 읽기 전용에서 다시 쓰기/읽기 가능 보드로 변경해주는 함수

        @type  session_key: string
        @param session_key: User Key
        @type  board_name: string
        @param board_name: Board Name
        @rtype: boolean, string 
        @return:
            1. 성공: True, 'OK' 
            2. 실패:
                1. 로그인되지 않은 유저: False, 'NOT_LOGGEDIN'
                2. 시샵이 아닌 경우: False, 'no permission'
                3. 존재하지 않는 게시판: False, 'board does not exist'
                4. 이미 읽기전용가 아닌경우 보드의 경우: False, 'not read only board'
                5. 데이터베이스 오류: False, 'DATABASE_ERROR'
        '''

        self._is_sysop(session_key)
        session = model.Session()
        board = self._get_board_from_session(session, board_name)
        if not board.read_only:
            session.close()
            raise InvalidOperation('not read only board')
        board.read_only = False
        session.commit()
        session.close()
        # 보드에 변경이 발생하므로 캐시 초기화
        self.cache_board_list()

    @require_login
    @log_method_call_important
    def edit_board(self, session_key, board_name, new_name, new_description):
        '''
        보드의 이름과 설명을 변경한다. 이름이나 설명을 바꾸고 싶지 않으면 파라메터로 길이가 0 인 문자열을 주면 된다.

        @type  session_key: string
        @param session_key: User Key
        @type  board_name: string
        @param board_name: 설명을 수정하고자 하는 Board Name
        @type  new_name: string
        @param new_name: 보드에게 할당할 새 이름 (미변경시 '')
        @type  new_description: string
        @param new_description: 보드에게 할당할 새 설명 (미변경시 '')
        @rtype: void
        @return:
            1. 성공: 아무것도 리턴하지 않음
            2. 실패:
                1. 로그인되지 않은 유저: 'NOT_LOGGEDIN'
                2. 시샵이 아닌 경우: 'no permission'
                3. 존재하지 않는 게시판: 'board does not exist'
                4. 기타 오류 : 주석 추가해 주세요
        '''
        self._is_sysop(session_key)

        board_name = smart_unicode(board_name)
        new_name = smart_unicode(new_name)
        new_description = smart_unicode(new_description)

        # 변경이 필요한 항목에 대해서만 변경을 진행한다.
        session = model.Session()
        board = self._get_board_from_session(session, board_name)
        if new_name != u'':
            board.board_name = new_name
        if new_description != u'':
            board.board_description = new_description
        try:
            session.commit()
            session.close()
        except IntegrityError:
            raise InvalidOperation("board already exist")
        # TODO :전체적인 Error 들 정리 ...
        except InvalidRequestError:
            raise InternalError()
        # 보드에 변경이 생겼으므로 캐시 초기화
        self.cache_board_list()

    @require_login
    @log_method_call_important
    def hide_board(self, session_key, board_name):
        '''
        보드를 숨겨주는 함수

        @type  session_key: string
        @param session_key: User Key
        @type  board_name: string
        @param board_name: Board Name
        @rtype: boolean, string
        @return:
            1. 성공: True, 'OK'
            2. 실패:
                1. 로그인되지 않은 유저: False, 'NOT_LOGGEDIN'
                2. 시샵이 아닌 경우: False, 'no permission'
                3. 존재하지 않는 게시판: False, 'board does not exist'
                4. 이미 숨겨져 있는 보드의 경우: False, 'already hidden'
                5. 데이터베이스 오류: False, 'DATABASE_ERROR'
        '''
        self._is_sysop(session_key)
        session = model.Session()
        board = self._get_board_from_session(session, board_name)
        if board.hide:
            session.close()
            raise InvalidOperation('already hidden')
        board.hide = True
        session.commit()
        session.close()
        # 보드에 변경이 발생하므로 캐시 초기화
        self.cache_board_list()

    @require_login
    @log_method_call_important
    def return_hide_board(self, session_key, board_name):
        '''
        숨겨진 보드를 다시 보여주는 함수

        @type  session_key: string
        @param session_key: User Key
        @type  board_name: string
        @param board_name: Board Name
        @rtype: boolean, string
        @return:
            1. 성공: True, 'OK'
            2. 실패:
                1. 로그인되지 않은 유저: False, 'NOT_LOGGEDIN'
                2. 시샵이 아닌 경우: False, 'no permission'
                3. 존재하지 않는 게시판: False, 'board does not exist'
                4. 숨겨져 있는 보드가 아닌 경우: False, 'not hidden board'
                5. 데이터베이스 오류: False, 'DATABASE_ERROR'
        '''
        self._is_sysop(session_key)
        session = model.Session()
        board = self._get_board_from_session(session, board_name)
        if not board.hide:
            session.close()
            raise InvalidOperation('not hidden board')
        board.hide = False
        session.commit()
        session.close()
        # 보드에 변경이 발생하므로 캐시 초기화
        self.cache_board_list()

    @require_login
    @log_method_call_important
    def delete_board(self, session_key, board_name):
        self._is_sysop(session_key)
        session = model.Session()
        board = self._get_board_from_session(session, board_name)
        board.deleted = True
        session.commit()
        session.close()
        # 보드에 변경이 발생하므로 캐시 초기화
        self.cache_board_list()
