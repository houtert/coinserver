import logging
from datetime import datetime

import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import util
from broker import Broker
from database import Coindb

logger = logging.getLogger()

stream_handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)s :: %(message)s')
stream_handler.setFormatter(formatter)
stream_handler.setLevel(logging.DEBUG)

file_handler = logging.FileHandler('coinserver.log')
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.DEBUG)

logger.addHandler(stream_handler)
logger.addHandler(file_handler)

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

db = Coindb()
broker = Broker()
# model = Model(db)

start_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

assets = broker.get_assets()


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "assets": assets, "start_date": start_time})


@app.get("/coin/{symbol}", response_class=HTMLResponse)
async def coin(request: Request, symbol: str, hours: int = 24):
    asset = broker.get_asset(symbol)
    candles = db.get_candles(symbol, hours)

    if candles is None:
        raise HTTPException(status_code=404, detail="Symbol not found")

    else:
        candles = candles.iloc[::-1]
        candles = candles.to_dict('records')

    return templates.TemplateResponse("coin.html",
                                      {"request": request, "symbol": symbol, "name": asset['name'], "candles": candles})


'''

                 REST API IMPLEMENTATION

'''


@app.get("/v1/coins")
async def coins():
    coins = db.get_coins()
    return coins


@app.get("/v1/price/{coin}")
async def price(coin: str, hours: int = 24):
    prices = db.get_prices(coin, hours)
    if prices is not None:
        result = prices.values.tolist()
    else:
        raise HTTPException(status_code=404, detail="Symbol not found")
    return result


@app.get("/v1/prices")
async def prices():
    price_list = {}
    coins = db.get_coins()
    for coin in coins:
        price = db.get_price(coin)
        price_list[coin] = price
    return price_list


@app.get("/v1/candle/{coin}")
async def candle(coin: str, hours: int = 24):
    candles = db.get_candles(coin, hours)
    if candles is not None:
        result = candles.values.tolist()
    else:
        raise HTTPException(status_code=404, detail="Symbol not found")
    return result


@app.get("/v1/livecandle/{coin}")
async def candle(coin: str):
    candles = broker.get_last_candles(coin)
    if len(candles) == 0:
        raise HTTPException(status_code=404, detail="Symbol not found")

    converted_candles = []
    for i in range(len(candles) - 1, -1, -1):
        data = candles[i]
        candlestick = {
            "time": data[0],
            "open": data[1],
            "high": data[2],
            "low": data[3],
            "close": data[4]
        }
        converted_candles.append(candlestick)

    return converted_candles


def main():
    assets = broker.get_assets()
    myIP = util.getIP()
    uvicorn.run(app, host=myIP, port=4000)


if __name__ == "__main__":
    main()
