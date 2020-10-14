# iplocation
批量查询ip归属地

get_ip_location.py -h
usage: get_ip_location.py [-h] [-f FILE] [-s SOURCE] [-p PROXY]

optional arguments:
  -h, --help            show this help message and exit
  -f FILE, --file FILE  ip input file
  -s SOURCE, --source  SOURCE
                        ip location query source api:1.baidu;2.ip.cn;3.ipip
                        free;4.ipip local db file
  -p PROXY, --proxy  PROXY
                        api requets proxy:http/socks5

内置4种可选查询方式

- 百度api
- ip.cn api(已不可用)
- ipip.net 免费接口(单ip日限1000,可使用代理)
- ipip.net 本地数据库文件