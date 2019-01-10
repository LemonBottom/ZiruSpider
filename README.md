
简述：   
自如网使用了将图片与偏移量的方式对租房价格反爬。如下图，爬虫需要用图片识别来进行反反爬。一些开源的图片识别模块识别正确率非常低，百度云的OCR通用识别大概率会少识别一个数字，高精度识别基本不会错。

![image](https://github.com/LemonBottom/ZiruSpider/blob/master/ziru.png?raw=true)
![image](https://github.com/LemonBottom/ZiruSpider/blob/master/Screen%20Shot%202019-01-10%20at%202.27.32%20PM.png?raw=true)

使用pyecharts对数据进行简单处理，计算区域平均价格：
![image](https://github.com/LemonBottom/ZiruSpider/blob/master/ziruSpider/自如合租地区平均价格.png?raw=true)
