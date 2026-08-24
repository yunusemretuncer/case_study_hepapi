import sys
from unittest.mock import MagicMock, patch
import pytest


@pytest.fixture
def app_module():
    """
    app.py import edilirken gercek bir MongoDB'ye baglanmaya calisiyor
    (MongoClient(os.getenv("MONGODB_URI"))). Import etmeden once
    pymongo.MongoClient'i sahte (mock) bir client ile degistiriyoruz ki
    testler gercek bir Mongo instance'ina ihtiyac duymasin.
    """
    with patch("pymongo.MongoClient") as MockClient:
        mock_db = MagicMock()
        mock_db.settings.count_documents.return_value = 1  # task_id zaten "var" say

        MockClient.return_value.TaskManager = mock_db

        import run as flask_app_module
        flask_app_module.db = mock_db
        yield flask_app_module

    sys.modules.pop("run", None)  # bir sonraki test temiz import etsin


@pytest.fixture
def client(app_module):
    app_module.app.config["TESTING"] = True
    app_module.app.config["WTF_CSRF_ENABLED"] = False  # test client CSRF token gondermiyor
    with app_module.app.test_client() as c:
        yield c


# ---------- Is mantigi (asil unit testler) ----------

def test_updateTaskID_increments_value(app_module):
    app_module.db.settings.find_one.return_value = {"value": 5}

    app_module.updateTaskID(3)

    app_module.db.settings.update_one.assert_called_once_with(
        {"name": "task_id"},
        {"$set": {"value": 8}},
    )


def test_createTask_inserts_with_current_id(app_module):
    app_module.db.settings.find_one.return_value = {"value": 0}

    form = MagicMock()
    form.title.data = "Test Gorevi"
    form.priority.data = "high"
    form.shortdesc.data = "kisa aciklama"

    response = app_module.createTask(form)

    app_module.db.tasks.insert_one.assert_called_once_with(
        {"id": 0, "title": "Test Gorevi", "shortdesc": "kisa aciklama", "priority": "high"}
    )
    assert response.status_code == 302  # redirect('/')


def test_deleteTask_by_id(app_module):
    form = MagicMock()
    form.key.data = "7"
    form.title.data = ""

    app_module.deleteTask(form)

    app_module.db.tasks.delete_many.assert_called_once_with({"id": 7})


def test_deleteTask_by_title_when_no_key(app_module):
    form = MagicMock()
    form.key.data = ""
    form.title.data = "Silinecek Gorev"

    app_module.deleteTask(form)

    app_module.db.tasks.delete_many.assert_called_once_with({"title": "Silinecek Gorev"})


def test_updateTask_sets_shortdesc(app_module):
    form = MagicMock()
    form.key.data = "3"
    form.shortdesc.data = "guncellendi"

    app_module.updateTask(form)

    app_module.db.tasks.update_one.assert_called_once_with(
        {"id": 3},
        {"$set": {"shortdesc": "guncellendi"}},
    )


def test_resetTask_drops_and_reinserts_settings(app_module):
    app_module.resetTask(MagicMock())

    app_module.db.tasks.drop.assert_called_once()
    app_module.db.settings.drop.assert_called_once()
    app_module.db.settings.insert_one.assert_called_once_with({"name": "task_id", "value": 0})


# ---------- Route testi (Flask test_client ile) ----------

def test_index_route_returns_200(client, app_module):
    app_module.db.tasks.find.return_value = []

    with patch.object(app_module, "render_template", return_value="ok"):
        response = client.get("/")

    assert response.status_code == 200