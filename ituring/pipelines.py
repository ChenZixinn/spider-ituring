# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import xlwt


class IturingPipeline:
    # excel中对应的sheet表名称
    sheet_list = ["计算机", "科普", "设计", "经营管理", "专业数学", "个人技能", "电子通信", "心理学"]
    # 列名
    col = ("书名","作者","价格","阅读量","加入心愿单")
    # item的key
    col_index = ("book_name","author","price","reading","like")

    def process_item(self, item, spider):
        category = item["category"]
        # 切换到对应sheet表
        sheet = self.book.get_sheet(category)
        row = sheet.last_used_row + 1
        # 最多只获取200本
        if row <= 200:
            for i in range(len(self.col_index)):
                sheet.write(row, i, item[self.col_index[i]])
        return item

    def open_spider(self, spider):
        # 开启爬虫时先填写好列名
        self.book = xlwt.Workbook(encoding='utf-8',style_compression=0)
        for sheet_name in self.sheet_list:
            sheet = self.book.add_sheet(sheet_name, cell_overwrite_ok=True)

            for i in range(len(self.col)):
                sheet.write(0, i, self.col[i])

    def close_spider(self, spider):
        # 关闭时保存
        self.book.save(f"./数据.xls")
