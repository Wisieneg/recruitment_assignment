import json
from . import app, client


SOURCE = {
        "source": {
                "app_name": "pl.api.cms.test",
                "user_id": 1
            }
        }


NON_USER_SOURCE = {
        "source": {
                "app_name": "pl.api.cms.test",
                "user_id": 5
            }
        }


def check_error(code, error_type, resp):
    assert resp.status_code == code
    assert "error" in resp.json
    assert all(x in resp.json["error"] for x in ["code", "message", "type"])
    assert resp.json["error"]["code"] == str(code)
    assert resp.json["error"]["type"] == error_type


def test_404(client):
    payload = {
            **NON_USER_SOURCE
            }
    resp = client.get(
            "/site/1/module/gallery",
            data=json.dumps(payload),
            content_type="application/json"
            )
    check_error(404, "Not found", resp)


def test_403(client):
    payload = {
            **SOURCE
            }
    resp = client.get(
            "/site/3/module/gallery",
            data=json.dumps(payload),
            content_type="application/json"
            )
    check_error(403, "Forbidden", resp)


def test_400(client):
    payload = {}
    resp = client.get(
            "/site/111111111/module/gallery",
            data=json.dumps(payload),
            content_type="application/json"
            )
    check_error(400, "Bad Request", resp)
