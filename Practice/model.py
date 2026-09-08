# Books table
# | Column   | Type    | Requirement |
# | -------- | ------- | ----------- |
# | id       | INTEGER | PRIMARY KEY |
# | title    | TEXT    | NOT NULL    |
# | author   | TEXT    | NOT NULL    |
# | category | TEXT    | NOT NULL    |
# | price    | INTEGER | NOT NULL    |
# | owner_id | INTEGER | NOT NULL    |

# Users Table
# | Column     | Type    | Requirements         |
# | ---------- | ------- | -------------------- |
# | `id`       | Integer | Primary key, indexed |
# | `username` | String  | Not nullable         |
# | `email`    | String  | Not nullable         |
# | `password` | String  | Not nullable         |
# | `role`     | String  | Not nullable         |


from database import Base
from sqlalchemy import Column,Integer,String,ForeignKey
from sqlalchemy.orm import relationship

class Users(Base):
    __tablename__ = "users"
    id = Column(Integer,primary_key=True,index=True)
    username = Column(String,nullable=False,unique=True)
    email = Column(String,nullable=False,unique=True)
    password = Column(String,nullable=False,unique=True)
    role = Column(String,nullable=False)

    # adding the relationship between users and books -> 1:m -> represent Python object connection
    books = relationship("Books",back_populates="owner")


class Books(Base):
    __tablename__ = "books"
    id = Column(Integer,primary_key=True,index=True)
    title = Column(String,nullable=False)
    author = Column(String,nullable=False)
    category = Column(String,nullable=False)
    price = Column(Integer,nullable=False)
    owner_id = Column(Integer,ForeignKey("users.id"),nullable=False)

    owner = relationship("Users",back_populates="books")

