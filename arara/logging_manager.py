# -*- coding: utf-8 -*-

class LoggingManager(object):

    def __init__(self):
	pass

    def search(session_key, log_search_dic):
	"""
	�α� ���̺��� �˻��ϴ� �Լ�

	>>> logging.search(session_key, log_search_dic)

	  - Current log_search_dic { board_name, article_no, user_id, title, author, date }
	    NULL Values are allowed for each key.

	@type  session_key: string
	@param session_key: User Key
	@type  log_search_dic: dictionary
	@param log_search_dic: Log Search Query Dictionary
	@rtype: list
	@return:
	    1. �˻� ����: Log Dictionary List
	    2. �˻� ����: False
	"""
