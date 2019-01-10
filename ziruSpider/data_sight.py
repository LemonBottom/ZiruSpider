# Create time:2019-01-10 14:31
# Author:Chen

from pyecharts import Bar
import MySQLdb


class DataSight:

    def __init__(self):
        self.server = MySQLdb.connect(host='localhost', user='root', passwd='123', db='ziru', port=3306, charset='utf8').cursor()

    def avg_price(self):
        self.server.execute("select area,avg(price) as avg_price from zufang_20190110 group by area order by avg_price desc;")
        result = self.server.fetchall()
        bar = Bar("自如合租地区平均价格", "作者：Chen")
        bar.add("价格", [i[0] for i in result], [int(i[1]) for i in result], xaxis_interval=0)
        bar.render(path='自如合租地区平均价格.png')


if __name__ == "__main__":
    d = DataSight().avg_price()