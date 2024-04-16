import json
import logging
from enum import Enum

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel

from db import crud
from db.database import SessionMaker


class OrderUpdate(BaseModel):
    e: str
    E: int
    s: str
    c: str
    S: str
    o: str
    f: str
    q: str
    p: str
    P: str
    F: str
    g: int
    C: str
    x: str
    X: str
    r: str
    i: int
    l: str
    z: str
    L: str
    n: str
    N: str | None
    T: int
    t: int
    I: int
    w: bool
    m: bool
    M: bool
    O: int
    Z: str
    Y: str
    Q: str
    W: int
    V: str


class Balance(BaseModel):
    a: str
    f: str
    l: str


class AccountUpdate(BaseModel):
    e: str
    E: int
    u: int
    B: list[Balance]


class MessageType(Enum):
    execution_report = "executionReport"
    outbound_account_position = "outboundAccountPosition"


class MessageFactory:
    @staticmethod
    def create_message(message) -> dict | None:
        # message_data = json.loads(message)
        message_type = message.get("e")
        if message_type == MessageType.execution_report.value:
            return jsonable_encoder(OrderUpdate(**message))
        elif message_type == MessageType.outbound_account_position.value:
            return jsonable_encoder(AccountUpdate(**message))
        else:
            logging.warning(f"Unsupported message type: {message_type}")


class MessageHandler:
    def __init__(self):
        self.handlers = {}

    def register_handler(self, message_type, handler):
        self.handlers[message_type] = handler

    def handle_message(self, trader, message):
        message = json.loads(message)
        message_type = message.get("e")
        if message_type in self.handlers:
            handler = self.handlers[message_type]
            handler(trader, message)
        else:
            logging.warning(f"No handler registered for message: {message}")


def handle_execution_report(trader, message):
    from worker.app import handle_event

    with SessionMaker() as db:
        db_trader = crud.get_trader(db=db, trader_id=trader["id"])
        for follower in crud.get_followers_by_traders(db=db, db_trader=db_trader):
            if MessageFactory().create_message(message) is not None:
                handle_event.delay(
                    follower.dict(), MessageFactory().create_message(message)
                )


def handle_outbound_account_position(trader, message):
    logging.info(f"Update balance for {trader['email']} according to message {message}")


handler = MessageHandler()
handler.register_handler(MessageType.execution_report.value, handle_execution_report)
handler.register_handler(
    MessageType.outbound_account_position.value, handle_outbound_account_position
)
