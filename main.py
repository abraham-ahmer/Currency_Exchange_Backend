from fastapi import FastAPI, Request, HTTPException
from database import engine, SessionLocal
from contextlib import asynccontextmanager
from database_models import Base
from auth_folder import signup, login
import currency
from fastapi.middleware.cors import CORSMiddleware

from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from datetime import datetime
from exception import CurrencyAPIError
from time import time
from sqlalchemy import text

from rate_limit import limiter
from slowapi.errors import RateLimitExceeded

Base.metadata.create_all(bind=engine)


# Lifespan FIRST
@asynccontextmanager
async def lifespan(app:FastAPI):
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
    except Exception as e:
        raise RuntimeError(f"Database connection failed {e}")
    yield
    engine.dispose()

# Create app ONCE with lifespan
app = FastAPI(title="Currency Exchange App", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)








#global data validation error.. if someone put "ten" instead of 10.
@app.exception_handler(RequestValidationError)
async def global_validation_error(req:Request, exc:RequestValidationError):
    # Convert errors to serializable format (remove non-serializable context)
    errors = []
    for error in exc.errors():
        error_dict = {
            "loc": error.get("loc"),
            "msg": error.get("msg"),
            "type": error.get("type")
        }
        errors.append(error_dict)
    
    return JSONResponse(
        status_code=422,
        content={
            "message": "Invalid request data. Please check your input.",
            "details": errors,
            "timestamp": datetime.utcnow().isoformat()
        },
    )

# global HTTPEXCEPTION handler
@app.exception_handler(HTTPException)
async def http_exception_handler(req:Request, exc:HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "details": exc.detail,
            "status_code":exc.status_code,
            "timestamp": datetime.utcnow().isoformat()
        },
    )

# global valueerror handler
@app.exception_handler(ValueError)
async def http_exception_handler(req:Request, exc:ValueError):
    return JSONResponse(
        status_code= 400,
        content={
            "message": str(exc),
            "status_code": 400,
            "timestamp": datetime.utcnow().isoformat()
        },
    )

# global error handling for bad currency
@app.exception_handler(CurrencyAPIError)
async def currency_error(req:Request, exc:CurrencyAPIError):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error_type": "CurrencyAPIError",
            "message":exc.message,
            "status_code": exc.status_code,
            "timestamp": datetime.utcnow().isoformat()
        },
    )


################### in the header section, there is now a new  x-process-time: 1.58s (time varies) 
# middleware
@app.middleware("http")
async def show_time(req:Request, call_next):
    start_time = time()
    try:
         response = await call_next(req)
    except Exception as e:
        raise e 
       
    process_time = time() - start_time

    # add a new header
    response.headers["x-time"] = f"{process_time:.3}s"

    return response


###############################  For limiting request per minute (rate limit)

#create limit by client id
app.state.limiter = limiter


#create global error handler for RateLimitExceeded
@app.exception_handler(RateLimitExceeded)
async def limit_handling(request:Request, exc:RateLimitExceeded):
    return JSONResponse(
        status_code= 429,
        content={"message":"Too many requests, slow down G!"}
    )

app.include_router(signup.router)
app.include_router(login.router)
app.include_router(currency.router)








