import httpx

from fastapi import FastAPI, Request, Response
from app.Database import Database
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from app.JwtService import JwtService
from app.PasswordService import PasswordService


class User(BaseModel):
    username: str
    hashed_password: str

app = FastAPI()
db = Database()

ROUTES = {
    "fronius": "http://fronius-ms:8081",
    "kostal": "http://kostal-ms:8082",
    "shelly": "http://shelly-ms:8083",
    "forecasting": "http://forecasting-ms:8084",
    "newsfeed": "http://newsfeed-ms:8085",
    "weatherservice": "http://weatherservice-ms:8086",
    "alert": "http://alert-ms:8087"
}
origins = [
    "http://localhost:4200",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

EXCLUDED_ROUTES = ["/api/v1/auth/register", "/api/v1/auth/login"]

@app.on_event("startup")
def setup():
    db.setup_db()


@app.middleware("http")
async def check_jwt(request: Request, call_next):

    if request.method == "OPTIONS":
        return await call_next(request)

    if request.url.path in EXCLUDED_ROUTES:
        return await call_next(request)

    bearer_token = request.headers.get("Authorization")
    if not bearer_token:
        return Response("Bad request: Token missing", status_code=400)

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

    token = JwtService.create_jwt(username)

    return {
        "data": {
            "token": token,
            "token_type": "bearer"},
        "message": "Success"
    }



@app.post("/api/v1/auth/login")
async def login(request: Request):
    body =  await request.json()

    username = body["email"]
    password = body["password"]

    db_response = db.get_user_password(username)
    if not db_response or not db_response[0] or not db_response[0][0]:
        return Response("Unauthorized: Wrong credentials", status_code=401)

    hashed_password = db_response[0][0]

    if not PasswordService.verify_password(password, hashed_password):
        return Response("Unauthorized: Wrong credentials", status_code=401)

    token = JwtService.create_jwt(username)

    return {
        "data":{
            "token": token,
            "token_type": "bearer"},
        "message": "Success"
        }



@app.api_route("/api/v1/{vendor}/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
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

