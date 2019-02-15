---
title: SQLAlchemy
date: 2019-02-14 15:17:15
tags: SQLAlchemy
categories: 
	- SQLAlchemy
	- SQL
---

`SQLAlchemy`是Python的 ORM 框架,Models是Django自带的ORM框架, 配置和使用比较简单,也正是因为其是Django原生的,所以兼容性远远不如SQLAlchemy;SQLAlchemy ORM框架是真正算得上是全面的ORM框架,它可以在任何使用SQL查询时使用.

<!--more-->

# 基本使用

建表

```python
# 导入SQLAlchemy
from sqlalchemy.ext.declarative import declarative_base

# 导入数据库连接引擎
from sqlalchemy import create_engine

# 导入ORM对应数据库数据类型的字段
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String

# 创建ORM模型基类
Base = declarative_base()


# 创建ORM对象
class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(32), index=True)
    age = Column(Integer, index=True)


# 创建数据库连接
engine = create_engine("mysql+pymysql://root:@127.0.0.1:3306/db2019?charset=utf8")

# 数据库中创建User对应的表
# 去engine数据库中创建所有继承Base的ORM对象类

Base.metadata.create_all(engine)
```

# 增删改查

## 增加数据

### 增加单条数据

```python
# 想要操纵数据库 打开数据库连接
from sqlalchemy.orm import sessionmaker
# 引入创建好的连接引擎
from main import engine
from main import User


# 创建会话窗口
Session = sessionmaker(engine)
# 打开会话窗口
db_session = Session()

user_obj = User(name="yao", age=18)
# 通过打开的会话窗口提交数据
db_session.add(user_obj)
# 执行会话窗口的操作
db_session.commit()
# 关闭会话窗口
db_session.close()
```

### 增加多条数据

```python
# 想要操纵数据库 打开数据库连接
from sqlalchemy.orm import sessionmaker
# 引入创建好的连接引擎
from main import engine
from main import User


# 创建会话窗口
Session = sessionmaker(engine)
# 打开会话窗口
db_session = Session()

db_session.add_all([
    User(name="y1", age=19),
    User(name="y2", age=20),
    User(name="y3", age=21)
])
# 执行会话窗口的操作
db_session.commit()
# 关闭会话窗口
db_session.close()

# 当然也你也可很任性的提交多条数据
user2 = User(name="yy",age=18)
user3 = User(name="yyy",age=18)
db_session.add(user2)
db_session.add(user3)
db_session.commit()
db_session.close()
```

## 查找数据

```python
# 想要操纵数据库 打开数据库连接
from sqlalchemy.orm import sessionmaker
# 引入创建好的连接引擎与表
from main import engine
from main import User

Session = sessionmaker(engine)
db_session = Session()

# 简单查询
user_list = db_session.query(User).all()
for user in user_list:
    print(user.name, user.age)

user = db_session.query(User).first()
print(user.name, user.age)

# 带条件的查询
user_list = db_session.query(User).filter(User.id == 1).all()
print(user_list[0].name, user_list[0].age)

user = db_session.query(User).filter_by(id=1).first()
print(user.name, user.age)

user_list = db_session.query(User).filter(User.id <= 2).all()
for user in user_list:
    print(user.name, user.age)

# 查看查询的sql语句
sql = db_session.query(User).filter(User.id >= 2)
print(sql)

# 高级查询
# and or
from sqlalchemy.sql import and_
from sqlalchemy.sql import or_
user_list1 = db_session.query(User).filter(and_(User.id >= 2, User.age >= 20)).all()
user_list2 = db_session.query(User).filter(or_(User.id >= 2, User.age >= 20)).all()

# 查询数据 指定查询数据列 加入别名
r2 = db_session.query(User.name.label('username'), User.id).first()
# 此时r2.name的别名为r2.username, r2.name就不能再使用了
print(r2.id, r2.username)

# 原生SQL筛选条件
from sqlalchemy.sql import text
r7 = db_session.query(User).from_statement(text("SELECT * FROM User where name=:name")).params(name='y1').all()
print(r7[0].name)

# 字符串匹配方式筛选条件 并使用 order_by进行排序
r6 = db_session.query(User).filter(text("id<:value and name=:name")).params(value=224, name='y1').order_by(User.id.asc()).all()
r6_ = db_session.query(User).filter(text("id<:value and name=:name")).params(value=224, name='y1').order_by(User.id.desc()).all()

# query的时候我们不在使用User ORM对象,而是使用User.name来对内容进行选取
user_list = db_session.query(User.name).all()

# 通配符
ret = db_session.query(User).filter(User.name.like('e%')).all()
ret = db_session.query(User).filter(~User.name.like('e%')).all()

# 限制
ret = db_session.query(User)[1:2]

# 排序
ret = db_session.query(User).order_by(User.name.desc()).all()
ret = db_session.query(User).order_by(User.name.desc(), User.id.asc()).all()

# 分组
from sqlalchemy.sql import func

ret = db_session.query(User).group_by(User.extra).all()
ret = db_session.query(
    func.max(User.id),
    func.sum(User.id),
    func.min(User.id)).group_by(User.name).all()

ret = db_session.query(
    func.max(User.id),
    func.sum(User.id),
    func.min(User.id)).group_by(User.name).having(func.min(User.id) >2).all()
```

