from arara.article_manager import ArticleManager
from arara.blacklist_manager import BlacklistManager
from arara.member_manager import MemberManager
from arara.login_manager import LoginManager
from arara.messaging_manager import MessagingManager
from arara.notice_manager import NoticeManager
from arara.read_status_manager import ReadStatusManager

class Namespace(object):
    def __init__(self):
        self.login_manager = LoginManager()
        self.member_manager = MemberManager()
        self.login_manager._set_member_manager(self.member_manager)
        self.member_manager._set_login_manager(self.login_manager)
        self.article_manager = ArticleManager(self.login_manager)
        self.blacklist_manager = BlacklistManager()
        self.blacklist_manager._set_member_manager(self.member_manager)
        self.blacklist_manager._set_login_manager(self.login_manager)
        self.messaging_manager = MessagingManager()
        self.messaging_manager._set_login_manager(self.login_manager)
        self.messaging_manager._set_member_manager(self.member_manager)
        self.notice_manager = NoticeManager()
        self.notice_manager._set_login_manager(self.login_manager)
        self.notice_manager._set_member_manager(self.member_manager)
        self.read_status_manager = ReadStatusManager()
        self.read_status_manager._set_login_manager(self.login_manager)
        self.read_status_manager._set_member_manager(self.member_manager)

namespace = None

def get_namespace():
    global namespace
    if not namespace:
        namespace = Namespace()
    return namespace

def get_server():
    import xmlrpclib
    server = xmlrpclib.Server('http://localhost:8000', use_datetime=True)
    return server

# vim: set et ts=8 sw=4 sts=4
