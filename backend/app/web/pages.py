from pathlib import Path

from fastapi import APIRouter, File, Form, Query, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from backend.app.models.mutual_fund import MutualFundRecommendationRequest
from backend.app.models.portfolio import PortfolioHoldingInput
from backend.app.models.watchlist import AlertCreateRequest, WatchlistAddRequest
from backend.app.services.chat_service import ChatService
from backend.app.services.fundamental_service import FundamentalService
from backend.app.services.market_valuation_service import MarketValuationService
from backend.app.services.mutual_fund_service import MutualFundService
from backend.app.services.news_service import NewsService
from backend.app.portfolio_analysis.analyzer import analyze_broker_file
from backend.app.services.portfolio_service import PortfolioService
from backend.app.services.sector_service import SectorService
from backend.app.services.stock_service import StockDataError, StockService
from backend.app.services.technical_service import TechnicalService
from backend.app.services.watchlist_service import WatchlistService
from backend.app.web.helpers import bar_chart_html, candlestick_chart_html, format_inr, format_large_inr, sentiment_class

WEB_ROOT = Path(__file__).resolve().parents[3] / "web"
templates = Jinja2Templates(directory=str(WEB_ROOT / "templates"))
templates.env.filters["inr"] = format_inr
templates.env.filters["large_inr"] = format_large_inr
templates.env.filters["sentiment_class"] = sentiment_class

router = APIRouter(include_in_schema=False)

NAV_ITEMS = [
    {"href": "/dashboard", "icon": "🏠", "label": "Dashboard", "key": "dashboard"},
    {"href": "/stocks", "icon": "📊", "label": "Stocks", "key": "stocks"},
    {"href": "/technical", "icon": "📉", "label": "Technical", "key": "technical"},
    {"href": "/fundamental", "icon": "📋", "label": "Fundamentals", "key": "fundamental"},
    {"href": "/news", "icon": "📰", "label": "News", "key": "news"},
    {"href": "/market", "icon": "🌡️", "label": "Market", "key": "market"},
    {"href": "/mutual-funds", "icon": "💰", "label": "Mutual Funds", "key": "mutual-funds"},
    {"href": "/chat", "icon": "🤖", "label": "AI Chat", "key": "chat"},
    {"href": "/sectors", "icon": "🏭", "label": "Sectors", "key": "sectors"},
    {"href": "/portfolio", "icon": "💼", "label": "Portfolio", "key": "portfolio"},
    {"href": "/watchlist", "icon": "👁️", "label": "Watchlist", "key": "watchlist"},
]


def _base_context(request: Request, page_key: str, title: str, **extra):
    default_symbol = extra.get("default_symbol") or extra.get("symbol") or "RELIANCE"
    return {
        "request": request,
        "page_key": page_key,
        "title": title,
        "nav_items": NAV_ITEMS,
        "default_symbol": default_symbol,
        **extra,
    }


@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, symbol: str = Query(default="RELIANCE")) -> HTMLResponse:
    market = None
    stock = None
    errors: list[str] = []

    try:
        market = MarketValuationService().analyze()
    except Exception as exc:
        errors.append(str(exc))

    try:
        stock = StockService().get_stock_summary(symbol)
    except Exception as exc:
        errors.append(f"Stock preview: {exc}")

    return templates.TemplateResponse(
        "dashboard.html",
        _base_context(request, "dashboard", "Dashboard", default_symbol=symbol, symbol=symbol, market=market, stock=stock, errors=errors),
    )


@router.get("/stocks", response_class=HTMLResponse)
def stocks_page(
    request: Request,
    symbol: str = Query(default="RELIANCE"),
    period: str = Query(default="6mo"),
) -> HTMLResponse:
    summary = None
    chart_html = None
    error = None

    try:
        service = StockService()
        summary = service.get_stock_summary(symbol)
        history = service.get_stock_history(symbol, period=period, interval="1d")
        chart_html = candlestick_chart_html(history, summary.company_name)
    except StockDataError as exc:
        error = str(exc)
    except Exception as exc:
        error = str(exc)

    return templates.TemplateResponse(
        "stocks.html",
        _base_context(
            request,
            "stocks",
            "Stock Research",
            default_symbol=symbol,
            symbol=symbol,
            period=period,
            summary=summary,
            chart_html=chart_html,
            error=error,
        ),
    )


