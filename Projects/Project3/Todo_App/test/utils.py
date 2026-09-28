from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy import StaticPool 
from ..database import Base
import pytest
from fastapi.testclient import TestClient
from ..main import app
from ..models import Todos, Users
from ..router.auth import bcrypt_context

SQLALCHEMY_DATABASE_URL = "sqlite:///./testdb.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL,connect_args={'check_same_thread':False},poolclass=StaticPool)

TestSessionLocal = sessionmaker(autocommit=False,autoflush=False,bind=engine)

Base.metadata.create_all(bind=engine)

# database dependency - only for testing purpose
def override_get_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()

# user dependency - get authenticated current user dependency
def override_get_current_user():
    return {'username':'AryanPatil03','user_id':1,'user_role':'user'}

client = TestClient(app=app)

@pytest.fixture
def test_todo():
    todo = Todos(
        title = "Learn to code",
        description = "Need to learn everyday",
        priority = 5,
        complete = False,
        owner_id = 1
    )
    db = TestSessionLocal()
    db.add(todo)
    db.commit()
    yield todo

    #delete the todo created after executing
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM todosAPP;"))
        connection.commit()

# for users.py we need to create a pytest.fixture, because the original endpoint checks for user is None to return an error
# but in override_get_current_user we are passing a dict so its not None, so test passes
@pytest.fixture()
def test_user():
    user = Users(
        email = "aryanpatil123@gmail.com",
        username = "AryanPatil03",
        first_name = "Aryan",
        last_name = "Patil",
        hashed_password = bcrypt_context.hash("aryan03"),
        role = "admin",
        phone_number = "1234567891"
    )
    db = TestSessionLocal()
    db.add(user)
    db.commit()
    yield user
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM users;"))
        connection.commit()