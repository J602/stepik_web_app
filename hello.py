# encoding: utf-8


def app(environ, start_response):
    query_str = environ.get('QUERY_STRING', '')
    param_list = [i.encode() + '\n'.encode() for i in query_str.split('&')]
    start_response('200 OK', [('Content-Type', 'text/plain')])
    return param_list
