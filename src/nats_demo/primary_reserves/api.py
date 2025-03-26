import json

import nats
import uvicorn
from fastapi import FastAPI, Request

api = FastAPI()


@api.get("/{path:path}")
async def root(path: str, request: Request) -> dict:
    natsclient = await nats.connect()
    request_body = await request.body()
    if request_body != b"":
        request_json = await request.json()
    else:
        request_json = {}
    request_dict = {
        "headers": dict(request.headers),
        "query_params": dict(request.query_params),
        "path_params": dict(request.path_params),
        "cookies": request.cookies,
        "body": request_json,
    }
    response = await natsclient.request(
        subject=path.replace("/", "."),
        payload=json.dumps(request_dict).encode(),
        timeout=5,
    )
    return {"data": json.loads(response.data.decode())}


def main() -> None:
    uvicorn.run(api)


if __name__ == "__main__":
    main()
