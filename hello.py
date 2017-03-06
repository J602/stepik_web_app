# encoding: utf-8
from multiprocessing import cpu_count

bind = "127.0.0.1:8080"
workers = cpu_count()

def app(environ, start_response):
    query_str = environ.get('QUERY_STRING', '')
    param_list = [i.encode() + '\n'.encode() for i in query_str.split('&')]
    start_response('200 OK', [('Content-Type', 'text/plain')])
    return param_list
