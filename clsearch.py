# encoding=utf8
import requests
import re
from bs4 import BeautifulSoup
import bs4
import os
import time
import threading
import tkMessageBox

from Tkinter import *

class SearchSite(object):
    def __init__(self):
        self.session = requests.session()

    def vivist(self, ref, url):
        headers = {
            'Connection': 'keep-alive',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.130 Safari/537.36',
            'Refer' : ref,
        }
        response = self.session.get(url, headers=headers)
        return response.text
    def str2hex(self, str):
        hex_str = ''
        for ch in str:
            hex_str = hex_str + ('%x') % ord(ch)
        return hex_str

class CLBB(SearchSite):
    def __init__(self):
        super(CLBB, self).__init__()
        self.url = "http://www.cilibaba.com"
        self.hash_id_cer = re.compile(r'var url = \'/api/json_info\?hashes=\' \+ \'(.*)\';')
        self.hash_info_cer = re.compile(r'\"info_hash\": \"(\w+)\"')
        self.next_page_cer = re.compile(r'<li><a href=\"./(.*)\"> Next')

    def start(self, keyword):
        print "开始搜索 ", keyword
        self.search_url = '%s/search/%s' % (self.url, keyword)
        data = self.vivist('', self.search_url)
        filename = keyword.decode("utf8")
        if os.path.exists("result") != True:
          os.makedirs("result")
        try:
            t = time.localtime()
            file_path = 'result/%s_%04d_%02d_%02d_%02d_%02d_%02d.txt' % (filename, t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec)
            fp = open(file_path, 'wb')
            soup = self.writefile(fp, data)

            global next_page_list
            next_page_list = self.next_page_cer.findall(data)
            while len(next_page_list) > 0:
                next_page_url = '%s/%s' % (self.search_url, next_page_list[0].encode("utf8"))
                print ">>>"
                next_page_data = self.vivist(self.search_url, next_page_url)
                soup = self.writefile(fp, next_page_data)
                next_page_list = self.next_page_cer.findall(next_page_data)

            fp.close()
        except Exception, e:
            print "连接中断，意外终止", Exception, e


    def writefile(self, fp, data):
        soup = BeautifulSoup(data, "html.parser")
        if not soup.table:
            return soup

        for v in soup.table:
            if isinstance(v, bs4.element.Tag):
              fp.write(v.td.a[u'title'].encode("utf-8") + '\r\n')
              print " ", v.td.a['title'].encode("utf8")
              href = v.td.a[u'href']
              info_url = '%s%s' % (self.url, href)
              data = self.vivist('', info_url)
              info_soup = BeautifulSoup(data, "html.parser")
              fp.write("文件列表:\r\n")
              for li in info_soup.find_all("li"):
                if isinstance(li, bs4.element.Tag):
                  if li.string and li.a == None:
                    fp.write('\t' + li.string.encode("utf-8") + '\r\n')
              hash_id = self.hash_id_cer.findall(data)[0]
              hash_info_url = "%s/api/json_info?hashes=%s" % (self.url, hash_id)
              response = self.vivist('', hash_info_url)
              hash_info = self.hash_info_cer.findall(response)[0]
              magnet = "磁力链地址: magnet:?xt=urn:btih:" + hash_info.encode("utf-8")
              fp.write(magnet + '\r\n*********************************************************\r\n')

        return soup

def main():
    root = Tk()
    root.title("老司机")
    var = StringVar()
    show_msg = Label(root, textvariable=var).pack()
    var.set("请输入要搜索的关键字")
    entry = Entry(root, width = 50)
    entry.pack()

    searching_list = {}
    def updateMsg():
        msg = "正在搜索"
        for k, v in searching_list.items():
            msg = msg + " " + k.encode("utf-8")
        if msg == "正在搜索":
            var.set("搜索全部完成!")
        else:
            var.set(msg)

    def addSearchKeyword(keyword):
        searching_list[keyword] = "ss"
        updateMsg()

    def removeSearchKeyword(keyword):
        del searching_list[keyword]
        updateMsg()

    def startSearch(searcher, keyword):
        addSearchKeyword(keyword)
        searcher.start(keyword.encode("utf-8"))
        removeSearchKeyword(keyword)

    def Search():
        keyword = entry.get()
        t1 = threading.Thread(target = startSearch, args = (CLBB(), keyword))
        t1.start()

    menu = Menu(root)

    def help():
        tkMessageBox.showinfo(
            "如何使用",
            "1.输入要搜索的网络资源的关键字。\n（上一个关键字点\"开始搜索\"之后可立即开始搜索下一个，无须等待上一个完成）\n2.搜索完成后，查看result文件夹下生成的对应的关键字文件。\n3.找到磁力链地址，复制到迅雷，百度云，115网盘，QQ旋风等工具新建下载即可。"
        )

    menu.add_command(label="如何使用", command = help)
    root.config(menu=menu)

    def about():
        tkMessageBox.showinfo(
            "关于",
            "To: \n    私人使用！请勿随意传播！\n\t\t\t\t\tFrom: yestein"
        )
    menu.add_command(label="关于这个软件", command = about)
    root.config(menu=menu)

    Button(root, text = "开始搜索", command = Search).pack()
    root.update() # update window ,must do
    curWidth = root.winfo_reqwidth() # get current width
    curHeight = root.winfo_height() # get current height
    scnWidth,scnHeight = root.maxsize() # get screen width and height
    # now generate configuration information
    tmpcnf = '%dx%d+%d+%d'%(curWidth,curHeight,
    (scnWidth-curWidth)/4,(scnHeight-curHeight)/2 - 100)
    root.geometry(tmpcnf)

    root.mainloop()

if __name__ == '__main__':
    main()
