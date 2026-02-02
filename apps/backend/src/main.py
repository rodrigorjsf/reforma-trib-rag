import time
import logging
import threading
from collections import defaultdict
from datetime import datetime, timezone
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config import Settings, get_settings
from .models import (
    Citation,
    ErrorResponse,
    HealthResponse,
    QueryRequest,
    QueryResponse,
    RateLimitInfo,
    ResponseMode,
    Source,
    UserInfo,
    UserTier,
)
from .agents.scraping_worker import ScrapingWorker
from .agents.queue_manager import SQLiteQueueManager

logger = logging.getLogger(__name__)

app = FastAPI(
    title="ReformaTax API",
    description="Citation-grounded Q&A API for Brazilian Tax Reform (LC 214/2024)",
    version="0.1.0",
)

# CORS middleware - must be added before app starts
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Rate limiting state (in production, use Redis)
class RateLimiter:
    def __init__(self) -> None:
        self.requests: dict[str, list[float]] = defaultdict(list)
        self.daily_counts: dict[str, int] = defaultdict(int)
        self.daily_reset: dict[str, float] = {}

    def is_allowed(self, user_id: str, rpm_limit: int, daily_limit: int | None = None) -> bool:
        now = time.time()
        minute_ago = now - 60

        # Clean old requests
        self.requests[user_id] = [t for t in self.requests[user_id] if t > minute_ago]

        # Check RPM
        if len(self.requests[user_id]) >= rpm_limit:
            return False

        # Check daily limit
        if daily_limit is not None:
            today_start = datetime.now(timezone.utc).replace(
                hour=0, minute=0, second=0, microsecond=0
            ).timestamp()

            if self.daily_reset.get(user_id, 0) < today_start:
                self.daily_counts[user_id] = 0
                self.daily_reset[user_id] = today_start

            if self.daily_counts[user_id] >= daily_limit:
                return False

        self.requests[user_id].append(now)
        if daily_limit is not None:
            self.daily_counts[user_id] += 1

        return True

    def get_remaining_rpm(self, user_id: str, rpm_limit: int) -> int:
        now = time.time()
        minute_ago = now - 60
        recent = [t for t in self.requests.get(user_id, []) if t > minute_ago]
        return max(0, rpm_limit - len(recent))

    def get_reset_time(self, user_id: str) -> datetime:
        requests = self.requests.get(user_id, [])
        if not requests:
            return datetime.now(timezone.utc)
        oldest = min(requests)
        return datetime.fromtimestamp(oldest + 60, tz=timezone.utc)

    def get_daily_remaining(self, user_id: str, daily_limit: int) -> int:
        return max(0, daily_limit - self.daily_counts.get(user_id, 0))


rate_limiter = RateLimiter()

# Initialize queue manager
queue_manager = SQLiteQueueManager(settings.queue_db_path)


def start_background_worker():
    """Start scraping worker in background thread."""
    if not settings.scraping_worker_enabled:
        logger.info("Scraping worker disabled via config")
        return

    worker = ScrapingWorker(
        queue_manager=queue_manager,
        poll_interval=settings.scraping_worker_poll_interval,
        docs_path=settings.docs_path
    )

    thread = threading.Thread(target=worker.start, daemon=True)
    thread.start()
    logger.info("Scraping worker started in background thread")


@app.on_event("startup")
async def startup_event():
    """Initialize services on application startup."""
    start_background_worker()


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown."""
    queue_manager.close()


# Mock users (replace with Auth0 in production)
MOCK_USERS: dict[str, dict] = {
    "user1": {
        "id": "user1",
        "email": "test@example.com",
        "name": "Test User",
        "tier": UserTier.FREE,
    },
    "user2": {
        "id": "user2",
        "email": "pro@example.com",
        "name": "Pro User",
        "tier": UserTier.PRO,
    },
}


@app.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    return HealthResponse(
        status="ok",
        timestamp=datetime.now(timezone.utc),
        sources_updated=None,  # TODO: Track actual source update time
    )


@app.post(
    "/api/query",
    response_model=QueryResponse,
    responses={429: {"model": ErrorResponse}},
)
async def query(
    request: QueryRequest,
    settings: Annotated[Settings, Depends(get_settings)],
) -> QueryResponse:
    user_id = request.user_id or "anonymous"
    user = MOCK_USERS.get(user_id)
    tier = user["tier"] if user else UserTier.FREE

    # Determine rate limits based on tier
    if tier == UserTier.FREE:
        rpm_limit = settings.free_tier_rpm
        daily_limit = settings.free_tier_daily_limit
    else:
        rpm_limit = settings.paid_tier_rpm
        daily_limit = None

    # Check rate limit
    if not rate_limiter.is_allowed(user_id, rpm_limit, daily_limit):
        raise HTTPException(
            status_code=429,
            detail={
                "error": "Rate limit exceeded",
                "reset_time": rate_limiter.get_reset_time(user_id).isoformat(),
                "remaining_requests": rate_limiter.get_remaining_rpm(user_id, rpm_limit),
            },
        )

    # TODO: Replace with actual RAG pipeline
    # 1. Retrieve context chunks from ChromaDB
    # 2. Call generator LLM
    # 3. Validate response
    # 4. Return or fallback

    response = QueryResponse(
        id=f"resp_{int(time.time() * 1000)}",
        answer=f'Resposta para: "{request.question}" (Modo: {request.mode.value})',
        citations=[
            Citation(
                article="Art. 1º",
                section="caput",
                law="Lei Complementar 214/2024",
                text="Texto do artigo relevante...",
                url="https://www.planalto.gov.br/ccivil_03/leis/lcp/lcp214.htm",
            )
        ],
        mode=request.mode,
        sources=[
            Source(
                id="lc214",
                title="Lei Complementar 214/2024",
                type="law",
                url="https://www.planalto.gov.br/ccivil_03/leis/lcp/lcp214.htm",
                relevant_chunks=["Texto do chunk relevante..."],
            )
        ],
        tokens=150,
        timestamp=datetime.now(timezone.utc),
    )

    return response


@app.get(
    "/api/user/{user_id}",
    response_model=UserInfo,
    responses={404: {"model": ErrorResponse}},
)
async def get_user(
    user_id: str,
    settings: Annotated[Settings, Depends(get_settings)],
) -> UserInfo:
    user = MOCK_USERS.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    tier = user["tier"]
    rpm_limit = settings.free_tier_rpm if tier == UserTier.FREE else settings.paid_tier_rpm
    daily_limit = settings.free_tier_daily_limit if tier == UserTier.FREE else None

    return UserInfo(
        id=user["id"],
        email=user["email"],
        name=user["name"],
        tier=tier,
        rate_limit=RateLimitInfo(
            remaining=rate_limiter.get_remaining_rpm(user_id, rpm_limit),
            reset_time=rate_limiter.get_reset_time(user_id),
            daily_remaining=(
                rate_limiter.get_daily_remaining(user_id, daily_limit) if daily_limit else None
            ),
        ),
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    if isinstance(exc.detail, dict):
        return JSONResponse(status_code=exc.status_code, content=exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": str(exc.detail)},
    )
