# encoding:utf-8
import requests
import configparser
import datetime
from constant import BASE_CONF, TEMP_PATH
from dateutil import parser as dparser

# access_token 返回结果
"""

{   
    'refresh_token': '25.93158bf37b8c0b52285b9888035f2958.315360000.1953422145.282335-25244773', 
    'expires_in': 2592000, 
    'session_key': '9mzdA5mKRjs947VmT0czWIRVR/psRc5PmTdk+EKyvSzXKyOjtlauAEfmpEhJA/xMXVzyAwUoSr2LdQF6lALerKbfErsIlg==', 
    'access_token': '24.8316940270ef25b030c05a19214b7164.2592000.1640654145.282335-25244773', 
    'scope': 'public brain_all_scope unit_理解与交互V2 wise_adapt lebo_resource_base lightservice_public hetu_basic\
     lightcms_map_poi kaidian_kaidian ApsMisTest_Test权限 vis-classify_flower lpq_开放 cop_helloScope \
     ApsMis_fangdi_permission smartapp_snsapi_base smartapp_mapp_dev_manage iop_autocar oauth_tp_app \
     smartapp_smart_game_openapi oauth_sessionkey smartapp_swanid_verify smartapp_opensource_openapi \
     smartapp_opensource_recapi fake_face_detect_开放Scope vis-ocr_虚拟人物助理 idl-video_虚拟人物助理 smartapp_component\
     smartapp_search_plugin avatar_video_test b2b_tp_openapi b2b_tp_openapi_online', 
     'session_secret': 'c858d91f75bf1fa339594db8c31889ee'}
"""

# unit robot 返回结果
k = {'result':
         {'version': '3.0',
          'context': {
              'SYS_PRESUMED_SKILLS': ['1127361'],
              'SYS_PRESUMED_HIST': ['你好', '你好。咱们聊一会呀'],
              'SYS_VARS': {}
          },
          'timestamp': '2021-11-28 14:27:43.687',
          'service_id': 'S61860',
          'session_id': 'chat-session-id-1638080863583-fe6f33a155df45e89daaecd8398eee7f',
          'log_id': '7758521',
          'ref_id': '4l2zx_20211128142743_1254709863',
          'responses': [
              {'status': 0,
               'msg': 'ok',
               'origin': '1127361',
               'schema': {
                   'intents': [
                       {'slots': [],
                        'intent_name': 'BUILT_CHAT',
                        'intent_confidence': 1.0}]
               },
               'actions': [
                   {'confidence': 1.0,
                    'say': '你好。咱们聊一会呀',
                    'type': 'chat',
                    'action_id': 'chat_satisfy',
                    'img': []}],
               'raw_query': '你好',
               'slot_history': []}]
          },
     'error_code': 0,
     'error_msg': 'success'}


def get_access_token():
    # client_id 为官网获取的AK， client_secret 为官网获取的SK
    cache = open(TEMP_PATH + "/unit_api.ini", "a+")
    try:
        pms = cache.readlines()
        if len(pms) > 0:
            time = pms[0].strip()
            tk = pms[1].strip()
            # 计算token是否过期 官方说明一个月，这里保守29天
            time = dparser.parse(time)
            endtime = datetime.datetime.now()
            if (endtime - time).days <= 29:
                return tk
    finally:
        cache.close()
    access_token = ""
    cf = configparser.ConfigParser()
    cf.read(BASE_CONF, encoding="utf-8")
    client_id = cf.get("baidu", "app_key")
    client_secret = cf.get("baidu", "app_secret")
    host = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=%s&client_secret=%s' % (client_id, client_secret)
    try:
        response = requests.get(host)
        if response:
            res_data = response.json()
            access_token = res_data["access_token"]
    except Exception:
        return access_token


def get_robot_msg(message):
    access_token = get_access_token()
    robot_msg = []
    url = 'https://aip.baidubce.com/rpc/2.0/unit/service/v3/chat?access_token=' + access_token
    msg = message.encode("utf-8").decode("latin1")
    post_data = "{\"version\":\"3.0\",\"service_id\":\"S61860\",\"session_id\":\"\",\"log_id\":\"7758521\",\"request\":{\"terminal_id\":\"1127361\",\"query\":\"%s\"}}" % msg
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    response = requests.post(url, data=post_data, headers=headers)
    if response:
        res_data = response.json()["result"]["responses"]
        for _msg in res_data:
            for info in _msg["actions"]:
                robot_msg.append(info["say"])
    return robot_msg


if __name__ == '__main__':
    get_robot_msg("我好喜欢你啊")
