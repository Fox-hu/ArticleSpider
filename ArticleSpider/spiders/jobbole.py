from urllib import parse

import scrapy
import re
import json
from scrapy import Request

from ArticleSpider.items import JobboleArticleItem
from ArticleSpider.utils import common


class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['news.cnblogs.com']
    start_urls = ['http://news.cnblogs.com/']

    def parse(self, response):
        # xpath的意义在于定位html中的元素
        # 根据xpath 找到div类型中id为new_list的后代元素中 类型为h2且class为new_entry的元素 的子元素类型为a的元素的 href值
        # url = response.xpath('//div[@id="news_list"]//h2[@class="news_entry"]/a/@href').extract()

        # 获取新闻列表页中的新闻url并交给scrapy进行下载后调用相应的解析方法
        # 在调试时 只用取第一个就行 避免多次请求导致ip被封 后面将[:1]去掉
        post_nodes = response.css('#news_list .news_block')[:1]
        for post_node in post_nodes:
            image_url = post_node.css('.entry_summary img::attr(href)').extract_first("")
            post_url = post_node.css('.news_entry a::attr(href)').extract_first("")
            # 有些是带域名的 有些是不带的 使用parse 如果url不带域名 则带上域名
            # 将image_url作为meta传递给parse_detail方法
            yield Request(url=parse.urljoin(response.url, post_url), meta={"front_image_url": image_url},
                          callback=self.parse_detail)

        # 获取下一页的url并交给scrapy进行下载
        next_url = response.css("div.pager a:last-child::text").extract_first("")
        if next_url == "Next >":
            next_url = response.css("div.pager a:last-child::attr(href)").extract_first("")
            yield Request(url=parse.urljoin(response.url, next_url), callback=self.parse)

    def parse_detail(self, response):
        match_re = re.match(".*?(\d+)", response.url)
        if match_re:
            # 正则表达式中的第一项符合要求的
            post_id = match_re.group(1)
            article_item = JobboleArticleItem()
            title = response.css("#news_title a::text").extract_first("")
            create_date = response.css("#news_info .time::text").extract_first("")
            match_re = re.match(".*?(\d+.*)", create_date)
            if match_re:
                create_date = match_re.group(1)
            content = response.css("#news_content").extract()[0]
            tag_list = response.css(".news_tags a::text").extract()
            tags = ",".join(tag_list)

            article_item["title"] = title
            article_item["create_date"] = create_date
            article_item["content"] = content
            article_item["tags"] = tags
            article_item["url"] = response.url
            # 正则表达式中的第一项符合要求的
            article_item["front_image_url"] = response.meta.get("front_image_url", "")

            # 将article_item作为meta传递给parse_news_info方法
            yield Request(url=parse.urljoin(response.url, "/NewsAjax/GetAjaxNewsInfo?contentId={}".format(post_id)),
                          meta={"article_item": article_item}, callback=self.parse_news_info)

    def parse_news_info(self, response):
        j_data = json.loads(response.text)
        article_item = response.meta.get("article_item", "")
        praise_num = j_data["DiggCount"]
        fav_num = j_data["TotalView"]
        comment_num = j_data["CommentCount"]

        article_item["praise_nums"] = praise_num
        article_item["fav_nums"] = fav_num
        article_item["comment_nums"] = comment_num

        article_item["url_object_id"] = common.get_md5(article_item["url"])

        yield article_item
