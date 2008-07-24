# -*- coding: utf-8 -*-
import datetime
import time
import md5

from sqlalchemy import *
from sqlalchemy.orm import *

class User(object):
    def __init__(self, username, password, nickname, email, signature,
                 self_introduction, default_language):
        self.username = username
        self.set_password(password)
        self.nickname = nickname
        self.email = email
        self.signature = signature
        self.self_introduction = self_introduction
        self.default_language = default_language
        self.activated = 'False'
        self.widget = 0
        self.layout = ''
        self.join_time = datetime.datetime.fromtimestamp(time.time())
        self.last_login_time = None 
        self.last_logout_time = None
        self.last_login_ip = ''
        self.is_sysop = False

    def set_password(self, password):
        self.password = md5.md5(password).hexdigest()

    password = property(fset=set_password)

    def compare_password(self, password):
        if md5.md5(password).hexdigest() == self.password:
            return True
        else:
            return False

    def __repr__(self):
        return "<User('%s', '%s')>" % (self.username, self.nickname)

class UserActivation(object):
    def __init__(self, user, activation_code):
        self.user = user
        self.activation_code = activation_code
        self.issued_date = datetime.datetime.fromtimestamp(time.time())

    def __repr__(self):
        return "<UserActivation('%s', '%s')>" % (self.user.username, self.activation_code)

class Board(object):
    def __init__(self, board_name, board_description):
        self.board_name = board_name
        self.board_description = board_description

    def __repr__(self):
        return "<Board('%s', '%s')>" % (self.board_name, self.board_description)

class Article(object):
    def __init__(self, board, title, content, author, author_ip, parent):
        self.board = board
        self.title = title
        self.content = content
        self.author = author
        self.author_ip = author_ip
        self.deleted = False
        self.date = datetime.datetime.fromtimestamp(time.time())
        self.hit = 0
        self.vote = 0
        self.reply_count = 0
        if parent:
            if parent.root:
                self.root = parent.root
            else:
                self.root = parent
        else:
            self.root = None
        self.parent = parent
        self.last_modified_date = self.date

    def __repr__(self):
        return "<Article('%s', '%s', %s)>" % (self.title, self.author.username, str(self.date))

class ReadStatus(object):
    def __init__(self, user, read_status_data):
        self.user = user
        self.read_status_data = read_status_data

    def __repr__(self):
        return "<ReadStatus('%s', '%s')>" % (self.user.username, self.read_status_data)

class Blacklist(object):
    def __init__(self, user, target_user, block_article, block_message):
        self.user = user 
        self.target_user = target_user
        self.block_article = block_article
        self.block_message = block_message
        self.blacklisted_date = datetime.datetime.fromtimestamp(time.time())
        self.last_modified_date = self.blacklisted_date

    def __repr__(self):
        return "<Blacklist('%s','%s')>" % (self.user.username, self.target_user.username) 

class Message(object):
    def __init__(self, from_user, from_user_ip, to_user, message):
        self.from_user = from_user
        self.from_user_ip = from_user_ip
        self.to_user = to_user
        self.sent_time = datetime.datetime.fromtimestamp(time.time())
        self.message = message
        self.read_status = 'N'

    def __repr__(self):
        return "<Message('%s','%s','%s')>" % (self.from_user, self.to_user, self.message)

class Notice(object):
    def __init__(self, content):
        self.content = content
        self.valid = True

    def __repr__(self):
        return "<Notice('%s','%s')>" % (self.content, self.valid)

metadata = MetaData()
users_table = Table('users', metadata,
    Column('id', Integer, primary_key=True),
    Column('username', Unicode(40), unique=True),
    Column('password', Unicode(50)),
    Column('nickname', Unicode(20), unique=True),
    Column('email', Unicode(40)),
    Column('signature', Unicode(50)),
    Column('self_introduction', Unicode(100)),
    Column('default_language', Unicode(5)),  # ko_KR, en_US
    Column('activated', Boolean),
    Column('widget', Integer),
    Column('layout', Unicode(50)),
    Column('join_time', DateTime),
    Column('last_login_time', DateTime),
    Column('last_logout_time', DateTime),
    Column('last_login_ip', Unicode(15)),
    Column('is_sysop', Boolean),
)

user_activation_table = Table('user_activation', metadata,
    Column('user_id', Unicode(40), ForeignKey('users.id'), primary_key=True),
    Column('activation_code', Unicode(50), unique=True),
    Column('issued_date', DateTime),
)

board_table = Table('boards', metadata,
    Column('id', Integer, primary_key=True),
    Column('board_name', Unicode(30), unique=True),
    Column('board_description', UnicodeText),
)

articles_table = Table('articles', metadata,
    Column('id', Integer, primary_key=True),
    Column('title', Unicode(30)),
    Column('board_id', Integer, ForeignKey('boards.id')),
    Column('content', UnicodeText),
    Column('author_id', Integer, ForeignKey('users.id')),
    Column('author_ip', Unicode(15)),
    Column('date', DateTime),
    Column('hit', Integer),
    Column('vote', Integer),
    Column('deleted', Boolean),
    Column('root_id', Integer, ForeignKey('articles.id'), nullable=True),
    Column('parent_id', Integer, ForeignKey('articles.id'), nullable=True),
    Column('reply_count', Integer, nullable=False),
    Column('last_modified_date', DateTime),
)

