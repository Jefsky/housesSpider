# -*- coding = utf-8 -*-
# @Time : 2020/11/20 17:32
# @Auther : Jefsky
# @File : spider.py
# @Software : PyCharm

from bs4 import BeautifulSoup    # 网页解析,获取数据
import re               # 正则表达式,进行文字匹配
import urllib.request,urllib.error  # 指定URL,获取网页数据
import xlwt             # 进行excel操作
import sqlite3          # 进行SQLite数据库操作
import pymysql

def main():
    siteCity = 'bh'
    lastPage = 4
    baseUrl = "https://"+ siteCity +".fang.lianjia.com/loupan/pg"
    print('开始')
    createMysql();
    getCitys('https://www.lianjia.com/city/')

    # dataList = getData(baseUrl,siteCity,lastPage)
    # saveMysqlData(dataList)
    # savePath = "链家东莞新房数据.xls"
    # dbPath = "lianjia_newhouse.db"
    # saveData2Excel(dataList,savePath)
    # saveData2Db(dataList,dbPath)
    print('结束')

def getCitys(cityUrl):
    html = askUrl(cityUrl)
    soup = BeautifulSoup(html, "html.parser")
    links = soup.select('.city_province ul li a')
    for link in soup.select('.city_province ul li a'):
        href = link.get('href') + 'loupan/pg'
        print(href)
        site_city = re.findall('https://(\w*?)\.\w*.',href)
        print(site_city)
        sub_html = askUrl(href)
        sub_soup = BeautifulSoup(sub_html, "html.parser")
        page_box = sub_soup.find_all("div",class_='page-box')
        data_total_count = 0
        pages = 0
        if page_box != []:
            data_total_count = page_box[0].get('data-total-count')
            pages = int(data_total_count) // 10
            pages_more = int(data_total_count) % 10
            if pages_more != 0:
                pages = int(pages) + 2
            dataList = getData(href,site_city,pages)
            saveMysqlData(dataList)


def askUrl(url):
    head = {
        'user-agent': 'Mozilla / 5.0(Windows NT 10.0;Win64;x64) AppleWebKit / 537.36(KHTML, like Gecko) Chrome / 87.0.4280.66 Safari / 537.36',
        'OS': 'PC'
    }
    requset = urllib.request.Request(url,headers=head)
    html = '';
    try:
        response = urllib.request.urlopen(requset)
        html = response.read().decode('utf-8')
    except urllib.error.URLError as e:
        if hasattr(e,'code'):
            print(e.code)
        if hasattr(e,'reason'):
            print(e.reason)
    return html

def getData(baseUrl,siteCity,lastPage):
    dataList = []
    for i in range(1,int(lastPage)):
        print('第%d页'%i)
        url = baseUrl + str(i) + r'/'
        html = askUrl(url)
        soup = BeautifulSoup(html,"html.parser")
        # soup.select('.next')
        for item in soup.find_all('li',class_="resblock-list"):
            data = []
            pic = item.select('.lj-lazy')[0].get('data-original')
            data.append(pic)
            title = item.select('.name')[0].get_text()
            data.append(title)
            link = item.select('.name')[0].get('href')
            data.append(link)
            type = item.select('.resblock-type')[0].get_text()
            data.append(type)
            sale_status = item.select('.sale-status')[0].get_text()
            data.append(sale_status)
            local_area = item.select('.resblock-location span')[0].get_text()
            data.append(local_area)
            local_distin = item.select('.resblock-location span')[1].get_text()
            data.append(local_distin)
            address = item.select('.resblock-location a')[0].get_text()
            data.append(address)
            number = item.select('.number')[0].get_text()
            data.append(number)
            desc = item.select('.desc')
            if desc != []:
                desc = desc[0].get_text().strip()
            else:
                desc = ''
            data.append(desc)
            total = item.select('.second')
            if total != []:
                total = total[0].get_text()
            else:
                total = ''
            data.append(total)
            tags = item.select('.resblock-tag span')
            tag = []
            if tags != []:
                for i in tags:
                    tag.append(i.get_text())
            data.append(tag)
            areas = item.select('.resblock-area span')[0].get_text()
            data.append(areas)
            rooms = item.select('.resblock-room span')
            room = []
            if rooms != []:
                for i in rooms:
                    room.append(i.get_text())
            data.append(room)
            city = siteCity
            data.append(city)
            dataList.append(data)
    return dataList

