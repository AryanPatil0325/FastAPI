from .utils import * 
from fastapi import status
from ..router.auth import get_db, authenticate_users, create_access_token, SECRET_KEY, ALGORITHM, get_current_user
from jose import jwt
from datetime import timedelta
from fastapi import HTTPException

app.dependency_overrides[get_db] = override_get_db

# test to authenticate user
def test_authenticate_user(test_user):
    db = TestSessionLocal()

    auth_user = authenticate_users(test_user.username,"aryan03",db)
    assert auth_user is not None

    invalid_user = authenticate_users("invalid_user","aryan03",db)
    assert invalid_user is False

    wrong_pass = authenticate_users(test_user.username,"wrongpass",db)
    assert wrong_pass is False

# test create access token
def test_create_access_token():
    test_username = "test123"
    test_user_id = 1
    test_timedelta = timedelta(days=1)
    test_role = "user"

    token = create_access_token(test_username,test_user_id,test_timedelta,test_role)
    decoded = jwt.decode(token,SECRET_KEY,ALGORITHM)
    assert decoded['sub'] == test_username
    assert decoded['id'] == test_user_id
    assert decoded['role'] == test_role

@pytest.mark.asyncio # used to run async function (install pytest-asyncio)
async def test_get_current_user():
    encode = {"sub":"testuser",'id':1,"role":"user"}
    token = jwt.encode(encode,SECRET_KEY,ALGORITHM)
    user = await get_current_user(token)
    assert user == {"username":"testuser",'user_id':1,"user_role":"user"}

@pytest.mark.asyncio
async def test_get_current_user_without_payload():
    encode = {"role":"user"}
    token = jwt.encode(encode,SECRET_KEY,ALGORITHM)

    with pytest.raises(HTTPException) as exe:
        await get_current_user(token=token)

    assert exe.value.status_code == 401
    assert exe.value.detail == "Could not validate user"
    