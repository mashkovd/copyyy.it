import logging
import time

from binance.spot import Spot as Client
from binance.websocket.spot.websocket_api import SpotWebsocketAPIClient
from binance.websocket.spot.websocket_stream import SpotWebsocketStreamClient
from celery import Celery

import db.schemas
from db import crud, models
from db.database import SessionMaker
from lib.utils import app_logging
from settings import settings
from worker.core import OrderUpdate, handler

app = Celery(__name__, broker=settings.REDIS_URL, backend=settings.REDIS_URL)
app_logging(logging, logging.DEBUG)

app.conf.beat_schedule = {
    "execute-every-seconds": {
        "task": f"{__name__}.create_ws_for_traders",
        "schedule": settings.TIME_FOR_RECREATE_WS,
    },
}


def create_message_handler(trader: db.schemas.TraderDict):
    def message_handler(_, message):
        try:
            handler.handle_message(trader, message)
        except Exception as e:
            logging.error(f"Error handling message: {e} - {message}")

    return message_handler


def create_close_handler(trader: db.schemas.TraderDict):
    def message_handler(_):
        with SessionMaker() as db:
            crud.set_ws_status_for_trader(db=db, trader_id=trader["id"], status=False)
            logging.info(f"Websocket for {trader['email']} closed")

    return message_handler


@app.task
def get_open_orders(trader: db.schemas.TraderDict):
    logging.info(f"Getting open traders for {trader['email']} started")
    message_handler = create_message_handler(trader)
    client = SpotWebsocketAPIClient(
        api_key=trader["api_key"],
        api_secret=trader["api_secret"],
        on_message=message_handler,
    )
    client.get_open_orders()
    logging.info(f"Getting open traders for {trader['email']} finished")


@app.task
def start_user_data_stream(trader: db.schemas.TraderDict, response: dict):
    logging.info("Creating websocket for trader started")
    message_handler = create_message_handler(trader)
    close_handler = create_close_handler(trader)
    ws = SpotWebsocketStreamClient(
        on_message=message_handler,
        on_close=close_handler,
    )
    ws.user_data(listen_key=response["listenKey"])

    with SessionMaker() as db:
        crud.set_ws_status_for_trader(db=db, trader_id=trader["id"], status=True)
        logging.info(f"set ws status for {trader['email']} to True")

    time.sleep(settings.TIME_FOR_RECREATE_WS * 5)
    ws.user_data(
        response["listenKey"], action=SpotWebsocketStreamClient.ACTION_UNSUBSCRIBE
    )
    ws.stop()


def create_ws_for_trader(trader: models.Trader):
    client = Client(api_key=trader.api_key, api_secret=trader.api_secret)
    response = client.new_listen_key()
    logging.info("Receving listen key : {}".format(response["listenKey"]))

    start_user_data_stream.delay(trader.dict(), response)


@app.task
def create_ws_for_traders():
    logging.info("Creating websocket for traders started")
    l_traders = []
    with SessionMaker() as db:
        for trader in crud.get_traders_for_ws(db=db):
            l_traders.append(trader.id)
            create_ws_for_trader(trader)
    logging.info(f"Creating websocket for {len(l_traders)} traders finished")
    return l_traders


def create_order_message_handler(_, message):
    logging.info(f"create_order - message: {message}")
    return message


def create_order_error_handler(message):
    logging.info(f"WARNING create_order - message: {message}")


@app.task
def handle_event(follower: db.schemas.FollowerDict, message: dict):

    client = SpotWebsocketAPIClient(
        api_key=follower["api_key"],
        api_secret=follower["api_secret"],
        on_message=create_order_message_handler,
        on_error=create_order_error_handler,
    )
    message = OrderUpdate(**message)

    if message.X == "NEW":
        logging.info(f"create order for {follower['email']} started")
        new_order = client.new_order(
            symbol=message.s,
            side=message.S,
            type=message.o,
            timeInForce=message.f,
            quantity=message.q,
            price=message.p,
            newOrderRespType="RESULT",
        )
        logging.warning(f"create order {new_order} for {follower['email']} finished")


with SessionMaker() as db:
    for trader in crud.get_traders(db=db):
        trader.ws_active = False
    db.commit()
