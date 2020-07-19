from scrapy.cmdline import execute

import sys
import os

# 将项目的根目录添加到系统的path中 用于执行cmd命令
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 执行命令
execute(["scrapy", "crawl", "jobbole"])
