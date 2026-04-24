# Exchange Rate API for current data and others
# exchangeratehost for historical rate

import requests
from fastapi import APIRouter, Depends, HTTPException, Request
from models import CurrencyConvert, CurrencyLive, CurrencyHistoric, CurrencyResponse
from database import get_db
from sqlalchemy.orm import Session
from oauth import create_access
from database_models import User, Currency
from exception import CurrencyAPIError
from sqlalchemy import text
from datetime import date

from rate_limit import limiter
import os 
from dotenv import load_dotenv

load_dotenv()


router = APIRouter(tags=["Currency Exchange Activity"], prefix="/currency")

# currency converter
@router.post("/currency_converter")
@limiter.limit("10/minute")
async def Convert_Currency(request: Request, content:CurrencyConvert):
    if content.amount <=0:
        raise ValueError("amount must be 1 or greater.")
    
    key = os.getenv("CURRENCY_API_KEY")
    url = f"https://v6.exchangerate-api.com/v6/{key}/pair/{content.base_currency}/{content.target_currency}/{content.amount}" # Exchange Rate API
    response = requests.get(url)

    if response.status_code != 200:
        raise CurrencyAPIError("Invalid currency code", status_code=400)
       
    else:
        data = response.json()
        return {
            "base": content.base_currency,
            "target": content.target_currency,
            "amount": content.amount,
            "live": data["conversion_result"]
}
    




    
# Live (1 v 1)
@router.post("/live_currency_exchange")
@limiter.limit("10/minute")
def check_live_currency(request: Request, currency:CurrencyLive):
    key = os.getenv("CURRENCY_API_KEY")
    url = f"https://v6.exchangerate-api.com/v6/{key}/latest/{currency.base_currency}"
    response = requests.get(url)

    if response.status_code != 200:
            raise CurrencyAPIError("Invalid Currency Code", status_code=400)
    else:
        data = response.json()["conversion_rates"][currency.target_currency]

        return {
                "base": f"1 {currency.base_currency}",
                "target": f"{data} {currency.target_currency}"
    }

    

# historical data 

@router.post("/historical_currency_data", response_model=CurrencyResponse)
@limiter.limit("2/minute")
def historical_data(request: Request, content:CurrencyHistoric, db:Session = Depends(get_db), uc:User = Depends(create_access)):
    key = os.getenv("CURRENCY_API_KEY_FOR_HISTORIC")
    
    url = f"https://api.exchangerate.host/convert?from={content.base_currency}&to={content.target_currency}&amount={content.amount}&date={content.historical_date}&access_key={key}" # exchangeratehost

    if (content.historical_date > date.today()):
        raise HTTPException(detail="Cannot get currency data of future dates", status_code=400)

    response = requests.get(url)

    if response.status_code != 200:
        raise HTTPException(detail="Invalid currency code or Requested Data does not exist", status_code=400)
    
    data = response.json()

    if "result" not in data or data["result"] is None:
        raise HTTPException(detail="Requested Data does not exist", status_code=400)
    
    converted_val = data["result"]
    
    historic_return = Currency(
            base_currency= content.base_currency,
            target_currency= content.target_currency,
            amount= content.amount,
            converted= converted_val,
            historical_date= content.historical_date,
            user_id= uc.id
    )

    db.add(historic_return)
    db.commit()
    db.refresh(historic_return)

    return historic_return


# delete user and its history
@router.delete("/delete")
def delete_data(db:Session = Depends(get_db), uc:User = Depends(create_access)):
    db_user = db.query(User).filter(User.id == uc.id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User does not exist")
    

    db.delete(db_user)
    db.commit()
    return {"message":"You and all of your saved data has been deleted"}





################################### DB HEALTH
@router.get("/health")
def check_health(db:Session = Depends(get_db)):
    try:
        db = db.execute(text("Select 1"))
        return {"status":"ok", "DB":"Connected"}
    except Exception as e:
        return {"status":"error", "DB":"Not Connected"} 







