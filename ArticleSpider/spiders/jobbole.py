from urllib import parse

import scrapy
from scrapy import Request


class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['news.cnblogs.com']
    start_urls = ['http://news.cnblogs.com/']

    def parse(self, response):
        # xpath的意义在于定位html中的元素
        # 根据xpath 找到div类型中id为new_list的后代元素中 类型为h2且class为new_entry的元素 的子元素类型为a的元素的 href值
        # url = response.xpath('//div[@id="news_list"]//h2[@class="news_entry"]/a/@href').extract()

        # 获取新闻列表页中的新闻url并交给scrapy进行下载后调用相应的解析方法
        post_nodes = response.css('#news_list .news_block')
        for post_node in post_nodes:
            image_url = post_node.css('.entry_summary img:attr(href)').extract_first("")
            post_url = post_node.css('.news_entry a::attr(href)').extarct_first("")
            # 有些是带域名的 有些是不带的 使用parse 如果url不带域名 则带上域名
            yield Request(url=parse.urljoin(response.css, post_url), meta={"font_image_url": image_url},
                          callback=self.parse_detail)

        # 获取下一页的url并交给scrapy进行下载
        next_url = response.css("div.pager a:last-child::text").extract_first("")
        if next_url == "Next >":
            next_url = response.css("div.pager a:last-child::attr(href)").extract_first("")
            yield Request(url=parse.urljoin(response.url, next_url), callback=self.parse)

    def parse_detail(self, response):
        pass
