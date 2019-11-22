# -*- coding: utf-8 -*-
import scrapy
import json
from datetime import datetime
from bilibiliSpider.items import BilibilispiderItem

class BilibiliSpider(scrapy.Spider):
    name = 'bilibili'
    allowed_domains = ['bilibili.com']
    # start_urls = ['http://bilibili.com']

    # 网上找bilibili番剧列表的接口
    # https://www.bilibili.com/read/cv3044037/
    # https://github.com/RicterZ/AnimeReminder/issues/9
    # https://bangumi.bilibili.com/web_api/timeline_global

    # 索引页的ajax
    # 使用format拼接填充{}的数值
    request_url = 'https://bangumi.bilibili.com/media/web_api/search/result?page={}&season_type=1&pagesize=20'

    page = 1
    start_urls = [request_url.format(page)]

    # 番剧信息的ajax请求
    season_url = 'https://bangumi.bilibili.com/ext/web_api/season_count?season_id={}&season_type=1&ts={}'

    # 番剧详情页的ajax请求
    media_url = 'https://www.bilibili.com/bangumi/media/md{}'


    all_urls = [
        start_urls,
        season_url,
        media_url
    ]


    def parse(self, response):
        # # for test
        # self.log('hyl-%s' % str(response.url))
        # self.log('hyl-%s' % str(response.url.split('/')))
        # page = response.url.split('/')[-2]
        # filename = str('bilibili-%s.html' % page)
        # with open(filename, 'wb') as f:
        #     f.write(response.body)
        # self.log('Save file %s' % filename)
        self.log('hyl-parse')
        # self.log(response.meta)
        with open('bilibili-1.html', 'wb') as f:
            f.write(response.body)

        # response.body.decode(response.encoding)和response.text最终效果类似，
        # 但是text一次后就存入缓存后续不会再有额外的开销
        list_data = json.loads(response.text).get('result').get('data')
        # self.log('hyl-%s' % str(list_data))
        if list_data is None or list_data==[]:  # 如果响应中没有数据，则结束执行
            return
        for data in list_data:
            ts = datetime.timestamp(datetime.now())
            # Request and Response
            # callback（callable） - 将使用此请求的响应（一旦下载）作为其第一个参数调用的函数。
            # 如果请求没有指定回调，parse()将使用spider的parse()方法。请注意，如果在处理期间引发异常，则会调用errback。
            yield scrapy.Request(url=self.season_url.format(data.get('season_id'), ts),
                                 callback=self.parse_details,
                                 meta=data)

        self.page += 1  # 生成下一页的请求
        yield scrapy.Request(url=self.request_url.format(self.page),
                             callback=self.parse)

    def parse_details(self, response):
        item = BilibilispiderItem()
        self.log('hyl-parse_details')
        # self.log(response.meta)
        with open('bilibili-2.html', 'wb') as f:
            # 2019-11-13 13:30:55 [bilibili] DEBUG:
            # {'badge': '会员专享', 'badge_type': 0,
            # 'cover': 'http://i0.hdslb.com/bfs/bangumi/216e1bdaf88244215a13b1154116805ee9adbe07.png',
            # 'index_show': '全13话', 'is_finish': 1,
            # 'link': 'https://www.bilibili.com/bangumi/play/ss26297',
            # 'media_id': 4762734,
            # 'order': {'follow': '217.9万追番', 'play': '6733万次播放', 'pub_date': 1546790400,
            # 'pub_real_time': 1546790400, 'renewal_time': 1554132600,
            # 'score': '9.9分', 'type': 'follow'}, 'season_id': 26297,
            # 'title': '路人超能100 II(灵能百分百 第二季)', 'depth': 4,
            # 'download_timeout': 180.0, 'download_slot': 'bangumi.bilibili.com',
            # 'download_latency': 0.04638218879699707}
            f.write(response.body)

        # Unlike the Response.request attribute,
        # the Response.meta attribute is propagated along redirects and retries,
        # so you will get the original Request.meta sent from your spider.
        # Request.meta特殊键，meta获得是原始request的meta，虽然进入parse detail时已经reque另一个url
        # 该Request.meta属性可以包含任何任意数据，但有一些特殊的键由Scrapy及其内置扩展识别。
        meta_data = response.meta
        item['season_id'] = meta_data.get('season_id')
        item['media_id'] = meta_data.get('media_id')
        item['title'] = meta_data.get('title')
        item['index_show'] = meta_data.get('index_show')
        item['is_finish'] = meta_data.get('is_finish')
        item['video_link'] = meta_data.get('link')
        item['cover'] = meta_data.get('cover')
        item['pub_real_time'] = meta_data.get('order').get('pub_real_time')
        item['renewal_time'] = meta_data.get('order').get('renewal_time')
        # item['score'] = meta_data.get('order').get('score')

        resp_data = json.loads(response.text).get('result')
        # self.log(str(resp_data))
        item['favorites'] = resp_data.get('favorites')
        item['coins'] = resp_data.get('coins')
        item['views'] = resp_data.get('views')
        item['danmakus'] = resp_data.get('danmakus')
        # fa = resp_data.get('favorites')
        # co = resp_data.get('coins')
        # vi = resp_data.get('views')
        # dan = resp_data.get('danmakus')
        # return item['favorites'], item['coins'], item['views'], item['danmakus']
        # return fa, co, vi, dan
        yield scrapy.Request(url=self.media_url.format(item['media_id']),
                             callback=self.parse_media,
                             meta=item)

    def parse_media(self, response):
        self.log('hyl-parse_media')
        with open('bilibili-3.html', 'wb') as f:
            f.write(response.body)
        item = response.meta
        # 选取带有属性class='x'的div元素
        resp = response.xpath('//div[@class="media-info-r"]')
        # 选取带有属性class='x'的span元素中的span元素的text元素的任何类型节点
        item['media_tags'] = resp.xpath('//span[@class="media-tags"]/span/text()').extract()
        item['score'] = resp.xpath('//div[@class="media-info-score-content"]/text()').extract()[0]
        item['cm_count'] = resp.xpath('//div[@class="media-info-review-times"]/text()').extract()[0]
        yield item

