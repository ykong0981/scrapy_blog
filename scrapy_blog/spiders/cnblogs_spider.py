# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy_blog.items import ScrapyBlogItem


class CnblogsSpiderSpider(scrapy.Spider):
    name = 'cnblogs_spider'
    allowed_domains = ['www.cnblogs.com']
    start_urls = ['https://www.cnblogs.com']
    index = 1
    number = 3

    # 爬取数据
    def parse(self, response):
        list = response.xpath("//div[@id='post_list']//div[@class='post_item']")
        for item in list:
            blog_item = ScrapyBlogItem()
            blog_item['title'] = item.xpath(".//h3/a/text()").extract_first()
            blog_item['url'] = item.xpath(".//h3/a/@href").extract_first()
            blog_item['describe'] = item.xpath(".//p[@class='post_item_summary']").extract_first()
            blog_item['head_img'] = item.xpath(".//p/a/img[@class='pfs']/@src").extract_first()
            blog_item['praise'] = item.xpath(".//span[@class='diggnum']//text()").extract_first()
            blog_item['author'] = item.xpath(".//div//a[@class='lightblue']//text()").extract_first()
            blog_item['clicks'] = item.xpath(".//div//span[@class='article_view']//a/text()").extract_first()
            blog_item['create_time'] = item.xpath(".//div[@class='post_item_foot']").extract_first()
            self.correct_item(blog_item)
            yield scrapy.Request(url=blog_item['url'], meta={'items': blog_item}, callback=self.parse_content,
                                 dont_filter=True)
        next_link = response.xpath("//div//div[@class='pager']//a[last()]//@href").extract_first()
        if not (next_link is None) and self.index < self.number:
            self.index = self.index + 1
            yield scrapy.Request(self.start_urls[0] + next_link, callback=self.parse)

    # 爬取文章内容
    def parse_content(self, response):
        blog_item = response.meta['items']
        blog_item['content'] = response.xpath("//div//div[@id='cnblogs_post_body']").extract_first()
        yield blog_item

    # 修正数据
    def correct_item(self, items):
        for item in items:
            if items[item] is None:
                items[item] = ''
                items[item].strip()
        items['head_img'] = "http:" + items['head_img']
        items['describe'] = self.filter_html_tag(items['describe'])
        items['create_time'] = self.get_create_time(items['create_time'])
        return items

    # 替换标签
    def filter_html_tag(self, html):
        rule = re.compile(r'<[^>]+>', re.S)
        html = rule.sub('', html)
        return html.strip()

    # 获取创建时间
    def get_create_time(self, time):
        rule = '发布于'
        location = time.index(rule)
        time = time[location + 4:location + 20]
        return time