@router.get("/technical", response_class=HTMLResponse)
def technical_page(
    request: Request,
    symbol: str = Query(default="RELIANCE"),
    period: str = Query(default="6mo"),
) -> HTMLResponse:
    data = None
    error = None
    try:
        data = TechnicalService().analyze(symbol=symbol, period=period)
    except Exception as exc:
        error = str(exc)

    return templates.TemplateResponse(
        "technical.html",
        _base_context(request, "technical", "Technical Analysis", symbol=symbol, period=period, data=data, error=error),
    )


@router.get("/fundamental", response_class=HTMLResponse)
def fundamental_page(request: Request, symbol: str = Query(default="RELIANCE")) -> HTMLResponse:
    data = None
    error = None
    try:
        data = FundamentalService().analyze(symbol)
    except Exception as exc:
        error = str(exc)

    return templates.TemplateResponse(
        "fundamental.html",
        _base_context(request, "fundamental", "Fundamentals", symbol=symbol, data=data, error=error),
    )


@router.get("/news", response_class=HTMLResponse)
def news_page(request: Request, symbol: str = Query(default="RELIANCE")) -> HTMLResponse:
    data = NewsService().analyze(symbol)
    return templates.TemplateResponse(
        "news.html",
        _base_context(request, "news", "News Sentiment", symbol=symbol, data=data),
    )


@router.get("/market", response_class=HTMLResponse)
def market_page(request: Request) -> HTMLResponse:
    data = MarketValuationService().analyze()
    return templates.TemplateResponse(
        "market.html",
        _base_context(request, "market", "Market Valuation", data=data),
    )


@router.get("/mutual-funds", response_class=HTMLResponse)
def mutual_funds_page(
    request: Request,
    goal: str = Query(default="wealth_creation"),
    risk: str = Query(default="moderate"),
    horizon: int = Query(default=7),
    sip: float = Query(default=5000.0),
    submitted: bool = Query(default=False),
) -> HTMLResponse:
    data = None
    if submitted:
        data = MutualFundService().recommend(
            MutualFundRecommendationRequest(
                goal=goal,
                risk_appetite=risk,
                investment_horizon_years=horizon,
                monthly_sip=sip,
            )
        )

    return templates.TemplateResponse(
        "mutual_funds.html",
        _base_context(
            request,
            "mutual-funds",
            "Mutual Funds",
            goal=goal,
            risk=risk,
            horizon=horizon,
            sip=sip,
            data=data,
            submitted=submitted,
        ),
    )


@router.get("/chat", response_class=HTMLResponse)
def chat_page(
    request: Request,
    symbol: str = Query(default="RELIANCE"),
    answer: str | None = Query(default=None),
    question: str | None = Query(default=None),
    message: str | None = Query(default=None),
    error: str | None = Query(default=None),
) -> HTMLResponse:
    return templates.TemplateResponse(
        "chat.html",
        _base_context(
            request,
            "chat",
            "AI Company Chat",
            symbol=symbol,
            answer=answer,
            question=question,
            message=message,
            error=error,
        ),
    )


@router.post("/chat/upload", response_class=HTMLResponse)
async def chat_upload(request: Request, symbol: str = Form(...), file: UploadFile = File(...)) -> HTMLResponse:
    message = None
    error = None
    try:
        content = await file.read()
        result = ChatService().upload_pdf(symbol=symbol, filename=file.filename or "report.pdf", file_bytes=content)
        message = result.message
    except Exception as exc:
        error = str(exc)

    return templates.TemplateResponse(
        "chat.html",
        _base_context(request, "chat", "AI Company Chat", symbol=symbol.strip().upper(), message=message, error=error),
    )


