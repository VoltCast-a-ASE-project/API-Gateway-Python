import httpx

from fastapi import FastAPI, Request, Response
from app.Database import Database

app = FastAPI()

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
    db = Database()
    db.setup_db()

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