## 更新数据

```python
# 想要操纵数据库 打开数据库连接
from sqlalchemy.orm import sessionmaker
# 引入创建好的连接引擎与表
from main import engine
from main import User

Session = sessionmaker(engine)
db_session = Session()

# 修改数据即先查找再修改
data = db_session.query(User).filter(User.id == 1).update({"name": "yaoshao"})
db_session.commit()
db_session.close()

# 在原有值基础上添加
db_session.query(User).filter(User.id > 0).update({User.name: User.name + "99"}, synchronize_session=False)
```

## 删除数据

```python
# 想要操纵数据库 打开数据库连接
from sqlalchemy.orm import sessionmaker
# 引入创建好的连接引擎与表
from main import engine
from main import User

Session = sessionmaker(engine)
db_session = Session()

# 先查询再删除
data = db_session.query(User).filter(User.id == 1).delete()
db_session.commit()
db_session.close()
```

# 一对多的操作 : ForeignKey

# 使用

建表

```python
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import ForeignKey
from sqlalchemy import create_engine
from sqlalchemy.orm import relationship

Base = declarative_base()


class Student(Base):
    __tablename__ = "student"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(32), index=True)
    school_id = Column(Integer, ForeignKey("school.id"))
    student2school = relationship("School", backref="school2student")


class School(Base):
    __tablename__ = "school"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(32))


engine = create_engine("mysql+pymysql://root:@127.0.0.1:3306/db2019?charset=utf8")
Base.metadata.create_all(engine)
```

# 增删改查

## 增加数据

```python
from sqlalchemy.orm import sessionmaker

from many_create import engine
from many_create import School
from many_create import Student

Session = sessionmaker(engine)
db_session = Session()

# 添加数据
sch_obj = School(name="家里蹲")
db_session.add(sch_obj)
db_session.commit()

school = db_session.query(School).filter(School.name == "家里蹲").first()
stu_obj = Student(name="yao", school_id=school.id)
db_session.add(stu_obj)
db_session.commit()
db_session.close()

# 通过relationshi正向添加
stu_obj = Student(name="yaoshao", student2school=School(name="蹲家里"))
db_session.add(stu_obj)
db_session.commit()
db_session.close()

# 通过relationship反向添加
sch_obj = School(name="蹲")
sch_obj.school2student = [Student(name="y1"), Student(name="y2")]
db_session.add(sch_obj)
db_session.commit()
db_session.close()
```

## 修改数据

```python
from sqlalchemy.orm import sessionmaker

from many_create import engine
from many_create import School
from many_create import Student

Session = sessionmaker(engine)
db_session = Session()

sch = db_session.query(School).filter(School.name == "123").first()
stu = db_session.query(Student).filter(Student.name == "yaoshao").update({"school_id": sch.id})
db_session.commit()
db_session.close()
```

## 查找数据

```python
from sqlalchemy.orm import sessionmaker

from many_create import engine
from many_create import School
from many_create import Student

Session = sessionmaker(engine)
db_session = Session()

# 通过relationsh正向查询
student_list = db_session.query(Student).all()
for student in student_list:
    print(student.name, student.student2school.name)

# 通过relationship反向查询
school_list = db_session.query(School).all()
for school in school_list:
    for student in school.school2student:
        print(student.name, school.name, school.id)
```

## 删除数据

```python
from sqlalchemy.orm import sessionmaker

from many_create import engine
from many_create import School
from many_create import Student

Session = sessionmaker(engine)
db_session = Session()

school = db_session.query(School).filter(School.name == "蹲").first()
stu = db_session.query(Student).filter(Student.school_id == school.id).delete()
db_session.commit()
db_session.close()
```

# 多对多的关系

建表

```python
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import ForeignKey
from sqlalchemy import create_engine
from sqlalchemy.orm import relationship


Base = declarative_base()


class Book(Base):
    __tablename__ = "book"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(32))
    book2author = relationship("Author", secondary="relation", backref="author2book")


class Author(Base):
    __tablename__ = "author"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(32))


class Relation(Base):
    __tablename__ = "relation"
    id = Column(Integer, primary_key=True)
    book_id = Column(Integer, ForeignKey("book.id"))
    author_id = Column(Integer, ForeignKey("author.id"))


engine = create_engine("mysql+pymysql://root:@127.0.0.1:3306/db2019?charset=utf8")
Base.metadata.create_all(engine)
```

操作

```python
from sqlalchemy.orm import sessionmaker

from many_many import engine
from many_many import Book
from many_many import Author


session = sessionmaker(engine)
db_session = session()


# 正向添加
book_obj = Book(name="书籍1")
book_obj.book2author = ([Author(name="作者1"), Author(name="作者2")])
db_session.add(book_obj)
db_session.commit()
db_session.close()

# 反向添加
author_obj = Author(name="作者3", author2book=[Book(name="书籍2"), Book(name="书籍3")])
db_session.add(author_obj)
db_session.commit()
db_session.close()


# 正向查询
author_list = db_session.query(Author).all()
for author in author_list:
    for book in author.author2book:
        print(book.name, author.name)


# 反向查询
book_list = db_session.query(Book).all()
for book in book_list:
    for author in book.book2author:
        print(author.name, book.name)
```