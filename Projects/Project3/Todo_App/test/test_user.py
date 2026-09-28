from .utils import * 
from fastapi import status
from ..router.users import get_db, get_current_user

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

# test for getting current user
def test_get_current_user(test_user):
    response = client.get("/users/get_user")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["email"] == "aryanpatil123@gmail.com"
    assert response.json()["username"] == "AryanPatil03"
    assert response.json()["first_name"] == "Aryan"
    assert response.json()["last_name"] == "Patil"
    assert response.json()["role"] == "admin"
    # since json() == {} -> over here the hashed password will never match

# test for changing password
def test_update_password(test_user):
    request_data = {"existing_pass":"aryan03","new_password":"patilavs03"}
    response = client.put("/users/change_password",json=request_data)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message":"Password Changed Successfully"}

# test for invalid existing password
def test_invalid_update_password(test_user):
    request_data = {"existing_pass":"aryan","new_password":"patilavs03"}
    response = client.put("/users/change_password",json=request_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail":"Incorrect password or Error in password change"}

# test for update phone number
def test_update_phone_number(test_user):
    response = client.put("/users/update_phone_number/9819292929")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'message':"Phone number updated successfully"}