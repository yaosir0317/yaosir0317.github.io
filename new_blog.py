import os
import sys
from datetime import datetime


path = "./source/_posts"


def gen_blog(name: str, date: str, cate: str):
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
            "tags: {0}".format(cat), 
            "categories: {0}".format(cat),
            "---",
            "",
            "<!--more-->"
        )
        for content in content_list:
            f.write(content + "\n")
        f.close()


if __name__ == '__main__':
    name = sys.argv[1]
    date = sys.argv[2]
    cat = sys.argv[3]
    gen_blog(name, date, cat)
