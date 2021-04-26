import base64
import json
import pytest

from app import create_app
from data.db_session import global_init, SqlAlchemyBase, create_session
from models.users import User

__engine = None
app = create_app("secret_key")


def clear_db(engine):
    SqlAlchemyBase.metadata.drop_all(engine)
    SqlAlchemyBase.metadata.create_all(engine)


@pytest.fixture
def client():
    global __engine
    app.config['TESTING'] = True
    with app.test_client() as client:
        with app.app_context():
            __engine = global_init('db/api_test.db')
        yield client


def test_users_wrong_registration_fields(client):
    user = User(name="admin",
                email="admin@mail.ru",
                is_admin=1)
    user.set_password("admin12345")
    db_sess = create_session()
    db_sess.add(user)
    db_sess.commit()

    json_request = {"data": [{"name": "Саша",
                              "email": "test1@mail.ru",
                              "password": "password1"},
                             {"name": "Маша",
                              "password": "password1"},
                             {"name": "Саша",
                              "email": "test2@mail.ru",
                              "password": "password1"}
                             ]}

    credentials = base64.b64encode(b"admin@mail.ru:admin12345").decode("utf-8")
    response = client.post("/api/users", json=json_request,
                           headers={"Authorization": "Basic " + credentials})
    assert response.status_code == 400
    assert json.loads(response.data) == {
        "validation_error": {"bad_params": [{"name": "Маша", "password": "password1"}]}
    }


def test_correct_registration_users(client):
    json_request = {"data": [{"name": "Саша",
                              "email": "test1@mail.ru",
                              "password": "password1"},
                             {"name": "Маша",
                              "email": "test2@mail.ru",
                              "password": "password2"},
                             {"name": "Саша",
                              "email": "test3@mail.ru",
                              "password": "password3"}
                             ]}

    credentials = base64.b64encode(b"admin@mail.ru:admin12345").decode("utf-8")
    response = client.post("/api/users", json=json_request,
                           headers={"Authorization": "Basic " + credentials})
    assert response.status_code == 201
    assert json.loads(response.data) == {"users": [{"email": "test1@mail.ru"},
                                                   {"email": "test2@mail.ru"},
                                                   {"email": "test3@mail.ru"}]}


def test_patch_user_wrong_id(client):
    json_request = {"name": "Саша"}
    credentials = base64.b64encode(b"admin@mail.ru:admin12345").decode("utf-8")
    response = client.patch("/api/users/666", json=json_request,
                            headers={"Authorization": "Basic " + credentials})

    assert response.status_code == 404


def test_user_patch(client):
    json_request = {"name": "Саша"}
    credentials = base64.b64encode(b"test2@mail.ru:password2").decode("utf-8")
    response = client.patch("/api/users/3", json=json_request,
                            headers={"Authorization": "Basic " + credentials})

    assert response.status_code == 200
    assert json.loads(response.data) == {"user": {"name": "Саша",
                                                  "email": "test2@mail.ru",
                                                  "id": 3}}


def test_user_patch_forbidden(client):
    json_request = {"name": "Саша"}
    credentials = base64.b64encode(b"test2@mail.ru:password2").decode("utf-8")
    response = client.patch("/api/users/4", json=json_request,
                            headers={"Authorization": "Basic " + credentials})

    assert response.status_code == 403


def test_user_delete_wrong_id(client):
    credentials = base64.b64encode(b"admin@mail.ru:admin12345").decode("utf-8")
    response = client.delete("/api/users/666",
                             headers={"Authorization": "Basic " + credentials})

    assert response.status_code == 404


def test_user_delete_correct(client):
    credentials = base64.b64encode(b"admin@mail.ru:admin12345").decode("utf-8")
    response = client.delete("/api/users/3",
                             headers={"Authorization": "Basic " + credentials})

    assert response.status_code == 200
    assert json.loads(response.data) == {"banned_id": 3}


def test_user_get_wrong_id(client):
    credentials = base64.b64encode(b"admin@mail.ru:admin12345").decode("utf-8")
    response = client.get("/api/users/666",
                          headers={"Authorization": "Basic " + credentials})

    assert response.status_code == 404


def test_user_correct_get(client):
    credentials = base64.b64encode(b"test3@mail.ru:password3").decode("utf-8")
    response = client.get("/api/users/4",
                          headers={"Authorization": "Basic " + credentials})
    assert response.status_code == 200


def test_user_register_same_email(client):
    json_data = {"name": "Даша",
                 "email": "test1@mail.ru",
                 "password": "password1"}

    response = client.post("/api/users/personal_register", json=json_data)
    assert response.status_code == 400
    assert json.loads(response.data) == {"error": "email have been used"}


def test_correct_user_register(client):
    json_data = {"name": "Даша",
                 "email": "test4@mail.ru",
                 "password": "password4"}
    response = client.post("/api/users/personal_register", json=json_data)
    assert response.status_code == 201
    assert json.loads(response.data) == {"email": "test4@mail.ru"}


def test_wrong_params_category(client):
    credentials = base64.b64encode(b"admin@mail.ru:admin12345").decode("utf-8")
    response = client.post("/api/categories",
                           headers={"Authorization": "Basic " + credentials})

    assert response.status_code == 400


def test_correct_params_category(client):
    json_data = {"title": "Улитка в баре"}
    credentials = base64.b64encode(b"admin@mail.ru:admin12345").decode("utf-8")
    response = client.post("/api/categories", json=json_data,
                           headers={"Authorization": "Basic " + credentials})

    assert response.status_code == 201
    assert json.loads(response.data) == {"title": "Улитка в баре"}


