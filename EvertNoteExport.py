# -*- coding: utf-8 -*-
# Author by 程剑锋
# Contact on :程剑锋
# Any question please contact with me by Email: chengjianfeng@jd.com
# -------------------- Code Start -------------------- #

"""
    环境:本程序执行环境为Python3,请注意Python版本
    作用:
        用于将印象笔记中的内容批量的导入到 hexo 中
    操作步骤:
        在印象笔记中,将需要导出的笔记全部点选后,一次性到一个文件夹中
        确保 hexo 仓库的source目录下存在 _post 和 Resources 文件夹
        然后设置以下值:
        target_source_dir 是 hexo 仓库source文件夹的路径
        target_dest_dir 是hexo仓库的source文件夹所在的目录
        target_categories 是本次导出笔记的分类标记,可以有多个使用","分隔开来
        target_tags 是本次导出笔记的标签标记,可以有多个使用","分隔开来
        执行命令: python EvertNoteExport.py 即可完成导入。
    特性:
        支持同一笔记覆盖性写入,新数据会直接覆盖旧数据的所有文件
"""

import os
import urllib.request
import shutil
import time
import glob


# ----------- 全局参数配置区  -----------------

# 是Hexo目录的source目录
target_dest_dir = "/Users/chengjianfeng/Documents/Github/Hexo/hexo/source"

# 源目录下,导出的 html 和 .resources 文件夹 都在这个目录下
# 注意,请不要随意修改 html 和 .resources 文件夹的名字,否则部署到 hexo 上会出现链接错误
target_source_dir = "/Users/chengjianfeng/Desktop/iOS读书笔记"

# 表示此次导入的内容的分类 以及 标签
target_categories = ["iOS笔记"]     # 默认设为 "默认"
target_tags = ["iOS", "读书笔记"]


# ------------  全局函数区  -------------------

def validateString(obj):
    # 需要兼顾 basestring \ str \ unicode 三种字符串类情况
    if isinstance(obj, str) and len(obj) > 0:
        return True
    else:
        return False


def validateList(obj):
    if isinstance(obj, list) and len(obj) > 0:
        return True
    else:
        return False


# 返回主用户目录
def getHomeDirPath():
    ret = os.environ["HOME"]
    if validateString(ret):
        return ret
    ret = os.path.expandvars("$HOME")
    if validateString(ret):
        return ret
    ret = os.path.expanduser("~")
    if validateString(ret):
        return ret
    return ""


# 返回转化后的目录
def getAbsolutePath(filePath):
    if not validateString(filePath):
        return None
    if filePath[0:2] == "~/":
        return getHomeDirPath() + filePath[1:]
    else:
        return filePath


# [非递归]返回指定文件夹下的所有文件夹,是否需要隐藏文件可以指定,是否需要路径可以指定
def getAllDirsInSpecialDir(specifyDirName, needPathName = False, needHideElement = True):
    if not validateString(specifyDirName):
        return None
    specifyDirName = getAbsolutePath(specifyDirName)
    if not os.path.isdir(specifyDirName):
        return None
    resultList = []
    subLeafList = os.listdir(specifyDirName)
    for element in subLeafList:
        if os.path.isdir(specifyDirName + "/" + element):
            if element.find(".") == 0 and needHideElement:
                continue
            if needPathName:
                resultList.append(specifyDirName + "/" + element)
            else:
                resultList.append(element)
    return resultList


# 安全的获取指定文件内的content,返回str。出错则返回None
def safeGetFileContentStr(fileName, isNeedPrint = False):
    if not validateString(fileName):
        return None
    fileName = getAbsolutePath(fileName)
    if not os.path.isfile(fileName):
        return None
    try:
        fileFp = open(fileName, "r+")
    except Exception as e:
        if isNeedPrint:
            print("Error: open file %s error,exception detail : %s " % (fileName, str(e)))
        return None

    try:
        fileData = fileFp.read()
    except Exception as e:
        if isNeedPrint:
            print("Error: open file %s error,exception detail : %s" % (fileName, str(e)))
        fileFp.close()
        return None
    fileFp.close()
    return fileData


