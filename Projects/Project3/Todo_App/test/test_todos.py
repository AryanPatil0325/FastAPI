from ..router.todos import get_db, get_current_user
from fastapi import status
from .utils import *

app.dependency_overrides[get_db] = override_get_db # whenever get_db is called it will point to override_get_db which is a testing database dependency
app.dependency_overrides[get_current_user] = override_get_current_user

# test for all records
def test_all_authenticated_records(test_todo):
    response = client.get("/todos/records")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{
        "title" : "Learn to code",
        "description" : "Need to learn everyday",
        "priority" : 5,
        "complete" : False,
        "owner_id" : 1,
        "id": 1
    }]

# test for get record by id
def test_single_authenticated_record(test_todo):
    response = client.get("/todos/records/1")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "title" : "Learn to code",
        "description" : "Need to learn everyday",
        "priority" : 5,
        "complete" : False,
        "owner_id" : 1,
        "id": 1
    }

# test for get record by id not found 
def test_single_authenticated_record_not_found(test_todo):
    response = client.get("/todos/records/999")
    assert response.status_code == 404
    assert response.json() == {"detail":"Todo ID not found"}

# test to check adding a new todo
def test_create_todo(test_todo):
    request_data = {
        "title" : "New Todo",
        "description" : "New Todo",
        "priority" : 5,
        "complete" : False,
        "owner_id" : 1
    }

    response = client.post("/todos/create_todo",json=request_data)
    assert response.status_code == 201

    db = TestSessionLocal()
    test_model = db.query(Todos).filter(Todos.id == 2).first()
    assert test_model.title == request_data.get('title')
    assert test_model.description == request_data.get('description')
    assert test_model.priority == request_data.get('priority')
    assert test_model.complete == request_data.get('complete')
    assert test_model.owner_id == request_data.get('owner_id')

# test to update todo
def test_authenticated_update_todo(test_todo):
    request_update_data = {
        "title" : "New Updated Todo",
        "description" : "New Updated Description",
        "priority" : 2,
        "complete" : True,
        "owner_id" : 1
    }

    response = client.put("/todos/update_todo/1",json= request_update_data)
    assert response.status_code == 204
    db = TestSessionLocal()
    test_model = db.query(Todos).filter(Todos.id == 1).first()
    assert test_model.title == request_update_data.get("title")
    assert test_model.description == request_update_data.get("description")
    assert test_model.priority == request_update_data.get("priority")
    assert test_model.complete == request_update_data.get("complete")
    assert test_model.owner_id == request_update_data.get("owner_id")

# test update not found
def test_update_todo_not_found(test_todo):
    request_update_data = {
        "title" : "New Updated Todo",
        "description" : "New Updated Description",
        "priority" : 2,
        "complete" : True,
        "owner_id" : 1
    }

    response = client.put("/todos/update_todo/999",json= request_update_data)
    assert response.status_code == 404
    assert response.json() == {"detail":"Todo ID not found"}

# test delete todo
def test_delete_todo(test_todo):
    response = client.delete("/todos/delete_todo/1")
    assert response.status_code == 204
    db = TestSessionLocal()
    test_model = db.query(Todos).filter(Todos.id == 1).first()
    assert test_model is None

# test delete todo not found
def test_delete_todo_not_found(test_todo):
    response = client.delete("/todos/delete_todo/999")
    assert response.status_code == 404
    assert response.json() == {"detail":"Todo not found"}
