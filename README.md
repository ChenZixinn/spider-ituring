# spider_ituring
爬取ituring.com图书信息，输出到excel。Crawl ituring.com book information and output it to Excel.

##### 项目启动
```shell
scrapy crawl ituring_book
```

##### 需求分析
爬取 https://www.ituring.com.cn/book 下各图书分类200本图书信息，包含有**书名、作者、价格、阅读量、加入心愿单**数量。

##### 定义item
包含需要的字段
```python
import scrapy

class IturingItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    category = scrapy.Field()  # 分类
    book_name = scrapy.Field()  # 书名
    author = scrapy.Field()  # 作者
    price = scrapy.Field()  # 价格
    reading = scrapy.Field()  # 阅读量
    like = scrapy.Field()  # 加入心愿单
```

##### 管道里接收数据并写入excel
```python
def process_item(self, item, spider):
    # 拿到分类信息
    category = item["category"]
    # 切换到对应sheet表
    sheet = self.book.get_sheet(category)
    # 查看当前写入了多少数据
    row = sheet.last_used_row + 1
    # 最多只获取200本
    if row <= 200:
        for i in range(len(self.col_index)):
            # 写入到excel表中
            sheet.write(row, i, item[self.col_index[i]])
    return item

```

##### 中间件随机切换UserAgent
```python
# 用户代理
class USERAGENT(UserAgentMiddleware):

    # 初始化 注意一定是 user_agent=''
    def __init__(self, user_agent=''):
        super().__init__(user_agent)
        self.user_agent = user_agent

    def process_request(self, request, spider):
        item = random.choice(spider.settings["UAPOOL"])
        try:
            print("当前的User-Agent是：" + item)
            request.headers.setdefault('User-Agent', item)
        except Exception as e:
            print(e)

```


##### 数据爬取
```python
import math
import scrapy
import json

from spider_ituring.ituring.items import IturingItem


class IturingBookSpider(scrapy.Spider):
    name = 'ituring_book'
    allowed_domains = ['ituring.com.cn']
    start_urls = ['https://api.ituring.com.cn/api/Category/All']
    category_url = 'https://api.ituring.com.cn/api/Search/Advanced'  # post，body为from_data所定义的样式，根据分类返回图书信息的api，
    book_url = "https://api.ituring.com.cn/api/Book/"  # 每本图书的连接前缀
    headers = {
       'Accept': 'application/json',
       # 'Accept-Encoding': 'gzip, deflate',
       # 'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
       'Content-Type': 'application/json; charset=utf-8', # 这里声明json，不然会显示400数据错误
       # 'Referer': 'http://hotel.elong.com/search/list_cn_0101.html',
       # 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36',
       # 'X-Requested-With': 'XMLHttpRequest'
    }
    # 获取分类下数据的from参数
    from_data = {
        "categoryId": 0,  # 类型id
        "edition": 1,
        "name": "",
        "page": 1,  # 页码
        "sort": "new"
    }

    def parse(self, response):
        """
        根据爬取到的分类信息进行api查询,提交的数据为from_data说定义的样式
        :param response:
        :return:
        """
        # 获取到所有分类
        category = json.loads(response.text)
        # 拿到id
        for i in category:
            self.from_data["categoryId"] = i["id"]
            for page in range(1, math.ceil(200/15)+1):
                self.from_data["page"] = page
                yield scrapy.Request(self.category_url, headers=self.headers, callback=self.get_book_by_category,
                                     method='POST', body=json.dumps(self.from_data), encoding="utf-8", dont_filter=True)

    def get_book_by_category(self, response):
        """
        拿到一页图书的json数据
        :param response:
        :return:
        """
        page_data = json.loads(response.text)

        if(len(page_data["bookItems"]) > 0):
            for i in page_data["bookItems"]:
                # 提交到下一层
                yield scrapy.Request(self.book_url+str(i["id"]), callback=self.get_book, encoding="utf-8")

    def get_book(self, response):
        """
        将拿到的数据解析到item中，并返回
        :param response: 
        :return: 
        """
        book_data = json.loads(response.text)
        item = IturingItem()
        item["category"] = book_data["categories"][0][0]["name"]
        item["book_name"] = book_data["name"]
        item["author"] = book_data["authorNameString"]
        item["price"] = book_data["salesInfos"][1]["price"]
        item["reading"] = book_data["viewCount"]
        item["like"] = book_data["favCount"]
        print(f'分类：{item["category"]}, book_name:{item["book_name"]}, author:{item["author"]}, price:{item["price"]}, reading:{item["reading"]}, like:{item["like"]}')
        return item
```