def saveData2Excel(dataList,savePath):
    book = xlwt.Workbook(encoding="utf-8",style_compression=0)
    sheet = book.add_sheet('链家东莞新房数据',cell_overwrite_ok=True)
    col = ('缩略图','楼盘名','链接','类型','销售状态','镇区','地区','地址','单价','单价单位','总价','标签','建筑面积','居室','城市')
    for i in range(0,len(col)):
        sheet.write(0,i,col[i])
    for i in range(0,len(dataList)):
        print("第%d条"%(i+1))
        data = dataList[i]
        for j in range(0,len(col)):
            sheet.write(i+1,j,data[j])
    book.save(savePath)

def saveData2Db(dataList,dbPath):
    initDb(dbPath)
    conn = sqlite3.connect(dbPath)
    cursor = conn.cursor()
    for data in dataList:
        for index in range(len(data)):
            if index == 11 or index == 13 or index == 14:
                # print(data[index])
                data[index] = '"'+",".join(data[index])+'"'
                # print(data[index])
            else:
                data[index] = '"'+data[index]+'"'
            print(data)

        sql = '''
            insert into newhouse (
                pic,title,link,type,sale,local_area,local_dist,address,price,price_unit,price_total,tags,area,rooms,city
            ) values(%s)'''%",".join(data)

        # print(sql)
        cursor.execute(sql)
        conn.commit()
    cursor.close()
    conn.close()

def initDb(dbPath):
    sql = '''
        create table newhouse
        (
            id integer primary key autoincrement,
            title text,
            pic text,
            link text,
            type text,
            sale text,
            local_area text,
            local_dist text,
            address text,
            price text,
            price_unit text,
            price_total text,
            tags text,
            area text,
            rooms text,
            city text
        )
    '''
    conn = sqlite3.connect(dbPath)
    cursor = conn.cursor()
    cursor.execute(sql)
    conn.commit()
    conn.close()

def createMysql():
    # 打开数据库连接
    db = pymysql.connect("localhost", "root", "root", "lianjia", charset='utf8')
    cursor = db.cursor()
    cursor.execute("DROP TABLE IF EXISTS `newhouses`")
    sql = '''
            CREATE TABLE `newhouses`  (
              `id` int(11) NOT NULL AUTO_INCREMENT,
              `pic` text,
              `title` varchar(200) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL DEFAULT '',
                `link` varchar(200) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL DEFAULT '',
                `type` varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL DEFAULT '',
                `sale` varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL DEFAULT '',
                `local_area` varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL DEFAULT '',
                `local_dist` varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL DEFAULT '',
                `address` varchar(200) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL DEFAULT '',
                `price` varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL DEFAULT '',
                `price_unit` varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL DEFAULT '',
                `price_total` varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL DEFAULT '',
                `tags` varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL DEFAULT '',
                `area` varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL DEFAULT '',
                `rooms` varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL DEFAULT '',
                `city` varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL DEFAULT '',
              PRIMARY KEY (`id`) USING BTREE) 
        '''
    cursor.execute(sql)
    db.close()

def saveMysqlData(dataList):
    # 打开数据库连接
    db = pymysql.connect("localhost", "root", "root", "lianjia", charset='utf8')

    # 使用cursor()方法获取操作游标
    cursor = db.cursor()

    # SQL 插入语句
    for data in dataList:
        for index in range(len(data)):
            if index == 11 or index == 13 or index == 14:
                # print(data[index])
                data[index] = '"' + ",".join(data[index]) + '"'
                # print(data[index])
            else:
                data[index] = '"' + data[index] + '"'
            # print(data)
        sql = '''
            insert into `newhouses` (
                pic,title,link,type,sale,local_area,local_dist,address,price,price_unit,price_total,tags,area,rooms,city
            ) values(%s)''' % ",".join(data)
        # 执行sql语句
        print(sql)
        cursor.execute(sql)
        # 提交到数据库执行
        db.commit()
    # 关闭数据库连接
    db.close()

if __name__ == '__main__':
    main()