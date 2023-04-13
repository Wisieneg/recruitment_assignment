import pytest
import json
import os
from io import BytesIO
from . import app, client


SOURCE = {
        "source":{
                "app_name": "pl.api.cms.test",
                "user_id": 1
            }
        }

def check_error(code, error_type, resp):
    assert resp.status_code == code
    assert "error" in resp.json
    assert all(x in resp.json["error"] for x in ["code", "message", "type"])
    assert resp.json["error"]["code"] == str(code)
    assert resp.json["error"]["type"] == error_type


def test_ping(client):
    resp = client.get("/ping")
    assert resp.status_code == 200


def test_gallery_list(client):
    payload = {
            **SOURCE,
            "paginate": {
                    "page": 1,
                    "per_page": 2,
                    "order": "id",
                    "order_desc": True
                }
            }
    resp = client.get(
            "/site/1/module/gallery",
            data=json.dumps(payload),
            content_type="application/json"
            )
    assert resp.status_code == 200
    assert "pagination" in resp.json
    assert "data" in resp.json
    assert len(resp.json["data"])<=2
    assert resp.json["data"][0]["id"]>resp.json["data"][-1]["id"]


def test_gallery_add(client):
    payload = {
            **SOURCE,
            "payload": {
                    "name": "new test gallery",
                    "description": "new test gallery description"
                }
            }
    resp = client.post(
            "/site/1/module/gallery",
            data=json.dumps(payload),
            content_type="application/json"
            )
    assert resp.status_code == 201
    assert "gallery_id" in resp.json
    assert resp.json["gallery_id"] != 0


def test_gallery_get_one(client):
    payload = {
            **SOURCE
            }
    resp = client.get(
            "/site/1/module/gallery/1",
            data=json.dumps(payload),
            content_type="application/json"
            )
    assert resp.status_code == 200
    assert "data" in resp.json
    assert all(x in resp.json["data"] for x in ["id", "name", "description"])


def test_gallery_photo_upload(client):
    payload = {
            **SOURCE
            }
    with open("./test.png", "rb") as file:
        file_bytes = BytesIO(file.read())
    resp = client.post(
            "/site/1/module/gallery/1",
            data={**payload, "description": "file description", "file":(file_bytes, 'test.png')},
            content_type="multipart/form-data"
            )
    print(resp.json)
    assert resp.status_code == 200
    assert "photo_id" in resp.json
    assert resp.json["photo_id"] > 0


def test_gallery_change(client):
    payload = {
            **SOURCE,
            "payload":{
                "name": "new test name",
                "description": "new test description"
                }
            }
    resp = client.put(
            "/site/1/module/gallery/1",
            data=json.dumps(payload),
            content_type="application/json"
            )
    assert resp.status_code == 204




def test_gallery_move_up(client):
    payload = {
            **SOURCE
            }
    resp = client.put(
            "/site/1/module/gallery/1/move_up",
            data=json.dumps(payload),
            content_type="application/json"
            )
    assert resp.status_code == 204


def test_gallery_move_down(client):
    payload = {
            **SOURCE
            }
    resp = client.put(
            "/site/1/module/gallery/1/move_down",
            data=json.dumps(payload),
            content_type="application/json"
            )
    assert resp.status_code == 204


def test_gallery_photos_update(client):
    payload = {
            **SOURCE,
            "photos":[
                    {
                        "id": 1,
                        "description": "new description"
                    },
                    {
                        "id": 2,
                        "description": "new description"
                    }
                ]
            }
    resp = client.put(
            "/site/1/module/gallery/1/photos/update",
            data=json.dumps(payload),
            content_type="application/json"
            )
    assert resp.status_code == 204


def test_gallery_photo_reupload(client):
    payload = {
            **SOURCE
            }
    with open("./test.png", "rb") as file:
        file_bytes = BytesIO(file.read())
    resp = client.put(
            "/site/1/module/gallery/1/photo/1",
            data={**payload, "description": "file description", "file":(file_bytes, 'test.png')},
            content_type="multipart/form-data"
            )
    assert resp.status_code == 204


def test_gallery_photo_update(client):
    payload = {
            **SOURCE,
            "payload":
                    {
                        "description": "new description"
                    }
            }
    resp = client.put(
            "/site/1/module/gallery/1/photo/1/update",
            data=json.dumps(payload),
            content_type="application/json"
            )
    assert resp.status_code == 204


def test_gallery_photo_move_up(client):
    payload = {
            **SOURCE
            }
    resp = client.put(
            "/site/1/module/gallery/1/photo/1/move_up",
            data=json.dumps(payload),
            content_type="application/json"
            )
    assert resp.status_code == 204


def test_gallery_photo_move_down(client):
    payload = {
            **SOURCE
            }
    resp = client.put(
            "/site/1/module/gallery/1/photo/1/move_down",
            data=json.dumps(payload),
            content_type="application/json"
            )
    assert resp.status_code == 204


def test_gallery_delete(client):
    payload = {
            **SOURCE
            }
    resp = client.delete(
            "/site/1/module/gallery/1",
            data=json.dumps(payload),
            content_type="application/json"
            )
    assert resp.status_code == 204


def test_subjects_get_list(client):
    payload = {
            **SOURCE
            }
    resp = client.get(
            "/site/1/module/subject",
            data=json.dumps(payload),
            content_type="application/json"
            )
    assert resp.status_code == 200
    assert all(x in resp.json[0] for x in ["id", "subject", "connections_count"])


def test_subjects_get_list(client):
    payload = {
            **SOURCE
            }
    resp = client.get(
            "/site/1/module/subject",
            data=json.dumps(payload),
            content_type="application/json"
            )
    assert resp.status_code == 200
    assert all(x in resp.json[0] for x in ["id", "subject", "connections_count"])


def test_subjects_add(client):
    payload = {
            **SOURCE,
            "payload": {
                "subject": "new subject"
                }
            }
    resp = client.post(
            "/site/1/module/subject",
            data=json.dumps(payload),
            content_type="application/json"
            )
    assert resp.status_code == 201


def test_subjects_get_one(client):
    payload = {
            **SOURCE
            }
    resp = client.get(
            "/site/1/module/subject/1",
            data=json.dumps(payload),
            content_type="application/json"
            )
    assert resp.status_code == 200
    assert all(x in resp.json for x in ["id", "subject", "connections_count"])
    assert resp.json["id"] == 1


def test_subjects_change(client):
    payload = {
            **SOURCE,
            "payload":{
                "subject": "new subject"
                }
            }
    resp = client.put(
            "/site/1/module/subject/1",
            data=json.dumps(payload),
            content_type="application/json"
            )
    assert resp.status_code == 204


def test_subjects_delete(client):
    payload = {
            **SOURCE,
            "payload":{
                "subject": "new subject"
                }
            }
    resp = client.put(
            "/site/1/module/subject/1",
            data=json.dumps(payload),
            content_type="application/json"
            )
    assert resp.status_code == 204


def test_subject_prefix_row_get_list(client):
    payload = {
            **SOURCE
            }
    resp = client.get(
            "/site/1/module/subject/mu",
            data=json.dumps(payload),
            content_type="application/json"
            )
    assert resp.status_code == 200
    assert len(resp.json) >= 1
    assert resp.json[0]["id"] == 1


def test_gallery_options(client):
    resp = client.options("/site/1/module/gallery")
    assert resp.status_code == 200
    assert "allow" in resp.headers
    assert all(x in resp.headers["allow"] for x in ["GET", "POST", "OPTIONS"])


