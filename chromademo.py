#py -m pip install chromadb

import chromadb
import requests
from collections import OrderedDict

def preflight(session):
    url = "https://ssgenaius-backend.azurewebsites.net"
    headers = {
        "Content-Type": "application/json",
        "Access-Control-Request-Headers": "content_type",
        "Access-Control-Request-Method": "POST",
        "Origin": "https://genaius.z13.web.core.windows.net",
        "Referer": "https://genaius.z13.web.core.windows.net/"
    }
    preflight_response = session.options(url, headers=headers)

    # 检查preflight响应
    if preflight_response.status_code == 200:
        print("Preflight request successful")
    else:
        print("Preflight request failed")
        print(preflight_response)



def callgpt(session, prompt):
    headers = {
        "Content-Type": "application/json",
        "Access-Control-Request-Headers": "content_type",
        "Access-Control-Request-Method": "POST",
        "Origin": "https://genaius.z13.web.core.windows.net",
        "Referer": "https://genaius.z13.web.core.windows.net/"
    }
    url = 'https://ssgenaius-backend.azurewebsites.net'
    data = {"message": prompt}
    print(data)
    return session.post(url, json=data, headers=headers)

session = requests.Session()
preflight(session)
filename = 'novel4.txt'  # 文件名
delimiter = ['.']  # 分隔符列表，包括句号和回车

with open(filename, 'r') as f:
    lines = f.readlines()  # 读取文件内容为列表形式

# 对每一行进行处理
result = []
for line in lines:
    words = line.strip().split(delimiter[0])  # 以句号分割
    result.extend(words)

chunks = []
ids = []
currChunk = ""

for sentence in result:
    if len(currChunk) ==0 or len(currChunk) + len(sentence) < 100:
        currChunk += sentence + ". "
    else:
        chunks.append(currChunk)
        ids.append(str(len(chunks)))
        currChunk=""

client = chromadb.Client()
collection = client.create_collection("novel4")
collection.add(
    documents=chunks, 
    ids=ids
)

print(len(chunks))

question = input("please ask question: ")
while question != 'end':
    questionType: rangeQuestion;
    
    results = collection.query(
        query_texts=[question],
        n_results=2
    )
    print(results)

    queryIDs = []
    for idDoc in results['ids'][0]:
        print(idDoc)
        idDocInt = int(idDoc)
        for idForRange in range(idDocInt-1,idDocInt+2):
            queryIDs.append(str(idForRange))
    print(queryIDs)
    
    results2 = collection.get(
        ids= list(OrderedDict.fromkeys(queryIDs))
    )
    print(results2)
    prompt = 'please answer this question {' + question +'} with the following information: ' + '.'.join(results2['documents'])

    response = callgpt(session, prompt)
    if response.ok:
        json_data = response.json()
        print(json_data['message'])
    else:
        print(response)
        print('请求失败')
    
    question = input("\n\nplease ask question: ")