def safeWriteFileContentStr(fileName, content, isNeedPrint = False):
    ret = True
    if not validateString(content):
        return False
    fileName = getAbsolutePath(fileName)

    if os.path.exists(fileName):
        safeRemovePath(fileName)

    try:
        writerFileFP = open(fileName, "w")
    except Exception as e:
        if isNeedPrint:
            print("Error: writer file %s error, exception detail : %s" % (fileName, str(e)))
        return False

    try:
        writerFileFP.write(content)
    except Exception as e:
        if isNeedPrint:
            print("Error: writer file %s error, exception detail : %s" % (fileName, str(e)))
        ret = False
    finally:
        writerFileFP.close()
    return ret


def safeRemovePath(path):
    if not validateString(path):
        return False
    path = getAbsolutePath(path)
    if os.path.isfile(path):
        os.remove(path)
        return True
    if os.path.isdir(path):
        shutil.rmtree(path)
        return True
    return False


# 安全的copy文件夹到指定的位置,指定位置必须不能存在同名文件夹
def safeCopyDirToNewDir(sourceDir, targetDir):
    if not validateString(sourceDir) or not validateString(targetDir):
        return False
    sourceDir = getAbsolutePath(sourceDir)
    targetDir = getAbsolutePath(targetDir)
    if not os.path.exists(sourceDir):
        return False
    if os.path.exists(targetDir):
        safeRemovePath(targetDir)
    try:
        shutil.copytree(sourceDir, targetDir)
    except:
        return False
    return True


def formatCategoriesAndTags(sourceList):
    if not validateList(sourceList):
        return ""
    elif len(sourceList) == 1:
        return sourceList[0]
    else:
        ret = "\n\t- ".join(sourceList)
        ret = "\n\t- " + ret
        return ret


# ---------------  正式代码区  -----------------

target_dest_html_dir = target_dest_dir + "/_posts"
target_dest_resource_dir = target_dest_dir + "/Resources"

if not validateList(target_categories):
    target_categories = ["默认"]

export_dir_list = getAllDirsInSpecialDir(target_source_dir, True)
export_html_list = glob.glob(target_source_dir + "/*.html")

if not validateList(export_html_list):
    print("Error: target_source_dir is empty,target_source_dir = %s", target_source_dir)

for source_html_path in export_html_list:
    source_html_basename = os.path.basename(source_html_path)
    if source_html_basename == "index.html" or len(source_html_basename) < 5 or source_html_basename[-5:] != ".html":
        continue

    note_name = source_html_basename[0:-5]
    url_name = urllib.request.quote(note_name)

    need_replace_str = url_name + ".resources"
    replace_str = "/Resources/" + need_replace_str

    dest_html_path = target_dest_html_dir + "/" + os.path.basename(source_html_path)

    source_content = safeGetFileContentStr(source_html_path)
    if not source_content:
        print("Error: source_html_path is error! source_html_path = %s", source_html_path)
    source_content = source_content.replace(need_replace_str, replace_str)

    source_append_content = "---\n" + "title: " + note_name + "\n" + "date: " + time.strftime('%Y-%m-%d %H:%M:%S',
                                                                                              time.localtime(
                                                                                                      time.time())) + "\n" + "tags: " + formatCategoriesAndTags(
        target_tags) + "\n" + "categories: " + formatCategoriesAndTags(target_categories) + "\n---\n\n"
    source_content = source_append_content + source_content
    safeWriteFileContentStr(dest_html_path, source_content)

if validateList(export_dir_list):
    for source_resource_path in export_dir_list:
        resource_basename = os.path.basename(source_resource_path)
        if not ".resources" in resource_basename:
            continue
        dest_resource_path = target_dest_resource_dir + "/" + resource_basename
        safeCopyDirToNewDir(source_resource_path, dest_resource_path)
