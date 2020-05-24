import os
from datetime import datetime


path = os.path.dirname(__file__) + "/source/_posts"
name = "Java基本数据类型"
date = ""
cat = "Java"


file_name = os.path.join(path, "{0}.md".format(name))
create_file = os.path.join(path, name)
if not os.path.isdir(create_file):
    os.makedirs(create_file)

if not os.path.isfile(file_name):
    f = open(file_name, "w")
    content_list = (
        "---",
        "title: {0}".format(name),
        "date: {0}".format(date or datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        "tags: Java", "categories: {0}".format(cat),
        "---",
        "",
        "<!--more-->"
    )
    for content in content_list:
        f.write(content + "\n")
    f.close()
