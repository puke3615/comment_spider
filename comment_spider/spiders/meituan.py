# coding=utf-8
from scrapy import Spider, Request
from comment_spider.util import *
import json
import re

get_url = lambda page: 'http://hz.meituan.com/meishi/pn%s/' % page


def data_change():
    print('Data changed.')
    exit(0)


class MeituanSpider(Spider):
    name = 'meituan'
    page = 1
    start_urls = [get_url(page)]
    shop_index = 1

    headers = {
        'Host': 'www.meituan.com',
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Mobile Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        # 'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Cookie': 'uuid=d9f34299c1aa4700b57b.1533529950.1.0.0; _lx_utm=utm_source%3Dgoogle%26utm_medium%3Dorganic; _lxsdk_cuid=1650d8210c2c8-01cc48fa57f124-336b7b05-13c680-1650d8210c3c8; __mta=147110536.1533529952707.1533529952707.1533529952707.1; ci=50; client-id=4fb967a2-deb0-4c90-8408-2def9dc61c9a; oc=-3SKHsosP2d57O95hCYTmTexMhVqo4FIr5jQcztD5J5u_GXn3LjVWWou3uvfqHm4cPOGIMmgH3hNpYXXqbtqA66xGDYgxq8SWnCYIRpidQP13Wxum7XxTcrTNbJC_8r_5xlRsKULCrAWTz-CPQfr6HgZM1gLCuOpCxBnDwi_9JQ; lat=30.207471; lng=120.208933',
    }

    def parse(self, response):
        if response.status != 200:
            return
        poiInfos = self._parse_poiInfos(response)
        # poiId, frontImg, title, avgScore, allCommentNum, address, avgPrice, dealList
        for item in poiInfos:
            title = item['title']
            for _ in range(5):
                print('=' * 200)
            print('%d. %s' % (self.shop_index, title))
            self.shop_index += 1
            dump_comment_data(item['poiId'])
        self.page += 1
        yield Request(get_url(self.page))

    def _parse_poiInfos(self, response):
        html = response.text.encode('utf-8')
        pattern = '(?<=<script>window\._appState\s=\s).*(?=;<\/script>)'
        result = re.findall(pattern, html)
        json_data = json.loads(result[0])
        poiInfos = json_data['poiLists']['poiInfos']
        return poiInfos


from scrapy import cmdline

command = 'scrapy crawl %s' % 'meituan'
cmdline.execute(command.split(' '))