read_status_table = Table('read_status', metadata,
    Column('id', Integer, primary_key=True),
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('read_status_data', PickleType),
)

blacklist_table = Table('blacklists' , metadata,
    Column('id', Integer, primary_key=True),
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('blacklisted_user_id', Integer, ForeignKey('users.id')),
    Column('blacklisted_date', DateTime),
    Column('last_modified_date', DateTime),
    Column('block_article', Boolean),
    Column('block_message', Boolean),
)

message_table = Table('messages', metadata,
    Column('id', Integer, primary_key=True),
    Column('from_id', Integer, ForeignKey('users.id'), nullable=False),
    Column('from_ip', Unicode(15)),
    Column('to_id', Integer, ForeignKey('users.id'), nullable=False),
    Column('sent_time', DateTime),
    Column('message', Unicode(200)),
    Column('read_status', Unicode(1)),
)

notice_table = Table('notices' , metadata,
    Column('id', Integer, primary_key=True),
    Column('content', UnicodeText),
    Column('issued_date', DateTime),
    Column('due_date', DateTime),
    Column('valid', Boolean),
)

mapper(User, users_table)

mapper(UserActivation, user_activation_table, properties={
    'user':relation(User, backref='activation', uselist=False)
})

mapper(Article, articles_table, properties={
    'author':relation(User, backref='articles', lazy=False),
    'board':relation(Board, backref='articles', lazy=True),

    'children':relation(Article,
        primaryjoin=articles_table.c.parent_id==articles_table.c.id,
        backref=backref('parent', lazy=True,
            remote_side=[articles_table.c.id],
            primaryjoin=articles_table.c.parent_id==articles_table.c.id,
            )
        ),
    'descendants':relation(Article, lazy=True,
        primaryjoin=articles_table.c.root_id==articles_table.c.id,
        backref=backref('root',
            remote_side=[articles_table.c.id],
            primaryjoin=articles_table.c.root_id==articles_table.c.id,
            )
        )
})

mapper(ReadStatus, read_status_table, properties={
    'user': relation(User, backref='read_status')
})

mapper(Board, board_table)

mapper(Message, message_table, properties={
    'from_user': relation(User, primaryjoin=message_table.c.from_id==users_table.c.id,
                    backref=backref('send_messages', lazy=True, join_depth=1,
                                    primaryjoin=message_table.c.from_id==users_table.c.id,
                                    viewonly=False)
        ),
    'to_user': relation(User, primaryjoin=message_table.c.to_id==users_table.c.id,
                    backref=backref('received_messages', lazy=True, join_depth=1,
                                    primaryjoin=message_table.c.to_id==users_table.c.id,
                                    viewonly=False)
        ),
})

mapper(Blacklist, blacklist_table, properties={
    'user':relation(User, primaryjoin=blacklist_table.c.user_id==users_table.c.id,
                    backref=backref('blacklist', lazy=True, join_depth=1,
                                    primaryjoin=blacklist_table.c.user_id==users_table.c.id,
                                    viewonly=True)),
    'target_user':relation(User, primaryjoin=blacklist_table.c.blacklisted_user_id==users_table.c.id,
                    backref=backref('blacklisted', lazy=True, join_depth=1,
                                    primaryjoin=blacklist_table.c.blacklisted_user_id==users_table.c.id,
                                    viewonly=True)),
})

TEST_DATABASE_FILENAME = 'test.db'
CONNECTION_STRING = 'sqlite:///%s' % TEST_DATABASE_FILENAME
#CONNECTION_STRING = 'mysql://s20060735:s20060735@localhost/s20060735?charset=utf8&use_unicode=1'

engine = None

def get_engine():
    '''Factory method to create database connection.'''
    global engine
    if not engine:
        from sqlalchemy import create_engine
        engine = create_engine(CONNECTION_STRING, convert_unicode=True, encoding='utf-8', echo=False)
    return engine

Session = None

def init_database():
    global Session
    get_engine()
    metadata.create_all(engine)
    Session = sessionmaker(bind=engine, autoflush=True, transactional=True)

def init_test_database():
    """Test database must reset the database."""
    global engine, Session, namespace
    # 데이터베이스를 억지로 새로 만든다.
    from sqlalchemy import create_engine
    engine = create_engine('sqlite://', convert_unicode=True, encoding='utf-8', echo=False)
    Session = sessionmaker(bind=engine, autoflush=True, transactional=True)
    metadata.create_all(engine)

    # 네임스페이스 객체를 새로 만든다. (억지로)
    import arara
    arara.namespace = None
    arara.get_namespace()

def clear_test_database():
    """테스트 이후의 흔적을 지운다."""
    pass
