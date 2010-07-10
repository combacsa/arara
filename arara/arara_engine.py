#-*- coding: utf-8 -*-
from arara.article_manager import ArticleManager
from arara.blacklist_manager import BlacklistManager
from arara.board_manager import BoardManager
from arara.member_manager import MemberManager
from arara.login_manager import LoginManager
from arara.messaging_manager import MessagingManager
from arara.notice_manager import NoticeManager
from arara.read_status_manager import ReadStatusManager
from arara.search_manager import SearchManager
from arara.file_manager import FileManager

class ARAraEngine(object):
    '''
    하나의 서버에서 돌아가는 아라라 엔진 인스턴스.
    각 매니저 인스턴스들을 보유하고 있다.
    '''
    # TODO: 아래의 모든 "mapping" 을 독립적인 함수로 옮기자.
    # TODO: 이 클래스를 위한 TEST 는 설계할 수 있는가?

    def __init__(self):
        self.login_manager = LoginManager(self)
        self.member_manager = MemberManager(self)
        self.blacklist_manager = BlacklistManager(self)
        self.board_manager = BoardManager(self)
        self.read_status_manager = ReadStatusManager(self)
        self.article_manager = ArticleManager(self)
        self.messaging_manager = MessagingManager(self)
        self.notice_manager = NoticeManager(self)
        self.search_manager = SearchManager(self)
        self.file_manager = FileManager(self)

        # 일단 일일이 선언하기 귀찮아서 이렇게 구현했다.
        mapping = {
            'guest_login': self.login_manager.guest_login,
            'total_visitor': self.login_manager.total_visitor,
            'login': self.login_manager.login,
            'logout': self.login_manager.logout, 
            'update_session' : self.login_manager.update_session, 
            'get_session': self.login_manager.get_session,
            'get_user_id': self.login_manager.get_user_id,
            'get_user_ip': self.login_manager.get_user_ip,
            'get_current_online': self.login_manager.get_current_online,
            'is_logged_in': self.login_manager.is_logged_in,
            '_update_monitor_status': self.login_manager._update_monitor_status,
            'authenticate': self.member_manager.authenticate,
            'register_': self.member_manager.register_,
            'backdoor_confirm': self.member_manager.backdoor_confirm,
            'confirm': self.member_manager.confirm,
            'is_registered': self.member_manager.is_registered,
            'is_registered_nickname': self.member_manager.is_registered_nickname,
            'is_registered_email': self.member_manager.is_registered_email,
            'get_info': self.member_manager.get_info,
            'modify_password': self.member_manager.modify_password,
            'modify_password_sysop': self.member_manager.modify_password_sysop,
            'modify_user': self.member_manager.modify_user,
            'modify_authentication_email': self.member_manager.modify_authentication_email,
            'query_by_username': self.member_manager.query_by_username,
            'query_by_nick': self.member_manager.query_by_nick,
            'remove_user': self.member_manager.remove_user,
            'search_user': self.member_manager.search_user,
            'is_sysop': self.member_manager.is_sysop,
            '_logout_process': self.member_manager._logout_process,
            'add_blacklist': self.blacklist_manager.add_blacklist,
            'delete_blacklist': self.blacklist_manager.delete_blacklist,
            'modify_blacklist': self.blacklist_manager.modify_blacklist,
            'get_blacklist': self.blacklist_manager.get_blacklist,
            'get_article_blacklisted_userid_list': self.blacklist_manager.get_article_blacklisted_userid_list,
            'add_board': self.board_manager.add_board,
            'get_board': self.board_manager.get_board,
            'get_board_id': self.board_manager.get_board_id,
            'get_board_heading_list': self.board_manager.get_board_heading_list,
            'get_board_list': self.board_manager.get_board_list,
            'add_read_only_board': self.board_manager.add_read_only_board,
            'return_read_only_board': self.board_manager.return_read_only_board,
            'hide_board': self.board_manager.hide_board,
            'return_hide_board': self.board_manager.return_hide_board,
            'delete_board': self.board_manager.delete_board,
            'edit_board': self.board_manager.edit_board,
            'check_stat': self.read_status_manager.check_stat,
            'check_stats': self.read_status_manager.check_stats,
            'mark_as_read_list': self.read_status_manager.mark_as_read_list,
            'mark_as_read': self.read_status_manager.mark_as_read,
            'mark_as_viewed': self.read_status_manager.mark_as_viewed,
            'save_to_database': self.read_status_manager.save_to_database,
            'get_today_best_list': self.article_manager.get_today_best_list,
            'get_today_best_list_specific': self.article_manager.get_today_best_list_specific,
            'get_weekly_best_list': self.article_manager.get_weekly_best_list,
            'get_weekly_best_list_specific': self.article_manager.get_weekly_best_list_specific,
            'not_read_article_list': self.article_manager.not_read_article_list,
            'new_article_list': self.article_manager.new_article_list,
            'article_list': self.article_manager.article_list,
            'read_article': self.article_manager.read_article,
            'read_recent_article': self.article_manager.read_recent_article,
            'article_list_below': self.article_manager.article_list_below,
            'vote_article': self.article_manager.vote_article,
            'write_article': self.article_manager.write_article,
            'write_reply': self.article_manager.write_reply,
            'modify_article': self.article_manager.modify_article,
            'delete_article': self.article_manager.delete_article,
            'destroy_article': self.article_manager.destroy_article,
            'fix_article_concurrency': self.article_manager.fix_article_concurrency,
            'save_file': self.file_manager.save_file,
            'download_file': self.file_manager.download_file,
            'delete_file': self.file_manager.delete_file,
            'sent_list': self.messaging_manager.sent_list,
            'receive_list': self.messaging_manager.receive_list,
            'send_message_by_username': self.messaging_manager.send_message_by_username,
            'send_message_by_nickname': self.messaging_manager.send_message_by_nickname,
            'send_message': self.messaging_manager.send_message,
            'read_received_message': self.messaging_manager.read_received_message,
            'read_sent_message': self.messaging_manager.read_sent_message,
            'delete_received_message': self.messaging_manager.delete_received_message,
            'delete_sent_message': self.messaging_manager.delete_sent_message,
            'register_article': self.search_manager.register_article,
            'ksearch': self.search_manager.ksearch,
            'search': self.search_manager.search,
            'get_banner': self.notice_manager.get_banner,
            'get_welcome': self.notice_manager.get_welcome,
            'list_banner': self.notice_manager.list_banner,
            'list_welcome': self.notice_manager.list_welcome,
            'add_banner': self.notice_manager.add_banner,
            'add_welcome': self.notice_manager.add_welcome,
            'remove_banner': self.notice_manager.remove_banner,
            'remove_welcome': self.notice_manager.remove_welcome,
            }
                
        for x in mapping:
            self.__dict__[x] = mapping[x]
