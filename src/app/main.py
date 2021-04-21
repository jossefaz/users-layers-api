import os
import time
import uuid

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Request

from .api import monitor, customlayers
from .db.db_engine import engine, database
from .db.db_models import metadata
from .utils.http import HTTPFactory
from .utils.logs import RestLogger, log_http_request, log_http_response
from .utils.env import REQUEST_ID_KEY, REQUEST_TIME_KEY, ACCESS_TOKEN_KEY

RestLogger.init_logger()
metadata.create_all(engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=[ACCESS_TOKEN_KEY]
)


@app.middleware("http")
async def add_request_id_process_time_header(request: Request, call_next):
    request_id = HTTPFactory.set_request_id(request)
    request.state.user, new_token = await HTTPFactory.instance.check_user_credentials(request)
    start_time = time.time()
    log_http_request(request.url, request.method, request.headers,
                     request.path_params)
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000
    formatted_process_time = '{0:.2f}'.format(process_time)
    response.headers[REQUEST_TIME_KEY] = str(process_time)
    response.headers[REQUEST_ID_KEY] = request_id
    if new_token:
        response.headers[ACCESS_TOKEN_KEY] = new_token
    log_http_response(formatted_process_time, response.status_code, response.headers)
    return response


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


app.include_router(monitor.router, prefix="/monitor", tags=["monitoring"])
app.include_router(customlayers.router, prefix="/layers", tags=["layers"])
