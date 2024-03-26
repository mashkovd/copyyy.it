from typing import Annotated

from fastapi import Body, Depends, FastAPI, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from db import crud, models, schemas
from db.database import SessionMaker, engine

app = FastAPI()

models.Base.metadata.create_all(bind=engine)


# Dependency
def get_db():
    db = SessionMaker()
    try:
        yield db
    finally:
        db.close()


@app.post("/traders/", response_model=schemas.Trader)
def create_trader(
    trader: Annotated[
        schemas.TraderCreate,
        Body(
            examples=[
                {
                    "email": "trader@mail.com",
                    "is_active": True,
                    "api_key": "trader_api_key",
                    "api_secret": "trader_api_secret",
                }
            ],
        ),
    ],
    db: Session = Depends(get_db),
):
    db_trader = crud.get_trader_by_email(db, email=trader.email)
    if db_trader:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_trader(db=db, trader=trader)


@app.get("/traders/", response_model=list[schemas.Trader])
def read_traders(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    traders = crud.get_traders(db, skip=skip, limit=limit)
    return traders


@app.get("/traders/{traider_id}", response_model=schemas.Trader)
def read_trader(trader_id: int, db: Session = Depends(get_db)):
    db_trader = crud.get_trader(db, trader_id=trader_id)
    if db_trader is None:
        raise HTTPException(status_code=404, detail="Trader not found")
    return db_trader


@app.delete("/traders/{traider_id}")
def delete_trader(trader_id: int, db: Session = Depends(get_db)):
    db_trader = crud.get_trader(db, trader_id=trader_id)
    if db_trader is None:
        raise HTTPException(status_code=404, detail="Trader not found")
    return crud.delete_trader(db=db, db_trader=db_trader)


@app.put("/traders/{trader_id}", response_model=schemas.Trader)
def update_trader(
    trader: Annotated[
        schemas.TraderCreate,
        Body(
            examples=[
                {
                    "email": "trader@tradermail.com",
                    "is_active": True,
                    "api_key": "trader_api_key",
                    "api_secret": "trader_api_secret",
                }
            ],
        ),
    ],
    db: Session = Depends(get_db),
):
    db_trader = crud.get_trader(db, trader_id=trader.id)
    if db_trader is None:
        raise HTTPException(status_code=404, detail="Trader not found")
    return crud.update_trader(db=db, trader=trader, db_trader=db_trader)


@app.post("/traders/{trader_id}/followers/", response_model=schemas.FollowerCreate)
def create_follower_for_trader(
    trader_id: int,
    follower: Annotated[
        schemas.FollowerCreate,
        Body(
            examples=[
                {
                    "email": "follower@mail.com",
                    "is_active": True,
                    "api_key": "follower_api_key",
                    "api_secret": "follower_api_secret",
                }
            ],
        ),
    ],
    db: Session = Depends(get_db),
):
    trader = crud.get_trader(db, trader_id=trader_id)
    if trader is None:
        raise HTTPException(status_code=404, detail="Trader not found")
    try:
        return crud.create_follower_for_trader(db=db, follower=follower, trader=trader)
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Follower already exists")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating follower - {e}")


@app.get("/followers/", response_model=list[schemas.Follower])
def read_followers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    followers = crud.get_followers(db, skip=skip, limit=limit)
    return followers
