from enum import Enum
import os

File_Operation_Type = Enum('File_Operation_Type', 'a w')

def outTxtHeader(Opertype,fieldir ,filename,metas):
    if os.path.exists(fieldir) == False:
        os.makedirs(fieldir)
    if os.path.exists(fieldir +filename) ==True:
        return
    fileHeader =open(fieldir +filename, Opertype,encoding='utf-8')
    for title in metas:
        fileHeader.write(title + "\t")
    fileHeader.write("\n")
    fileHeader.close()

def outTxtLine(Opertype,fieldir, filename, str):
    if os.path.exists(fieldir) == False:
        os.makedirs(fieldir)
    fileHeader =open(fieldir +filename, Opertype,encoding='utf-8')
    fileHeader.write(str + "\n")
    fileHeader.close()

def outDicCon(Opertype,fieldir,filename,HeaderMetas,Dic):
    if os.path.exists(fieldir) == False:
        os.makedirs(fieldir)
    fileHeader =open(fieldir + filename, Opertype,encoding='utf-8')
    for i in HeaderMetas:
         for k in Dic.keys():
             if(i == k):
                 fileHeader.write(str(Dic[k]).replace("\r","").replace("\n","").replace("\t","") + "\t")
    fileHeader.write("\n")
    fileHeader.close();

def outList(Opertype,fieldir,filename,slist):
    if os.path.exists(fieldir) == False:
        os.makedirs(fieldir)
    fileHeader =open(fieldir + filename, Opertype,encoding='utf-8')
    for sStr in slist:
         fileHeader.write(sStr.replace("\r","").replace("\n","").replace("\t","") + "\t")
         fileHeader.write("\n")
    fileHeader.close();









