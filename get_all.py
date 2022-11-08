import requests
import tomd
import re
from bs4 import BeautifulSoup
import os


class TTT:
    def __init__(self):
        self.header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
        }
        url = 'https://tttang.com/sort/php/?page=2'
        self.get_urls(url)

    def get_urls(self,url):
        res = requests.get(url,headers=self.header).text
        urls = re.findall('<a class="title" href="(.*?)">',res)
        for url in urls:
            url = 'https://tttang.com'+url
            self.save_markdown(url)

    def save_markdown(self,url):
        res = requests.get(url,headers=self.header).text
        self.soup = BeautifulSoup(res, 'lxml')
        self.article = self.soup.article

        if not self.get_file_name():
            return False
        self.mk_imagefile()
        self.get_filter()
        self.get_need_images()
        res = tomd.Tomd(self.article).markdown
        with open(self.get_file_name()+'.md','w+',encoding='utf-8') as f:
            f.write(res)
        print(url+'finish!')

    def get_filter(self):

        res = self.article
        res = str(res)
        res = re.sub('<br/>','',res)
        # res = re.sub('<a.*?a>','',res)
        res = re.sub('<p><code>','```',res)
        res = re.sub('<pre><code>','```',res)
        res = re.sub('</code></p>','```',res)
        res = re.sub('</code><*pre>','```',res)
        res = re.sub('<div>','',res)
        res = re.sub('</div>','',res)

        res = re.sub('<p><img','<img',res)
        res = re.sub('/></p>','/>',res)
        res = re.sub('```','',res)

        res = res.replace('<article class="articles">','').replace('</article>','')
        self.article = res

    def get_need_images(self):
        all_imgs = self.soup.find_all('img')
        for img in all_imgs:
            img = str(img)
            if img in self.article:
                #
                #
                #
                markdown_path = self.get_image_url(img)
                self.article = self.article.replace(img,markdown_path)
    def get_image_url(self,img_tag):
        url = re.findall('src="(.*?)"',img_tag)[0]
        img_name = url.split('/')[-1]
        img_name_last = img_name.split('.')[-1]
        img_file_name = self.get_file_name()
        res = requests.get(url=url,headers=self.header)
        with open(img_file_name+'/'+img_name,'wb') as f:
            f.write(res.content)

        markdown_path = '![image]('+img_file_name+'/'+img_name+')'
        return markdown_path

    def get_file_name(self):
        file_name = self.soup.head.title.get_text()
        filter = ['<','>','/','\\','|',':','"','*','?',' ']
        for i in filter:
            if i in file_name:
                file_name = file_name.replace(i,'')
        if os.path.exists(file_name+'.md'):
            return False
        return file_name
    def mk_imagefile(self):
        if not os.path.exists(self.get_file_name()):
            os.mkdir(self.get_file_name())
if __name__ == "__main__":
    ttt = TTT()
