#!/usr/bin/env python
# -*- coding=utf-8 -*-
# ip获取归属地
# date:2020-10-15
# base on python3
# To use socks5 proxy,you need update the requests library: python -m pip install -U requests[socks]

import re
import os
import time
import json
import ipdb
import datx
import argparse
import requests
requests.packages.urllib3.disable_warnings()

#  python -m pip install ipip-datx
#  python -m pip install ipip-ipdb,if use python2.x or before 3.3,also should python -m  pip install ipaddress


"""
默认使用接口1,但如追求精度,可使用接口3;如有ipip本地数据库则建议优先用接口4，兼顾精度和速度.
"""
ip_query_sources_api={"1":"baidu_ip_api","2":"ip_cn_api","3":"ipip_free_api","4":"ipip_local_db_file_api"}
headers_curl={"User-Agent": "curl/7.63.0"}
headers={
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36"
}
# ipip.net 本地.ipdb、.datx数据库
db=None
db_file_type=""

def init_ipip_local_db_file():
    global db,db_file_type
    ipip_local_db_files=[file for file in os.listdir() if file.endswith(".ipdb")  or file.endswith(".datx")]
    if len(ipip_local_db_files)>0:
        ipip_local_db_file=ipip_local_db_files[0]
        try:
            db=None
            if ipip_local_db_file.endswith(".ipdb"):
                db=ipdb.City(ipip_local_db_file)
                db_file_type="ipdb"
            elif ipip_local_db_file.endswith(".datx"):
                db=datx.City(ipip_local_db_file)
                db_file_type="datx"
            else:
                return False
            print("load ipip local db file: {}".format(ipip_local_db_file))
            return True
            pass
        except Exception as e:
            # raise e
            print("load ipip local db file {} faild!".format(ipip_local_db_file))
    else:
        print("not any ipip local db file found!")
    return False

def main(target_file,outputfile,query_source_select='1',proxy={}):
    start_time=time.time()
    ips=[]
    results=[]
    #check target file is empty
    if not os.path.getsize(target_file):
        print("{} is empty!".format(target_file))
        return

    query_source_select_api_func=ip_query_sources_api[query_source_select]
    print("query source api: {}".format(query_source_select_api_func))
    if ip_query_sources_api[query_source_select] =="ipip_local_db_file_api" and not init_ipip_local_db_file():
        return
    if proxy=={}:
        print("proxy: No proxy")
    else:
        print("proxy: {}".format(proxy["http"]))
    with open(target_file,"r+") as fi:
        ips=fi.readlines()
    ips=(list)(map(lambda ip:ip.strip(),ips))
    print("{}\n".format("-"*20))
    for ip in ips:
        location= globals()[query_source_select_api_func](ip,proxy)
        result="{},{}".format(ip,location)
        print(result)
        results.append(result)
    pass
    with open(outputfile,"w") as fo:
        for x in results:
            fo.write(x+"\n")
    end_time=time.time()
    print("\n{}\nfinished in {}s".format("-"*20,round(end_time-start_time,2)))
    print("result saved to {}……".format(outputfile))



#老接口：https://sp0.baidu.com/8aQDcjqpAAV3otqbppnN2DJv/api.php?query=223.99.173.5&co=&resource_id=5809&t=1555296645505&ie=utf8&oe=gbk&cb=op_aladdin_callback&format=json&tn=baidu&cb=jQuery1102033277190464606443_1555296628953&_=1555296628956
def baidu_ip_api_old(ip,proxy={}):
    try:
        jres=requests.get("https://sp0.baidu.com/8aQDcjqpAAV3otqbppnN2DJv/api.php?query={}&co=&resource_id=5809&t=1555296645505&ie=utf8&oe=gbk&cb=op_aladdin_callback&format=json&tn=baidu&cb=jQuery1102033277190464606443_1555296628953&_=1555296628956".format(ip),headers=headers,proxies=proxy,verify=False)
        item=json.loads((re.findall(r"\((.*)\)",jres.text))[0])
        location=item["data"][0]["location"].replace(" ","")
        return location
        pass
    except Exception as e:
        pass
    return ""

#接口存在请求速率限制,快速访问容易导致429 Too Many Requests
def baidu_ip_api(ip,proxy=None):
    try:
        res=requests.get("https://qifu-api.baidubce.com/ip/geo/v1/district?ip={}".format(ip),headers=headers,proxies=proxy,verify=False)
        if res.status_code == 200:
            json_res=res.json()
            location="{}{}".format(json_res["data"]["prov"] if json_res["data"]["prov"]==json_res["data"]["city"] else "{}{}".format(json_res["data"]["prov"],json_res["data"]["city"]),json_res["data"]["district"])
            location =location if location.startswith(json_res["data"]["country"]) else "{}{}".format(json_res["data"]["country"],location)
            return location
            pass
    except Exception as e:
        pass
    return ""

#接口2：https://ip.cn?ip=
#速度尚可，但目前该接口已不可用
def ip_cn_api(ip,proxy={}):
    try:
        jres=requests.get("https://ip.cn?ip={}".format(ip),timeout=5,headers=headers_curl,proxies=proxy,verify=False).json()
        location="{}{}".format(jres.get("country"),jres.get("city"))
        return location
        pass
    except Exception as e:
        # raise e
        pass
    return ""
    
#接口3：http://freeapi.ipip.net/ 
#限速、次数,限速为单IP每秒最多 5 次请求,单ip限每日请求1000次,但精度相对前三者较高  
def ipip_free_api(ip,proxy={}):
    try:
        jres=requests.get("http://freeapi.ipip.net/{}".format(ip),timeout=10,headers=headers,proxies=proxy,verify=False)
        location="".join(jres.content.decode()[1:-1].split(",")).replace("\"","")
        return location
        pass
    except Exception as e:
        raise e
        pass
    return ""

#接口4：ipip本地.ipdb格式数据库,精度可与接口3相比，但是受版本更新限制
def ipip_local_db_file_api(ip,proxy={},country="CN"):
    if db:
        if db_file_type=="ipdb":
            # print(db.is_ipv4())
            # print(db.build_time())
            location_infos=db.find_map(ip, country)
            # print(location_info["city_name"]+location_info["isp_domain"])
            location=location_infos["city_name"]+location_infos["isp_domain"]
        elif db_file_type=="datx":
            locations=(list)(db.find(ip))
            location="{}{}{}".format(locations[0],locations[1],locations[2],locations[4])
        location=location.replace("阿里云/电信/联通/移动/铁通/教育网","阿里云")
        return location
    return ""
    pass

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', dest='file', default='ip.txt', help='ip input file')
    parser.add_argument('-s', '--source ', dest='source', default='1', help='ip location query source api:1.baidu;2.ip.cn;3.ipip free;4.ipip local db file')
    parser.add_argument('-p', '--proxy ', dest='proxy', default='', help='api requets proxy:http/socks5')
    parser.add_argument('-o', '--outputfile ', dest='outputfile', default='locations.csv', help='location result outputfile')
    args = parser.parse_args()
    if not os.path.exists(args.file):
        print ('{} not exists! Please input target file!').format(args.file)
    else:
        if args.proxy:
            proxy={
                "https":args.proxy,
                "http":args.proxy
            }
        else:
            proxy={}
        main(args.file,args.outputfile,args.source,proxy)