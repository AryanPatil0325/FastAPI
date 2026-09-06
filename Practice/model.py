# | Column   | Type    | Requirement |
# | -------- | ------- | ----------- |
# | id       | INTEGER | PRIMARY KEY |
# | title    | TEXT    | NOT NULL    |
# | author   | TEXT    | NOT NULL    |
# | category | TEXT    | NOT NULL    |
# | price    | INTEGER | NOT NULL    |
# | owner_id | INTEGER | NOT NULL    |

from database import Base
from sqlalchemy import Column,Integer,String

class Books(Base):
    __tablename__ = "books"
    id = Column(Integer,primary_key=True,index=True)
    title = Column(String,nullable=False)
    author = Column(String,nullable=False)
    category = Column(String,nullable=False)
    price = Column(Integer,nullable=False)
    owner_id = Column(Integer,nullable=False)
