import requests
from lxml import etree
import time

page = 35



import json

# query = "(cold -temperature) | flu"
query = r"Vulnerability Detection | learning"
fields = "title,year"

url = f"http://api.semanticscholar.org/graph/v1/paper/search/bulk?query={query}&fields={fields}&year=2023-"
r = requests.get(url).json()

print(f"Will retrieve an estimated {r['total']} documents")
retrieved = 0

with open(f"papers.jsonl", "a") as file:
    while True:
        if "data" in r and retrieved <= 1000:
            retrieved += len(r["data"])
            print(f"Retrieved {retrieved} papers...")
            for paper in r["data"]:
                print(json.dumps(paper), file=file)
        if "token" not in r:
            break
        r = requests.get(f"{url}&token={r['token']}").json()

print(f"Done! Retrieved {retrieved} papers total")




# # 目标网页的URL
# url0 = f'https://www.semanticscholar.org/venue?name=IEEE%20Transactions%20on%20Information%20Forensics%20and%20Security&page={page}&sort=pub-date'

# # 发送HTTP GET请求
# response = requests.get(url=url0)
# # 检查请求是否成功
# if response.status_code == 200:
#     # 获取网页的HTML内容
#     # time.sleep(5)
#     # 解析HTML内容
#     tree = etree.HTML(response.text)
#     # html_string = etree.tostring(tree, pretty_print=True).decode('utf-8')
#     print("[+] Tree:",tree)
#     document = tree.xpath('/')
#     print("[+] document:",document)
    
#     # 打印整个网页的HTML内容
#     # print(html_string)


def get_json_by_id(semantic_scholar_id):
    semantic_scholar_id = "5376629c08e312e5a20d1ca5bb6819b0b9a5ca0d"

    # 构造请求的URL
    url = f"https://api.semanticscholar.org/v1/paper/{semantic_scholar_id}"

    # 发起请求
    response = requests.get(url)

    # 检查请求是否成功
    if response.status_code == 200:
        data = response.json()
        # print(str(data))
        
        # 检查是否有引用文献
        if "references" in data and len(data["references"]) > 0:
            # 打印引用文献的信息，例如标题、作者、时间和Semantic Scholar-ID
            for reference in data["references"]:
                print(f"Title: {reference.get('title', 'No title available')}")
                # 打印每个引用的作者，如果有的话
                if "authors" in reference:
                    authors = ", ".join([author.get("name", "N/A") for author in reference["authors"]])
                    print(f"Authors: {authors}")
                # 打印出版年份
                print(f"Year: {reference.get('year', 'No year available')}")
                # 打印 Semantic Scholar ID
                print(f"Semantic Scholar ID: {reference.get('paperId', 'No ID available')}")
                print("-----")
        else:
            print("暂没有References")
    else:
        print(f"请求失败，状态码：{response.status_code}")








    
#     # 使用XPath表达式获取整个文档
#     # 这里我们使用'/'获取整个文档，你可以根据需要修改XPath
#     document = tree.xpath('/html/body/div[1]/div[1]/div[2]/div/div[3]/div/div[1]/a/h2/span[1]/span')
#     print(document)
    
#     # 输出整个HTML源码
#     # print(etree.tostring(document[0], pretty_print=True).decode('utf-8'))
#     print("Done!")
# else:
#     print(f"Failed to retrieve the webpage: Status code {response.status_code}")