import json
from sys import orig_argv

import httpx

from fastapi import FastAPI, Request, Response
from app.Database import Database
from pydantic import BaseModel

from app.JwtService import JwtService
from app.PasswordService import PasswordService


class User(BaseModel):
    username: str
    password: str


class UserInDB(User):
    hashed_password: str
app = FastAPI()
db = Database()

ROUTES = {
    "fronius": "http://localhost:8081",
    "kostal": "http://localhost:8082",
    "shelly": "http://localhost:8083",
    "forecasting": "http://localhost:8084",
    "newsfeed": "http://localhost:8085",
    "weatherservice": "http://localhost:8086",
    "alert": "http://localhost:8087"
}

@app.on_event("startup")
def setup():
    db.setup_db()

@app.post("/api/v1/auth/register")
async def register(payload: Request, response: Response):
    body =  await payload.json()

    username = body["username"]
    password = body["password"]

    hashed_password = PasswordService.create_password_hash(password)
    user = User(username=username, hashed_password=hashed_password)

    if not db.write_user_data(user):
        return Response("Conflict: Email already in use", status_code=409)

    return Response("Created: User", status_code=201)

@app.post("/api/v1/auth/login")
async def login(payload: Request, response: Response):
    body =  await payload.json()

    username = body["username"]
    password = body["password"]

    user = User(username=username, password=password)

    db_response = db.get_user_password(username)
    value = ' '.join(db_response[0])
    print(value)

    test_e = {
        "hashed_password": value
    }
    return UserInDB(**test_e)
    # hashed_password = db_response[0].split('p=')[1]
    #
    #
    # print(password)
    # print(hashed_password)
    #
    #
    #
    # if not PasswordService.verify_password(password, hashed_password):
    #     return Response("Unauthorized: Wrong password", status_code=401)
    #
    # jwt = JwtService.create_jwt(username)
    #
    # return Response(f"JWT: {jwt}", status_code=201)




@app.api_route("/{vendor}/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def route(vendor: str, path: str, request: Request):
    target = ROUTES.get(vendor)
    if not target:
        return Response("Unknown target", status_code=404)

    url = f"{target}/{vendor}/{path}"

    headers = dict(request.headers)
    headers.pop("host", None)

    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.request(
            method=request.method,
            url=url,
            params=request.query_params,
            content=await request.body(),
            headers=headers,
        )

    return Response(content=resp.content, status_code=resp.status_code, headers=dict(resp.headers))

