# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import json
import csv
import pymongo
from scrapy.utils.project import get_project_settings

class BilibilispiderPipeline(object):
    fieldnames = ['season_id', 'media_id', 'title',
                  'index_show', 'is_finish', 'video_link',
                  'cover', 'pub_real_time', 'renewal_time',
                  'favorites', 'coins', 'views',
                  'danmakus', 'depth', 'download_timeout',
                  'download_slot', 'download_latency', 'media_tags',
                  'score', 'cm_count'
                  ]
    def __init__(self):
        settings = get_project_settings()
        # mongo_url = settings["MONGO_URI"]
        mongo_host = settings["MONGO_HOST"]
        mongo_port = settings["MONGO_PORT"]
        mongo_db = settings["MONGO_DB"]
        mongo_col = settings["MONGO_COLLECTION"]
        # 创建MONGODB数据库链接
        client = pymongo.MongoClient(host=mongo_host, port=mongo_port)
        # 指定数据库
        mydb = client[mongo_db]
        # 存放数据的数据库表名
        self.post = mydb[mongo_col]

    def open_spider(self, spider):
        self.file = open('bilibili.json', 'w', encoding='utf-8')
        with open('bilibili.csv', 'w', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.fieldnames)
            writer.writeheader()
        pass

    def process_item(self, item, spider):
        content = json.dumps(dict(item), ensure_ascii=False) + ',\n'
        # print(content)
        # print('---content---')
        self.file.write(content)
        # mongodb
        data = dict(item)
        self.post.insert(data)

        with open('bilibili.csv', 'a', encoding='utf-8') as csvfile:
            fieldnames = ['season_id', 'media_id', 'title',
                          'index_show', 'is_finish', 'video_link',
                          'cover', 'pub_real_time', 'renewal_time',
                          'favorites', 'coins', 'views',
                          'danmakus', 'depth', 'download_timeout',
                          'download_slot', 'download_latency', 'media_tags',
                          'score', 'cm_count'
                          ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writerow(dict(item))

        return item

    def close_spider(self, spider):
        self.file.close()
        pass

# item 定义
# item['season_id'] = meta_data.get('season_id')
# item['media_id'] = meta_data.get('media_id')
# item['title'] = meta_data.get('title')
# item['index_show'] = meta_data.get('index_show')
# item['is_finish'] = meta_data.get('is_finish')
# item['video_link'] = meta_data.get('link')
# item['cover'] = meta_data.get('cover')
# item['pub_real_time'] = meta_data.get('order').get('pub_real_time')
# item['renewal_time'] = meta_data.get('order').get('renewal_time')
#
# resp_data = json.loads(response.text).get('result')
# item['favorites'] = resp_data.get('favorites')
# item['coins'] = resp_data.get('coins')
# item['views'] = resp_data.get('views')
# item['danmakus'] = resp_data.get('danmakus')
#
# item['media_tags'] = resp.xpath('//span[@class="media-tags"]/span/text()').extract()
# item['score'] = resp.xpath('//div[@class="media-info-score-content"]/text()').extract()[0]
# item['cm_count'] = resp.xpath('

# item example
# "season_id": 2546,
# "media_id": 2546,
# "title": "言叶之庭",
#
# "index_show": "全1话",
# "is_finish": 1,
# "video_link": "https://www.bilibili.com/bangumi/play/ss2546",
#
# "cover": "http://i0.hdslb.com/bfs/bangumi/99997c5adb361c2c27780ef690b13244dfda7cc7.jpg",
# "pub_real_time": 1369929600,
# "renewal_time": 1435145961,
#
# "favorites": 1345759,
# "coins": 104040,
# "views": 11444259,
#
# "danmakus": 443956,
# "depth": 8,
# "download_timeout": 180.0,
#
# "download_slot": "www.bilibili.com",
# "download_latency": 0.11623001098632812,
# "media_tags": ["日常", "少女", "治愈"],
#
# "score": "9.6",
# "cm_count": "7636人评"