from fastapi import FastAPI
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from services.limiter import limiter

from api.router import api_router
from fastapi.middleware.cors import CORSMiddleware
from config import get_settings



def create_app() -> FastAPI:
	app = FastAPI(title="NaturalSQL Backend", version="0.1.0")
	app.include_router(api_router)
	app.state.limiter = limiter
	app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

	settings = get_settings()
	app.add_middleware(
		CORSMiddleware,
		allow_origins=settings.cors_allowed_origins,
		allow_credentials=True,
		allow_methods=["GET", "POST", "OPTIONS"],
		allow_headers=["Content-Type", "Authorization"],
	)
	return app

# Create the FastAPI app instance

app = create_app()
