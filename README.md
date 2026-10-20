# Flask JWT Students & Reports API

A REST API built with Flask that manages two resources, **students** and **reports**, and protects the student routes with **JWT authentication** (access and refresh tokens).

## Features

- Full CRUD (GET, POST, PUT, DELETE) for students and reports
- JWT authentication with Flask-JWT-Extended
  - Access token valid for 5 minutes
  - Refresh token valid for 7 days
- Input validation with clear JSON error messages and proper HTTP status codes
- Custom handlers for 401, 404, 405 and 500 errors
- Automated test script (32 checks)

## Tech stack

- Python 3
- Flask
- Flask-JWT-Extended

## Getting started

### 1. Clone the repository

```
git clone https://github.com/YOUR-USERNAME/YOUR-REPO-NAME.git
cd YOUR-REPO-NAME
```

### 2. Create a virtual environment and install dependencies

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

(On macOS/Linux, activate with `source .venv/bin/activate`.)

### 3. Run the server

```
python app.py
```

The API runs at `http://127.0.0.1:5000`.

## Authentication

Student routes require a token. Reports are public.

1. Log in with `POST /login` and the demo credentials:
   ```json
   {"username": "admin", "password": "admin123"}
   ```
2. The response contains an `access_token` and a `refresh_token`.
3. Send the access token on protected requests:
   ```
   Authorization: Bearer <access_token>
   ```
4. When the access token expires (after 5 minutes), call `POST /refresh` with the **refresh token** in the same header format to get a new access token.

> The credentials are for demonstration only. A real application would use a database and hashed passwords.

## Endpoints

| Method | Route | Token required | Description |
|--------|-------|----------------|-------------|
| GET | `/` | No | API status and endpoint list |
| POST | `/login` | No | Get access and refresh tokens |
| POST | `/refresh` | Refresh token | Get a new access token |
| GET | `/students` | Yes | List all students |
| GET | `/students/{id}` | Yes | Get one student |
| POST | `/students` | Yes | Create a student |
| PUT | `/students/{id}` | Yes | Update a student |
| DELETE | `/students/{id}` | Yes | Delete a student |
| GET | `/reports` | No | List all reports |
| GET | `/reports/{id}` | No | Get one report |
| POST | `/reports` | No | Create a report |
| PUT | `/reports/{id}` | No | Update a report |
| DELETE | `/reports/{id}` | No | Delete a report |

## Data models

**Student**

```json
{"ID_S": 3, "FN": "Omar", "LN": "Jlassi", "DMjr": 1, "Level": 2}
```

- `ID_S`: unique positive integer
- `FN`, `LN`: non-empty strings
- `DMjr`: 0 or 1
- `Level`: 1, 2, 3 or 4

**Report**

```json
{
  "ID_R": 3,
  "Title": "Data Mining",
  "Type": "Academic",
  "K1": "X",
  "K2": "Y",
  "K3": "Z",
  "Release_Date": "2026-11-01"
}
```

- `ID_R`: unique positive integer
- `Title`, `Type`, `K1`, `K2`, `K3`: non-empty strings
- `Release_Date`: format `YYYY-MM-DD`

## HTTP status codes used

| Code | Meaning |
|------|---------|
| 200 | OK |
| 201 | Created |
| 400 | Invalid or missing data |
| 401 | Missing, invalid or expired token |
| 404 | Resource or endpoint not found |
| 405 | Method not allowed |
| 409 | ID already exists |

## Testing

**Automated tests** (the server does not need to be running):

```
python test_api.py
```

**Manual tests:** use Postman (desktop app) or Thunder Client. Log in first, then add the access token as a Bearer token on the student routes.

## Project structure

```
.
├── app.py              # The API
├── test_api.py         # Automated tests
├── requirements.txt    # Dependencies
├── .gitignore
└── README.md
```

## Notes

- Data is stored in Python lists in memory, so it resets every time the server restarts.
- Set the `JWT_SECRET_KEY` environment variable for any real deployment. The default key in the code is for local demos only.
