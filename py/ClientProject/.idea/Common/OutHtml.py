import os
def outHtml(filedir,filename,HtmlCon):
    if os.path.exists(filedir) == False:
        os.makedirs(filedir)
    fileHeader =open(filedir + filename, 'w',encoding='utf8')
    fileHeader.write(HtmlCon)
    fileHeader.close()
