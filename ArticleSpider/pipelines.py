# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.pipelines.images import ImagesPipeline
import codecs
import json
from scrapy.exporters import JsonItemExporter


class ArticlespiderPipeline:
    def process_item(self, item, spider):
        return item


# 使用json的方式将item导出为json
class JsonWithEncodingPipeline(object):

    def __init__(self):
        # 第二个参数 a 代表追加到文末 w代表替换
        self.file = codecs.open("article.json", "a", encoding="utf-8")

    def process_item(self, item, spider):
        # 将item转化为字典 输出到文件上 一定要返回item
        lines = json.dumps(dict(item), ensure_ascii=False) + "\n"
        self.file.write(lines)
        return item

    def spider_closed(self, spider):
        self.file.close()


# 使用内置的jsonExporter导出
class JsonExporterPipeline(object):

    def __init__(self):
        self.file = open('articleExport.json', 'wb')
        self.exporter = JsonItemExporter(self.file, encoding="utf-8", ensure_ascii=False)
        self.exporter.start_exporting()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item

    def spider_closed(self, spider):
        self.exporter.finish_exporting()
        self.file.close()


# 配置图片下载的pipeline 存储下载的路径
class ArticleImagePipeline(ImagesPipeline):
    def item_completed(self, results, item, info):
        if "front_image_url" in item:
            for ok, value in results:
                image_file_path = value["path"]
            item["front_image_path"] = image_file_path

        return item
