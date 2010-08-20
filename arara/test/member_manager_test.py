#-*- coding: utf-8 -*-
import unittest
import os
import sys
import logging


THRIFT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../gen-py/'))
sys.path.append(THRIFT_PATH)
ARARA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
sys.path.append(ARARA_PATH)

from arara_thrift.ttypes import *
import arara.model
import arara
from arara import arara_engine
import arara.model
import etc.arara_settings

class MemberManagerTest(unittest.TestCase):
    def setUp(self):
        # Common preparation for all tests
        self.org_BOT_ENABLED = etc.arara_settings.BOT_ENABLED
        etc.arara_settings.BOT_ENABLED = False
        arara.model.init_test_database()
        self.engine = arara_engine.ARAraEngine()

        # Regiister one user, combacsa
        user_reg_dic = {'username':u'combacsa', 'password':u'combacsa', 'nickname':u'combacsa', 'email':u'combacsa@example.com', 'signature':u'combacsa', 'self_introduction':u'combacsa', 'default_language':u'english', 'campus':u'Daejeon'}
        register_key = self.engine.member_manager.register_(UserRegistration(**user_reg_dic))
        self.engine.member_manager.confirm(u'combacsa', unicode(register_key))

        # Register one user, serialx(with campus=null)
        user_reg_dic = {'username':u'serialx', 'password':u'serialx', 'nickname':u'serialx', 'email':u'serialx@example.com', 'signature':u'serialx', 'self_introduction':u'serialx', 'default_language':u'english', 'campus':u''}
        register_key = self.engine.member_manager.register_(UserRegistration(**user_reg_dic))
        self.engine.member_manager.confirm(u'serialx', unicode(register_key))

        # Register one user, pipoket, but not confirm.
        user_reg_dic = {'username':u'pipoket', 'password':u'pipoket', 'nickname':u'pipoket', 'email':u'pipoket@example.com', 'signature':u'pipoket', 'self_introduction':u'pipoket', 'default_language':u'english', 'campus':u'Daejeon'}
        self.register_key_pipoket = self.engine.member_manager.register_(UserRegistration(**user_reg_dic))

    def testAddUserWithoutConfirm(self):
        user_reg_dic = {'username':u'hodduc', 'password':u'hodduc', 'nickname':u'hodduc', 'email':u'hodduc@example.com', 'signature':u'hodduc', 'self_introduction':u'hodduc', 'default_language':u'english', 'campus':u'Daejeon' }
        # _register_without_confirm 함수로 가입 후 로그인
        # 만약 원래 의도대로 Self Activation되지 않았다면 login이 되지 않을 것이므로 Exception이 발생함
        self.engine.member_manager._register_without_confirm(user_reg_dic, False)
        session_key = self.engine.login_manager.login(u'hodduc', u'hodduc', u'143.248.234.140')

        user_reg_dic = {'username':u'sillo', 'password':u'sillo', 'nickname':u'sillo', 'email':u'sillo@example.com', 'signature':u'sillo', 'self_introduction':u'sillo', 'default_language':u'english', 'campus':u'Daejeon'}
        # _register_without_confirm 함수로 시삽 권한으로 가입 후 로그인
        # 시삽 권한을 가지는지 확인
        self.engine.member_manager._register_without_confirm(user_reg_dic, True)
        session_key = self.engine.login_manager.login(u'sillo', u'sillo', u'143.248.234.140')
        if not self.engine.member_manager.is_sysop(session_key):
            self.fail('_register_without_confirm() failed! :: Failed to grant SYSOP previlege')



    def testAddMikkang(self):
        user_reg_dic = {'username':u'mikkang', 'password':u'mikkang', 'nickname':u'mikkang', 'email':u'mikkang@example.com', 'signature':u'mikkang', 'self_introduction':u'mikkang', 'default_language':u'english', 'campus':u'Daejeon' }
        # Check this user is not yet registered
        self.assertEqual(False, self.engine.member_manager.is_registered(user_reg_dic['username']))
        self.assertEqual(False, self.engine.member_manager.is_registered_nickname(user_reg_dic['nickname']))
        self.assertEqual(False, self.engine.member_manager.is_registered_email(user_reg_dic['email']))

        # Register the user, login, and check if any problem occurs
        register_key = self.engine.member_manager.register_(UserRegistration(**user_reg_dic))
        self.engine.member_manager.confirm(u'mikkang', register_key)
        session_key = self.engine.login_manager.login(u'mikkang', u'mikkang', u'143.248.234.140')
        self.engine.login_manager.logout(session_key)

    def testNotAddSerialx(self):
        # XXX(combacsa): Implement Later
        pass

    def testViewCombacsa(self):
        session_key = self.engine.login_manager.login(u'combacsa', u'combacsa', u'143.248.234.145')
        member = self.engine.member_manager.get_info(unicode(session_key))
        self.assertEqual(True, member.activated)
        self.assertEqual(u"combacsa@example.com", member.email)
        self.assertEqual(u"combacsa", member.nickname)
        self.assertEqual(0, member.widget)
        self.assertEqual(0, member.layout)
        self.assertEqual(u"Daejeon", member.campus)
        self.engine.login_manager.logout(session_key)

    def testPasswdChange(self):
        # Change password, and then login again to check it applied
        session_key = self.engine.login_manager.login(u'combacsa', u'combacsa', u'143.248.234.145')
        user_password_dic = {'username':u'combacsa', 'current_password':u'combacsa', 'new_password':u'computer'}
        self.engine.member_manager.modify_password(session_key, UserPasswordInfo(**user_password_dic))
        self.engine.login_manager.logout(session_key)
        try:
            session_key = self.engine.login_manager.login(u'combacsa', u'combacsa', u'143.248.234.145')
            fail()
        except InvalidOperation:
            pass
        session_key = self.engine.login_manager.login(u'combacsa', u'computer', u'143.248.234.145')
        # Change password again to let it be untouched
        user_password_dic = {'username':u'combacsa', 'current_password':u'computer', 'new_password':u'combacsa'}
        self.engine.member_manager.modify_password(session_key, UserPasswordInfo(**user_password_dic))
        self.engine.login_manager.logout(session_key)

    def testPasswdChangeSysop(self):
        # Preparation
        session_key_sysop = self.engine.login_manager.login(u'SYSOP', u'SYSOP', u'127.0.0.1')
        # Test 1. SYSOP change pasword for user 'combacsa' successfully.
        user_password_dic = {'username':u'combacsa', 'current_password':u'', 'new_password':u'computer'}
        self.engine.member_manager.modify_password_sysop(session_key_sysop, UserPasswordInfo(**user_password_dic))
        # Test 1-1. combacsa can't login with old password
        session_key = None
        try:
            session_key = self.engine.login_manager.login(u'combacsa', u'combacsa', u'143.248.234.145')
            self.fail('Though sysop changed password, user was able to login with old password.')
        except InvalidOperation:
            pass
        # Test 1-2. combacsa can login with new password
        session_key = self.engine.login_manager.login(u'combacsa', u'computer', u'143.248.234.145')
        # Test 2. Anyone except SYSOP can't call modify_password_sysop even if it is user oneself.
        user_password_dic = {'username':u'combacsa', 'current_password':u'', 'new_password':u'combacsa'}
        try:
            self.engine.member_manager.modify_password_sysop(session_key, UserPasswordInfo(**user_password_dic))
            self.fail("Someone who was not a sysop successfully changed one's password.")
        except InvalidOperation:
            pass

    def testModifyInfo(self):
        session_key = self.engine.login_manager.login(u'combacsa', u'combacsa', u'143.248.234.145')
        modify_user_reg_dic = { 'nickname':u'combacsa is sysop', 'signature':u'KAIST07 && HSHS07 && SPARCS07', 'self_introduction':u'i am Kyuhong', 'default_language':u'korean', 'campus':u'Seoul', 'widget':1, 'layout':u'aaa' }
        self.engine.member_manager.modify_user(session_key, UserModification(**modify_user_reg_dic))
        member = self.engine.member_manager.get_info(unicode(session_key))
        self.assertEqual(1, member.widget)
        self.assertEqual(u"aaa", member.layout)
        self.assertEqual(u"combacsa is sysop", member.nickname)
        self.assertEqual(u"KAIST07 && HSHS07 && SPARCS07", member.signature)
        self.assertEqual(u"i am Kyuhong", member.self_introduction)
        self.assertEqual(u"korean", member.default_language)
        self.assertEqual(u"Seoul", member.campus)

        # Restore change (at least nickname)
        modify_user_reg_dic = { 'nickname':u'combacsa', 'signature':u'KAIST07 && HSHS07 && SPARCS07', 'self_introduction':u'i am Kyuhong', 'default_language':u'korean', 'campus':u'Seoul', 'widget':1, 'layout':u'aaa' }
        self.engine.member_manager.modify_user(session_key, UserModification(**modify_user_reg_dic))
        self.engine.login_manager.logout(session_key)

    def testSearch(self):
        # Single User Result
        session_key = self.engine.login_manager.login(u'combacsa', u'combacsa', u'143.248.234.145')
        users = self.engine.member_manager.search_user(session_key, u'serialx')
        self.assertEqual(1, len(users))
        self.assertEqual(u"serialx", users[0].username)
        self.assertEqual(u"serialx", users[0].nickname)
        # Multi User Result (Add new user with duplicated nickname)
        user_reg_dic = {'username':u'ggingkkang', 'password':u'xx', 'nickname':u'serialx', 'email':u'ggingkkang@example.com', 'signature':u'', 'self_introduction':u'', 'default_language':u'english', 'campus':u'Seoul' }
        register_key = self.engine.member_manager.register_(UserRegistration(**user_reg_dic))
        self.engine.member_manager.confirm(u'ggingkkang', unicode(register_key))

        users = self.engine.member_manager.search_user(session_key, u'serialx')
        self.assertEqual(2, len(users))
        if (users[0].username == 'serialx'): # not sure about order
            self.assertEqual(u"serialx", users[0].username)
            self.assertEqual(u"serialx", users[0].nickname)
            self.assertEqual(u"ggingkkang", users[1].username)
            self.assertEqual(u"serialx", users[1].nickname)
        else:
            self.assertEqual(u"serialx", users[1].username)
            self.assertEqual(u"serialx", users[1].nickname)
            self.assertEqual(u"ggingkkang", users[0].username)
            self.assertEqual(u"serialx", users[0].nickname)

        users = self.engine.member_manager.search_user(session_key, u'ggingkkang', u'username')
        self.assertEqual(1, len(users))
        self.assertEqual(u"ggingkkang", users[0].username)
        self.assertEqual(u"serialx", users[0].nickname)

        users = self.engine.member_manager.search_user(session_key, u'combacsa', u'nickname')
        self.assertEqual(1, len(users))
        self.assertEqual(u"combacsa", users[0].username)
        self.assertEqual(u"combacsa", users[0].nickname)

        try:
            self.engine.member_manager.search_user(session_key, u'mikkang', u'wrong_key')
            fail()
        except InvalidOperation:
            pass
        self.engine.login_manager.logout(session_key)

        # 찾는 사람이 없는 경우에는?

    def testRemove(self):
        # XXX(serialx): User remove temp. removed.
        session_key = self.engine.login_manager.login(u'combacsa', u'combacsa', u'143.248.234.145')
        try:
            self.engine.member_manager.remove_user(session_key)
            fail()
        except InvalidOperation:
            pass

    def testSysop(self):
        session_key = self.engine.login_manager.login(u'combacsa', u'combacsa', u'143.248.234.145')
        self.assertEqual(False, self.engine.member_manager.is_sysop(session_key))
        self.engine.login_manager.logout(session_key)
        session_key = self.engine.login_manager.login(u'SYSOP', u'SYSOP', u'143.248.234.145')
        self.assertEqual(True, self.engine.member_manager.is_sysop(session_key))
        self.engine.login_manager.logout(session_key)
        # Prevent adding SYSOP
        user_reg_dic = { 'username':u'SYSOP', 'password':u'SYSOP', 'nickname':u'SYSOP', 'email':u'SYSOP@sparcs.org', 'signature':u'', 'self_introduction':u'i am mikkang', 'default_language':u'english', 'campus':u'' }
        try:
            sysop_register_key = self.engine.member_manager.register_(UserRegistration(**user_reg_dic))
            fail()
        except InvalidOperation:
            pass

    def testBackdoorConfirm(self):
        user_reg_dic = {'username':u'mikkang20', 'password':u'mikkang', 'nickname':u'mikkang20', 'email':u'mikkang20@example.com', 'signature':u'mikkang', 'self_introduction':u'mikkang', 'default_language':u'english', 'campus':u'' }
        registration_key = self.engine.member_manager.register_(UserRegistration(**user_reg_dic))
        session_key = self.engine.login_manager.login(u'SYSOP', u'SYSOP', u'143.248.234.145')
        self.engine.member_manager.backdoor_confirm(session_key, u'mikkang20')
        self.engine.login_manager.logout(session_key)
        session_key = self.engine.login_manager.login(u'mikkang20', u'mikkang', u'143.248.234.140')
        self.engine.login_manager.logout(session_key)
        # XXX 시삽이 아닌 사람이 백도어 컨펌을 못 하는 것을 테스트.

    def testAuthenticate(self):
        # 인증 성공
        msg1 = self.engine.member_manager.authenticate(u'combacsa', u'combacsa', u'143.248.234.140')
        msg2 = self.engine.member_manager.authenticate(u'serialx',  u'serialx', u'143.248.234.140')
        # 인증 실패 - wrong passwd
        try:
            msg3 = self.engine.member_manager.authenticate(u'combacsa', u'mikkang', u'143.248.234.140')
        except InvalidOperation:
            pass
        # 인증 실패 - wrong username
        try:
            msg4 = self.engine.member_manager.authenticate(u'elaborate', u'elaborate', u'143.248.234.140')
        except InvalidOperation:
            pass
        # 인증 실패 - not activated
        try:
            msg5 = self.engine.member_manager.authenticate(u'pipoket', u'pipoket', u'143.248.234.140')
        except InvalidOperation:
            # XXX 실패 사유가 무엇인지 확인할 수 있어야 한다 ...
            pass
        try:
            msg6 = self.engine.member_manager.authenticate(u" ", u" ", u"143.248.234.140")
            self.fail()
        except InvalidOperation:
            pass

    def testUserToSysop(self):
        session_key = self.engine.login_manager.login(u'combacsa', u'combacsa', u'143.248.234.145')
        #Prevent user from using user_to_sysop
        try:
            self.engine.member_manager.user_to_sysop(session_key, u'combacsa')
            self.fail()
        except InvalidOperation:
            pass

        session_key = self.engine.login_manager.login(u'SYSOP', u'SYSOP', u'127.0.0.1')
        self.engine.member_manager.user_to_sysop(session_key, u'combacsa')
        self.engine.login_manager.logout(session_key)
        
        session_key = self.engine.login_manager.login(u'combacsa', u'combacsa', u'143.248.234.145')
        #check if user is not SYSOP
        self.assertEqual(True, self.engine.member_manager.is_sysop(session_key))

    def testAuthenticationMode(self):
        session_key = self.engine.login_manager.login(u'combacsa',u'combacsa', u'143.248.234.154')
        check_mode= self.engine.member_manager.authentication_mode(session_key)
        # 아직 인증단계를 유저별로 나누는 것이 구현이 안되어있기 때문에 기본값 0이 리턴됩니다.
        self.assertEqual(0, check_mode)


    def tearDown(self):
        self.engine.shutdown()
        arara.model.clear_test_database()
        etc.arara_settings.BOT_ENABLED = self.org_BOT_ENABLED
def suite():
    return unittest.TestLoader().loadTestsFromTestCase(MemberManagerTest)

if __name__ == "__main__":
    unittest.TextTestRunner(verbosity=2).run(suite())