@router.post("/chat/ask", response_class=HTMLResponse)
async def chat_ask(request: Request, symbol: str = Form(...), question: str = Form(...)) -> HTMLResponse:
    answer = None
    used_ai = False
    sources: list[str] = []
    error = None
    try:
        result = ChatService().ask(symbol=symbol, question=question)
        answer = result.answer
        used_ai = result.used_ai
        sources = result.sources
    except Exception as exc:
        error = str(exc)

    return templates.TemplateResponse(
        "chat.html",
        _base_context(
            request,
            "chat",
            "AI Company Chat",
            symbol=symbol.strip().upper(),
            question=question,
            answer=answer,
            used_ai=used_ai,
            sources=sources,
            error=error,
        ),
    )


@router.get("/sectors", response_class=HTMLResponse)
def sectors_page(request: Request, period: str = Query(default="3mo")) -> HTMLResponse:
    data = SectorService().analyze(period=period)
    chart_html = bar_chart_html(
        [sector.sector for sector in data.sectors],
        [sector.average_change_percent or 0 for sector in data.sectors],
        f"Sector performance ({period})",
    )
    return templates.TemplateResponse(
        "sectors.html",
        _base_context(request, "sectors", "Sector Analysis", period=period, data=data, chart_html=chart_html),
    )


@router.get("/portfolio", response_class=HTMLResponse)
def portfolio_page(
    request: Request,
    message: str | None = Query(default=None),
    error: str | None = Query(default=None),
) -> HTMLResponse:
    data = PortfolioService().analyze(fetch_live=False)
    return templates.TemplateResponse(
        "portfolio.html",
        _base_context(request, "portfolio", "Portfolio", data=data, message=message, error=error),
    )


@router.post("/portfolio/add")
def portfolio_add(
    symbol: str = Form(...),
    quantity: float = Form(...),
    avg_price: float = Form(...),
) -> RedirectResponse:
    PortfolioService().add_holding(PortfolioHoldingInput(symbol=symbol, quantity=quantity, avg_price=avg_price))
    return RedirectResponse(url="/portfolio?message=Holding added", status_code=303)


@router.post("/portfolio/remove/{holding_id}")
def portfolio_remove(holding_id: int) -> RedirectResponse:
    PortfolioService().remove_holding(holding_id)
    return RedirectResponse(url="/portfolio?message=Holding removed", status_code=303)


@router.post("/portfolio/upload", response_class=HTMLResponse)
async def portfolio_upload(request: Request, file: UploadFile = File(...)) -> HTMLResponse:
    data = PortfolioService().analyze(fetch_live=False)
    try:
        content = await file.read()
        upload_result = analyze_broker_file(content, file.filename or "holdings.csv", live_prices=False)
        message = f"Analyzed {upload_result['row_count']} holdings from broker file."
    except Exception as exc:
        return templates.TemplateResponse(
            "portfolio.html",
            _base_context(
                request,
                "portfolio",
                "Portfolio",
                data=data,
                error=str(exc),
            ),
        )
    return templates.TemplateResponse(
        "portfolio.html",
        _base_context(
            request,
            "portfolio",
            "Portfolio",
            data=data,
            upload_result=upload_result,
            message=message,
        ),
    )


@router.get("/watchlist", response_class=HTMLResponse)
def watchlist_page(request: Request, message: str | None = Query(default=None)) -> HTMLResponse:
    data = WatchlistService().intelligence()
    return templates.TemplateResponse(
        "watchlist.html",
        _base_context(request, "watchlist", "Watchlist", data=data, message=message),
    )


@router.post("/watchlist/add")
def watchlist_add(symbol: str = Form(...), notes: str = Form(default="")) -> RedirectResponse:
    WatchlistService().add(WatchlistAddRequest(symbol=symbol, notes=notes or None))
    return RedirectResponse(url="/watchlist?message=Added to watchlist", status_code=303)


@router.post("/watchlist/alert")
def watchlist_alert(
    symbol: str = Form(...),
    alert_type: str = Form(...),
    threshold: float = Form(...),
) -> RedirectResponse:
    WatchlistService().add_alert(AlertCreateRequest(symbol=symbol, alert_type=alert_type, threshold=threshold))
    return RedirectResponse(url="/watchlist?message=Alert created", status_code=303)
