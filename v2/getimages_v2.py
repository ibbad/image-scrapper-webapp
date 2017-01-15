import sys
from lxml import html
import requests
import urlparse
import os

def process_links(links):
    x = []
    for link in links:
        # link = link.split('?')[0]
        if link[-3:] == 'jpg' or link[-4:] == 'jpeg' or link[-3:] == 'png' or\
                link[-3:] == 'gif':
            x.append(link)
    return x

url = 'http://www.time.com'

page = requests.get(url)

tree = html.fromstring(page.text)
img = tree.xpath('//img/@src')
links = tree.xpath('//a/@href')

img_links = process_links(links)

img.extend(img_links)
if len(img) == 0:
    sys.exit("No images found")


images = [urlparse.urljoin(page.url, url) for url in img]


for x in range(0, len(img)):
    if img[x][:4] != "http":
        img[x] = "https:"+img[x]

with open('img_urls.txt', 'w+') as f:
    for im in img:
        f.write(im+'\n')
    f.close()
    sys.exit(0)


if not os.path.exists('images'):
    os.makedirs('images')

failed = 0
for img_url in img:
    try:
        tmp = requests.request('get', img_url)
        f = open('images/%s' % img_url.split('/')[-1], 'w')
        f.write(tmp.content)
        f.close()
        # print("successful:"+img_url)
    except Exception as ex:
        # print("failed:"+img_url)
        print(ex)
        failed +=1
        pass


print("Done, Failed to download %s images " % failed)