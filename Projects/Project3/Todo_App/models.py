# File which will help us to know the table model which we are creating

# # Table we need : 

# Name = users
# |   Id(pk)  |   email   |   username    |   first_name    |   last_name    | hashed_password | is_active |   role    |
# |  Int      |   Str     |   str         |   int           |   boolean      | str             |   boolean |   str     |


# Name = todos
# |   Id(pk)  |   title   |   description |   priority    |   complete    | owner_id(FK)   | # foreign key of users table ID
# |  Int      |   Str     |   str         |   int         |   boolean     | int            |

# imports
from database import Base
from sqlalchemy import Column,Integer,String,Boolean,ForeignKey

# class for table model - Users

# for mysql -> String(length) is required
# class Users(Base):
#     __tablename__ = "users"
#     id = Column(Integer,primary_key=True,index=True)
#     email = Column(String(200),unique=True)
#     username = Column(String(45),unique=True)
#     first_name = Column(String(45))
#     last_name = Column(String(45))
#     hashed_password = Column(String(200))
#     is_active = Column(Boolean,default=True)
#     role = Column(String(45))

# for sqlite3
class Users(Base):
    __tablename__ = "users"
    id = Column(Integer,primary_key=True,index=True)
    email = Column(String,unique=True)
    username = Column(String,unique=True)
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean,default=True)
    role = Column(String)
    phone_number = Column(String)


# class for table model - Todos table
# for mysql
# class Todos(Base):
#     # name of the table
#     __tablename__ = "todosAPP"
#     id = Column(Integer,primary_key=True,index=True)
#     title = Column(String(200))
#     description = Column(String(200))
#     priority = Column(Integer)
#     complete = Column(Boolean,default=False)
#     owner_id = Column(Integer, ForeignKey("users.id"))

# for sqlite3    
class Todos(Base):
    # name of the table
    __tablename__ = "todosAPP"
    id = Column(Integer,primary_key=True,index=True)
    title = Column(String)
    description = Column(String)
    priority = Column(Integer)
    complete = Column(Boolean,default=False)
    owner_id = Column(Integer, ForeignKey("users.id"))
