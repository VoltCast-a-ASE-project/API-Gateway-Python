import httpx

from fastapi import FastAPI, Request, Response
from app.Database import Database
from pydantic import BaseModel

from app.JwtService import JwtService
from app.PasswordService import PasswordService


class User(BaseModel):
    username: str
    password: str

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

EXCLUDED_ROUTES = ["/api/v1/auth/register", "/api/v1/auth/login"]

@app.on_event("startup")
def setup():
    db.setup_db()


@app.middleware("http")
async def check_jwt(request: Request, call_next):
    if request.url.path in EXCLUDED_ROUTES:
        return await call_next(request)

    bearer_token = request.headers.get("Authorization")
    token = bearer_token.split(" ")[1]

    if token is None:
        return Response("Bad request: Token missing", status_code=400)

    if not JwtService.verify_jwt(token):
        return Response("Unauthorized: Invalid Token", status_code=401)

    response = await call_next(request)
    return response

@app.post("/api/v1/auth/register")
async def register(request: Request):
    body =  await request.json()

    username = body["email"]
    password = body["password"]

    hashed_password = PasswordService.create_password_hash(password)
    user = User(username=username, hashed_password=hashed_password)

    if not db.write_user_data(user):
        return Response("Conflict: Email already in use", status_code=409)

    return Response("Created: User", status_code=201)



@app.post("/api/v1/auth/login")
async def login(request: Request):
    body =  await request.json()

    username = body["email"]
    password = body["password"]

    db_response = db.get_user_password(username)
    hashed_password = db_response[0][0]

    if not PasswordService.verify_password(password, hashed_password):
        return Response("Unauthorized: Wrong credentials", status_code=401)

    token = JwtService.create_jwt(username)

    return Response(f"JWT: {token}", status_code=201)



@app.post("/api/v1/add/microservice")
async def add_microservice(request: Request):
    body = await request.json()
    if not db.write_microservice_data(body):
        return Response("Internal Server Error: Microservice data could not be written to database", status_code=500)
    return Response("Wrote microservice data to database", status_code=200)



@app.api_route("/{vendor}/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def route(vendor: str, path: str, request: Request):
    target = ROUTES.get(vendor)
    if not target:
        return Response("Unknown target", status_code=404)

    url = f"{target}/{vendor}/{path}"

    headers = dict(request.headers)
    headers.pop("host", None)

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.request(
                method=request.method,
                url=url,
                params=request.query_params,
                content=await request.body(),
                headers=headers,
            )
    except Exception:
        return Response("Not found: Microservice not reachable", status_code=404)

    return Response(content=resp.content, status_code=resp.status_code, headers=dict(resp.headers))

