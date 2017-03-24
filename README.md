# EvertNoteExportToHexo
用于将印象笔记导出的笔记，批量的导入到Hexo中，并正确的设置资源链接，以及 文章的标题、日期、分类和标签等内容。


## 环境:
本程序执行环境为Python3,请注意Python版本


## 作用:
用于将印象笔记中的内容批量的导入到 hexo 中


## 操作步骤:
* 在印象笔记中,将需要导出的笔记全部点选后,一次性到一个文件夹中
* 确保 hexo 仓库的source目录下存在 _post 和 Resources 文件夹
* 然后设置以下值:
    * target_source_dir 是 hexo 仓库source文件夹的路径
    * target_dest_dir 是hexo仓库的source文件夹所在的目录
    * target_categories 是本次导出笔记的分类标记,可以有多个使用","分隔开来
    * target_tags 是本次导出笔记的标签标记,可以有多个使用","分隔开来
* 执行命令: python EvertNoteExport.py 即可完成导入。


## 特性:
支持同一笔记覆盖性写入,新数据会直接覆盖旧数据的所有文件。<br>
支持批量导入笔记。<br>
