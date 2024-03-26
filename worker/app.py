import json
import logging

from binance.lib.utils import config_logging
from binance.websocket.spot.websocket_api import SpotWebsocketAPIClient
from celery import Celery

import db.schemas
from db import crud
from db.database import SessionMaker
from settings import settings

app = Celery(__name__, broker=settings.REDIS_URL, backend=settings.REDIS_URL)
config_logging(logging, logging.DEBUG)

app.conf.beat_schedule = {
    "execute-every-seconds": {
        "task": f"{__name__}.get_active_traders",
        "schedule": settings.TIME_FOR_UPDATE_ORDER,
    },
}


def create_message_handler(trader: db.schemas.TraderDict):
    def message_handler(_, message):
        try:
            result = json.loads(message)["result"]
        except KeyError:
            logging.error(f"Error in message: {message}")
            return
        with SessionMaker() as db:
            db_trader = crud.get_trader_by_email(db=db, email=trader["email"])
            for follower in crud.get_followers_by_traders(db=db, db_trader=db_trader):
                logging.info(
                    f"Create order for {follower.email} according to trader's order {[order['orderId'] for order in result]}"
                )

    return message_handler


@app.task
def get_open_orders(trader: db.schemas.TraderDict):
    logging.info(f"Getting open traders for {trader['email']} started")
    message_handler = create_message_handler(trader)
    client = SpotWebsocketAPIClient(
        api_key=trader["api_key"],
        # api_key=settings.API_KEY,
        api_secret=trader["api_secret"],
        # api_secret=settings.API_SECRET,
        on_message=message_handler,
    )
    client.get_open_orders()
    logging.info(f"Getting open traders for {trader['email']} finished")


@app.task
def get_active_traders():
    logging.info("Getting active traders started")
    with SessionMaker() as db:
        for trader in crud.get_traders(db=db):
            get_open_orders.delay(trader.dict())
    logging.info("Getting active traders finished")
