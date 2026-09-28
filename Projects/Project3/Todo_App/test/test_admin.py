from .utils import * 
from ..router.admin import get_db, get_current_user
from fastapi import status

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

# test to read all todos
def test_read_admin_todos(test_todo):
    response = client.get("/admin/todos")
    current_user = override_get_current_user()
    if current_user["user_role"] == "admin":
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == [{
            "title" : "Learn to code",
            "description" : "Need to learn everyday",
            "priority" : 5,
            "complete" : False,
            "owner_id" : 1,
            "id": 1
        }]
    else:
        assert response.status_code == 401
        assert response.json() == {"detail":"Authentication Failed. Only Admin can access."}

# test delete admin authenticated todos
def test_delete_authenticated_todos(test_todo):
    response = client.delete("/admin/delete_todo/1")
    current_user = override_get_current_user()
    if current_user["user_role"] == "admin":
        assert response.status_code == status.HTTP_204_NO_CONTENT
        db = TestSessionLocal()
        test_model = db.query(Todos).filter(Todos.id == 1).first()
        assert test_model is None
    else:
        assert response.status_code == 401
        assert response.json() == {"detail":"Authentication Failed. Only Admin can access."}
        

# test delete admin authenticated todos not found
def test_delete_authenticated_todos_not_found(test_todo):
    response = client.delete("/admin/delete_todo/999")
    current_user = override_get_current_user()
    if current_user["user_role"] == "admin":
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {"detail":"Todo not found"}
    else:
        assert response.status_code == 401
        assert response.json() == {"detail":"Authentication Failed. Only Admin can access."}


