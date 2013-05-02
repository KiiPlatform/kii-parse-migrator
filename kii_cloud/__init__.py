# -*- coding: utf-8 -*-
# vim:set sts=4 sw=4 tw=0 et:

import httplib2
import json
import logging

APP_ID = None
APP_KEY = None
BASE_URL = None
TOKEN = None

default_logger = logging.getLogger('kii_cloud')

def init(app_id, app_key, region):
    global APP_ID, APP_KEY, BASE_URL
    APP_ID = app_id
    APP_KEY = app_key
    if region == u'jp':
        default_logger.debug('region is Japan')
        BASE_URL = u'https://api-jp.kii.com/api'
    else:
        BASE_URL = u'https://api.kii.com/api'

def json_request(uri, method, data, headers, logger=None):
    h = httplib2.Http()
    logger = logger if logger != None else default_logger
    logger.info('json_request - %s %s', method, uri)
    if headers != None:
        logger.info('> %s', headers)
    if data != None:
        logger.info('> %s', data)
        data = json.dumps(data).encode('UTF-8')
    (resp_headers, resp_body) = h.request(uri, method, data, headers)
    logger.info('< %s', resp_headers)
    logger.info('< %s', resp_body)
    try:
        resp_json = json.loads(resp_body) if resp_body != None else None
        return (resp_headers, resp_json)
    except ValueError:
        return (resp_headers, {})

def create_user(data):
    uri_array = [BASE_URL, u'apps', APP_ID, u'users']
    uri = u'/'.join(uri_array)
    headers = {
            u'content-type': u'application/vnd.kii.RegistrationRequest+json',
            u'x-kii-appid': APP_ID,
            u'x-kii-appkey': APP_KEY,
            }
    (resp, content) = json_request(uri, 'POST', data, headers)
    if resp.status == 201 or resp.status == 409:
        return True
    else:
        return False

def _has_token(username, password):
    if TOKEN:
        return True
    elif not create_user({ u'loginName': username, u'password': password }):
        return False
    uri = u'/'.join([BASE_URL, u'oauth2', u'token'])
    data = {
            u'username': username,
            u'password': password
            }
    headers = {
            'content-type': 'application/json',
            'x-kii-appid': APP_ID,
            'x-kii-appkey': APP_KEY,
            }
    (resp, resp_json) = json_request(uri, 'POST', data, headers)
    if resp.status != 200:
        return False
    if resp_json['access_token'] == None:
        return False
    else:
        global TOKEN
        TOKEN = str(resp_json['access_token'])
        return True

def create_object(bucket, data, obj_id=None):
    if not _has_token(u'kii_migrator', u'12345678'):
        return False
    uri_array = [BASE_URL, u'apps', APP_ID, u'buckets', bucket, u'objects']
    if obj_id:
        uri_array.append(obj_id)
    uri = u'/'.join(uri_array)
    headers = {
            'Authorization': u'Bearer ' + TOKEN,
            'content-type': 'content-type:application/vnd.%s.mydata+json' % APP_ID,
            'x-kii-appid': APP_ID,
            'x-kii-appkey': APP_KEY,
            }
    (resp, resp_json) = json_request(uri, 'PUT', data, headers)
    if resp.status == 201:
        return True
    else:
        return False
