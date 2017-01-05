import sublime
import sublime_plugin
import os
import threading
# import datetime
# import sys, xdrlib
# import json
# import random

# from . import xlwt
# from . import requests
from . import util
from . import setting
from . import xlsxwriter
from .requests.exceptions import RequestException
from .salesforce import (
    SalesforceMoreThanOneRecord,
    SalesforceMalformedRequest,
    SalesforceExpiredSession,
    SalesforceRefusedRequest,
    SalesforceResourceNotFound,
    SalesforceGeneralError,
    SalesforceError
    )



# class HelloCommand(sublime_plugin.TextCommand):
#     def run(self, edit):
#       self.sf = util.sf_login()
#       self.sftype = self.sf.get_sobject("user")

#       metadata = self.sftype.metadata()
#       print(metadata)

#       return
        # print('result=========>')
        # # Test it out
        # data = '''
        # 3 + 4 * 10 #$#
        #   + -20 *2
        # '''

        # # Give the lexer some input
        # lexer.input(data)

        # # Tokenize
        # while True:
        #     tok = lexer.token()
        #     if not tok: 
        #         break      # No more input
        #     print(tok)


# ------------------------------------------------------------
# calclex.py
#
# tokenizer for a simple expression evaluator for
# numbers and +,-,*,/
# ------------------------------------------------------------
from .ply import lex as lex

# List of token names.   This is always required
tokens = (
   'NUMBER',
   'PLUS',
   'MINUS',
   'TIMES',
   'DIVIDE',
   'LPAREN',
   'RPAREN',
)

# Regular expression rules for simple tokens
t_PLUS    = r'\+'
t_MINUS   = r'-'
t_TIMES   = r'\*'
t_DIVIDE  = r'/'
t_LPAREN  = r'\('
t_RPAREN  = r'\)'

# A regular expression rule with some action code
def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)    
    return t

# Define a rule so we can track line numbers
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)
    print('--->new')

# A string containing ignored characters (spaces and tabs)
t_ignore  = ' \t'

# Error handling rule
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

# Build the lexer
lexer = lex.lex()