def test_incorect_param_anecdotes_adding(client):
    json_data = {"data": [{"name": "Test1",
                           "text": "test",
                           "category": "Улитка в баре"},
                          {"name": "Test2",
                           "text": "test",
                           "category": "Улитка"},
                          {"name": "Test1",
                           "category": "Улитка в баре"}]}

    credentials = base64.b64encode(b"test3@mail.ru:password3").decode("utf-8")
    response = client.post("/api/anecdotes", json=json_data,
                           headers={"Authorization": "Basic " + credentials})

    assert response.status_code == 400
    assert json.loads(response.data) == {"validation_error": {
        "bad_params": [{"name": "Test2",
                        "text": "test",
                        "category": "Улитка"},
                       {"name": "Test1",
                        "category": "Улитка в баре"}]
    }}


def test_correct_anecdotes_adding(client):
    json_data = {"data": [{"name": "Test1",
                           "text": "test",
                           "category": "Улитка в баре"},
                          {"name": "Test2",
                           "text": "test",
                           "category": "Улитка в баре"},
                          {"name": "Test3",
                           "text": "test",
                           "category": "Улитка в баре"}]}

    credentials = base64.b64encode(b"test3@mail.ru:password3").decode("utf-8")
    response = client.post("/api/anecdotes", json=json_data,
                           headers={"Authorization": "Basic " + credentials})

    assert response.status_code == 201
    assert json.loads(response.data) == {"anecdotes": [{"name": "Test1"},
                                                       {"name": "Test2"},
                                                       {"name": "Test3"}]}


def test_one_anecdote_adding(client):
    json_data = {"name": "Test4",
                 "text": "test",
                 "category": "Улитка в баре"}

    credentials = base64.b64encode(b"test3@mail.ru:password3").decode("utf-8")
    response = client.post("/api/anecdote", json=json_data,
                           headers={"Authorization": "Basic " + credentials})

    assert response.status_code == 201


def test_get_not_moderated_anecdotes(client):
    response = client.get("/api/anecdotes/moderate")
    return response.status_code == 200


def test_incorrect_id_moderation(client):
    json_data = {"anecdote_id": 66666,
                 "is_published": 1}
    credentials = base64.b64encode(b"admin@mail.ru:admin12345").decode("utf-8")
    response = client.patch("/api/anecdotes/moderate", json=json_data,
                            headers={"Authorization": "Basic " + credentials})
    assert response.status_code == 404


def test_correct_moderation(client):
    json_data = {"anecdote_id": 1,
                 "is_published": 1}
    credentials = base64.b64encode(b"admin@mail.ru:admin12345").decode("utf-8")
    response = client.patch("/api/anecdotes/moderate", json=json_data,
                            headers={"Authorization": "Basic " + credentials})

    assert response.status_code == 200
    assert json.loads(response.data) == {"id": 1}


def test_get_random_anecdote(client):
    response = client.get("/api/anecdote")
    assert response.status_code == 200


def test_create_comment(client):
    json_data = {"anecdote_id": 1,
                 "text": "good anec"}
    credentials = base64.b64encode(b"admin@mail.ru:admin12345").decode("utf-8")
    response = client.post("/api/comments", json=json_data,
                           headers={"Authorization": "Basic " + credentials})
    assert response.status_code == 201


def test_create_comment_wrong_id(client):
    json_data = {"anecdote_id": 666,
                 "text": "good anec"}
    credentials = base64.b64encode(b"admin@mail.ru:admin12345").decode("utf-8")
    response = client.post("/api/comments", json=json_data,
                           headers={"Authorization": "Basic " + credentials})
    assert response.status_code == 404


def test_create_comment_not_pudlished(client):
    json_data = {"anecdote_id": 2,
                 "text": "good anec"}
    credentials = base64.b64encode(b"admin@mail.ru:admin12345").decode("utf-8")
    response = client.post("/api/comments", json=json_data,
                           headers={"Authorization": "Basic " + credentials})
    assert response.status_code == 400
    assert json.loads(response.data) == {"error": "anecdote haven't been published"}


def test_del_comment_wrong_id(client):
    json_data = {"comment_id": 666}
    credentials = base64.b64encode(b"admin@mail.ru:admin12345").decode("utf-8")
    response = client.delete("/api/comments", json=json_data,
                             headers={"Authorization": "Basic " + credentials})
    assert response.status_code == 404


def test_del_comment(client):
    json_data = {"comment_id": 1}
    credentials = base64.b64encode(b"admin@mail.ru:admin12345").decode("utf-8")
    response = client.delete("/api/comments", json=json_data,
                             headers={"Authorization": "Basic " + credentials})
    assert response.status_code == 200


def test_get_likes(client):
    credentials = base64.b64encode(b"admin@mail.ru:admin12345").decode("utf-8")
    response = client.get("/api/likes",
                          headers={"Authorization": "Basic " + credentials})
    assert response.status_code == 200


def test_put_like(client):
    json_data = {"anecdote_id": 1,
                 "value": -1}
    credentials = base64.b64encode(b"admin@mail.ru:admin12345").decode("utf-8")
    response = client.post("/api/likes", json=json_data,
                           headers={"Authorization": "Basic " + credentials})
    assert response.status_code == 201


# Не отбирайте костылик. Я инвалид, ножки болят(Александр)
def test_for_clearing_db():
    assert isinstance("Not test", str)
    SqlAlchemyBase.metadata.drop_all(__engine)
    SqlAlchemyBase.metadata.create_all(__engine)
