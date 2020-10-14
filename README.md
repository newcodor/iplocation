# iplocation
批量查询ip归属地

支持4种查询方式,默认最终输出csv文件

- 百度api(默认)
- ip.cn api(已不可用)
- ipip.net 免费接口(单ip日限1000,可使用代理)
- ipip.net 本地ipdb数据库文件(使用时将数据库文件置于同目录下)

```
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
```

使用示例:

```
get_ip_location.py -f ip.txt  -s 1 -p http://127.0.0.1:1080  -o iplocation.csv
```



