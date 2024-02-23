# -*- coding: utf-8 -*-

import oss2

endpoint = 'http://oss-cn-shenzhen.aliyuncs.com' # 假设你的Bucket处于杭州区域

auth = oss2.Auth('rabbitchat-bucket-shenzhen', 's9xwq1XwOWt5SuhBXkNLy8IGMMEE1k')
bucket = oss2.Bucket(auth, endpoint, 'rabbitchat-bucket-shenzhen')

# Bucket中的文件名（key）为story.txt
key = 'story.txt'

# 上传
bucket.put_object(key, 'Ali Baba is a happy youth.')

# 下载
bucket.get_object(key).read()

# 删除
bucket.delete_object(key)

# 遍历Bucket里所有文件
for object_info in oss2.ObjectIterator(bucket):
    print(object_info.key)