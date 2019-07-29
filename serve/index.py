import web
import time
import json
import sys
import os
import shutil

urls = (
    '/upload', 'upload',
    '/upload_check', 'uploadCheck'
)
class upload:
    def POST(self):
        data = web.input()
        if data['hash']:
            hashtxt = data['hash']
        if data['sdIndex']:
            sdIndex = data['sdIndex']
        if data['name']:
            uploadFileName = data['name']
        if data['shardCount']:
            shardCount = data['shardCount']

        if (int(shardCount)  == int(sdIndex)):  # 判断上传完最后一个文件
            mergeFile('./upload', uploadFileName, hashtxt);  # 合并文件
            shutil.rmtree('./upload/' + hashtxt)  # 删除
        else:
            filedir = './upload'
            sPs = filedir + "/" + hashtxt + "/"
            if not os.path.exists(sPs):  # 文件夹不存在
                os.makedirs(sPs)  # 创建hash文件夹
            x = web.input(blob={})
            if 'blob' in x:
                filePs = uploadFileName + ".part" + sdIndex  # 文件段保存路径
                # change this to the directory you want to store the file in.
                # filepath = x.file.filename.replace('\\', '/')  # replaces the windows-style slashes with linux ones.
                # filename = filepath.split('/')[-1]  # splits the and chooses the last part (the filename with extension)
                fout = open(sPs + filePs, 'wb')  # creates the file where the uploaded file should be stored
                fout.write(x.blob.file.read())  # writes the uploaded file to the newly created file.
                fout.close()  # closes the file, upload complete.
        return sdIndex  # 返回段索引


class uploadCheck:
    def POST(selfs):
        data = web.input()
        print(data)
        if data['hash']:
            hash = data['hash']
        if os.path.exists('./upload/' + hash):
            return str(
                len(os.listdir('./upload/' + hash)) - 1)  # 返回文件段索引
        else:
            return ""

def mergeFile(ps,nm,hs):#合并文件
    temp = open(ps+"/"+nm,'wb')#创建新文件
    count=len(os.listdir(ps+"/"+hs))
    for i in range(0,count):
        fp = open(ps+"/"+hs+"/"+nm+".part"+str(i), 'rb')#以二进制读取分割文件
        temp.write(fp.read())#写入读取数据
        fp.close()
    temp.close()

if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()
