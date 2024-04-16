from sqlalchemy.orm import Session

from . import models, schemas


def get_trader(db: Session, trader_id: int):
    return db.query(models.Trader).filter(models.Trader.id == trader_id).first()


def get_trader_by_email(db: Session, email: str):
    return db.query(models.Trader).filter(models.Trader.email == email).first()


def create_follower_for_trader(
    db: Session, follower: schemas.FollowerCreate, trader: models.Trader
):
    follower = models.Follower(**follower.dict(), trader_id=trader.id)
    db.add(follower)
    db.commit()
    db.refresh(follower)
    return follower


def create_trader(db: Session, trader: schemas.TraderCreate):
    trader = models.Trader(
        api_key=trader.api_key, api_secret=trader.api_secret, email=trader.email
    )
    db.add(trader)
    db.commit()
    db.refresh(trader)
    return trader


def get_traders(db: Session, skip: int = 0, limit: int = 100) -> list[models.Trader]:
    return db.query(models.Trader).offset(skip).limit(limit).all()


def get_traders_for_ws(
    db: Session, skip: int = 0, limit: int = 100
) -> list[models.Trader]:
    return (
        db.query(models.Trader)
        .filter(models.Trader.ws_active == False, models.Trader.is_active == True)
        .offset(skip)
        .limit(limit)
        .all()
    )


def set_ws_status_for_trader(db: Session, trader_id: int, status: bool = True):
    db_trader = get_trader(db, trader_id=trader_id)
    db_trader.ws_active = status
    db.commit()
    return db_trader


def get_followers(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Follower).offset(skip).limit(limit).all()


def get_followers_by_traders(
    db: Session, db_trader: models.Trader
) -> list[models.Follower]:
    return (
        db.query(models.Follower)
        .filter(models.Follower.trader_id == db_trader.id)
        .all()
    )


def delete_trader(db: Session, db_trader: models.Trader):
    db.delete(db_trader)
    db.commit()
    return {"ok": True}


def update_trader(db: Session, trader: schemas.TraderCreate, db_trader: models.Trader):
    db_trader.is_active = trader.is_active
    db_trader.api_key = trader.api_key
    db_trader.api_secret = trader.api_secret
    db.commit()
    db.refresh(db_trader)
    return db_trader
