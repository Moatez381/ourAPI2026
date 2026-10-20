"""Run with:  python test_api.py
Uses Flask's built-in test client, so the server does NOT need to be running.
"""
from app import app

client = app.test_client()
passed = failed = 0


def check(name, response, expected_status):
    global passed, failed
    ok = response.status_code == expected_status
    passed += ok
    failed += not ok
    print(f"[{'PASS' if ok else 'FAIL'}] {name} -> {response.status_code} "
          f"(expected {expected_status})")


def auth(token):
    return {"Authorization": f"Bearer {token}"}


# ---- Home & auth ----
check("GET /", client.get("/"), 200)
check("GET /nope", client.get("/nope"), 404)
check("Login bad credentials",
      client.post("/login", json={"username": "x", "password": "y"}), 401)
check("Login without JSON body", client.post("/login"), 400)

r = client.post("/login", json={"username": "admin", "password": "admin123"})
check("Login OK", r, 200)
access = r.get_json()["access_token"]
refresh = r.get_json()["refresh_token"]

# ---- Token rules ----
check("GET /students no token", client.get("/students"), 401)
check("GET /students garbage token",
      client.get("/students", headers=auth("garbage")), 401)
check("GET /students with refresh token (not allowed)",
      client.get("/students", headers=auth(refresh)), 401)
check("POST /refresh with refresh token",
      client.post("/refresh", headers=auth(refresh)), 200)
check("POST /refresh with access token (not allowed)",
      client.post("/refresh", headers=auth(access)), 401)

# ---- Students ----
check("GET /students", client.get("/students", headers=auth(access)), 200)
check("GET /students/1", client.get("/students/1", headers=auth(access)), 200)
check("GET /students/99",
      client.get("/students/99", headers=auth(access)), 404)

new_student = {"ID_S": 3, "FN": "Omar", "LN": "Jlassi", "DMjr": 1, "Level": 2}
check("POST /students no token", client.post("/students", json=new_student), 401)
check("POST /students OK",
      client.post("/students", json=new_student, headers=auth(access)), 201)
check("POST /students duplicate ID",
      client.post("/students", json=new_student, headers=auth(access)), 409)
check("POST /students missing fields",
      client.post("/students", json={"ID_S": 9}, headers=auth(access)), 400)
check("POST /students bad DMjr",
      client.post("/students", json={**new_student, "ID_S": 4, "DMjr": 5},
                  headers=auth(access)), 400)
check("POST /students bad Level",
      client.post("/students", json={**new_student, "ID_S": 4, "Level": 9},
                  headers=auth(access)), 400)
check("PUT /students/3",
      client.put("/students/3", json={"Level": 4}, headers=auth(access)), 200)
check("PUT /students/3 bad Level",
      client.put("/students/3", json={"Level": 0}, headers=auth(access)), 400)
check("DELETE /students/3",
      client.delete("/students/3", headers=auth(access)), 200)
check("DELETE /students/3 again",
      client.delete("/students/3", headers=auth(access)), 404)

# ---- Reports (public) ----
check("GET /reports", client.get("/reports"), 200)
check("GET /reports/1", client.get("/reports/1"), 200)
check("GET /reports/99", client.get("/reports/99"), 404)

new_report = {"ID_R": 3, "Title": "Data Mining", "Type": "Academic",
              "K1": "X", "K2": "Y", "K3": "Z", "Release_Date": "2026-11-01"}
check("POST /reports OK", client.post("/reports", json=new_report), 201)
check("POST /reports duplicate", client.post("/reports", json=new_report), 409)
check("POST /reports bad date",
      client.post("/reports", json={**new_report, "ID_R": 4,
                                    "Release_Date": "01/11/2026"}), 400)
check("PUT /reports/3",
      client.put("/reports/3", json={"Title": "Data Mining II"}), 200)
check("DELETE /reports/3", client.delete("/reports/3"), 200)
check("DELETE /reports/3 again", client.delete("/reports/3"), 404)

print(f"\n{passed} passed, {failed} failed")