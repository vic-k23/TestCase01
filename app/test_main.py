from fastapi.testclient import TestClient
from json import dumps

from main import app

test_client = TestClient(app)
headers = {
    'accept': "application/json",
}
cookies = None


def test_create_upload_file():
    files = {'file': ('test.json',
                      dumps({'array': ['1', '2', '3', '4', 5]}),
                      'application/json',
                      )}
    response = test_client.post(
        "/uploadfile",
        headers=headers,
        files=files
    )

    assert response.status_code == 200
    assert response.json() == {
        "sum": 15
    }


def test_get_sum_error():
    response = test_client.get(
        "/sum",
        headers=headers
    )

    assert response.status_code == 403
    assert response.json() == {
        "detail": "No session provided"
    }


def test_create_session():
    global cookies
    files = {'file': ('test.json',
                      dumps({'array': ['1', '2', '3', '4', 5]}),
                      'application/json',
                      )}
    response = test_client.post(
        "/uploadfile-async",
        headers=headers,
        files=files
    )

    cookies = response.cookies

    assert response.status_code == 200
    assert response.text == '"created session for test.json"'


def test_get_sum_success():
    global cookies
    response = test_client.get(
        "/sum",
        headers=headers,
        cookies=cookies
    )

    assert response.status_code == 200
    assert response.json() == {
        "filename": "test.json",
        "file_sum": 15
    }
