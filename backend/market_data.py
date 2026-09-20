import yfinance as yf
from datetime import datetime


def get_stock_price(symbol):
    """
    Get the latest available stock price and basic market information.
    For Indian NSE stocks, use symbols like TCS.NS
    """

    try:
        ticker = yf.Ticker(symbol)

        # Get recent market history
        history = ticker.history(period="5d")

        if history.empty:
            return {
                "success": False,
                "error": f"No market data found for {symbol}"
            }

        latest = history.iloc[-1]

        current_price = float(latest["Close"])
        previous_close = None

        if len(history) >= 2:
            previous_close = float(history.iloc[-2]["Close"])

        change = None
        change_percent = None

        if previous_close:
            change = current_price - previous_close
            change_percent = (change / previous_close) * 100

        # Basic information
        info = ticker.info

        return {
            "success": True,
            "symbol": symbol,
            "company": info.get("longName") or info.get("shortName") or symbol,
            "current_price": round(current_price, 2),
            "previous_close": round(previous_close, 2)
                if previous_close else None,
            "change": round(change, 2)
                if change is not None else None,
            "change_percent": round(change_percent, 2)
                if change_percent is not None else None,
            "currency": info.get("currency", "INR"),
            "market_cap": info.get("marketCap"),
            "pe_ratio": info.get("trailingPE"),
            "eps": info.get("trailingEps"),
            "52_week_high": info.get("fiftyTwoWeekHigh"),
            "52_week_low": info.get("fiftyTwoWeekLow"),
            "dividend_yield": info.get("dividendYield"),
            "volume": int(latest["Volume"])
                if latest["Volume"] else None,
            "updated_at": datetime.now().isoformat()
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def get_stock_history(symbol, period="1mo"):
    """
    Get historical stock prices.
    """

    try:
        ticker = yf.Ticker(symbol)
        history = ticker.history(period=period)

        if history.empty:
            return {
                "success": False,
                "error": f"No historical data found for {symbol}"
            }

        records = []

        for date, row in history.iterrows():
            records.append({
                "date": date.strftime("%Y-%m-%d"),
                "open": round(float(row["Open"]), 2),
                "high": round(float(row["High"]), 2),
                "low": round(float(row["Low"]), 2),
                "close": round(float(row["Close"]), 2),
                "volume": int(row["Volume"])
            })

        return {
            "success": True,
            "symbol": symbol,
            "period": period,
            "data": records
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def get_stock_metrics(symbol):
    """
    Get additional financial metrics for a stock.
    """

    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info

        return {
            "success": True,
            "symbol": symbol,
            "company": info.get("longName") or info.get("shortName"),
            "sector": info.get("sector"),
            "industry": info.get("industry"),
            "market_cap": info.get("marketCap"),
            "pe_ratio": info.get("trailingPE"),
            "forward_pe": info.get("forwardPE"),
            "eps": info.get("trailingEps"),
            "price_to_book": info.get("priceToBook"),
            "52_week_high": info.get("fiftyTwoWeekHigh"),
            "52_week_low": info.get("fiftyTwoWeekLow"),
            "dividend_yield": info.get("dividendYield"),
            "profit_margin": info.get("profitMargins"),
            "revenue_growth": info.get("revenueGrowth")
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def search_stock(company_name):
    """
    Search Yahoo Finance for a company.
    """

    try:
        search = yf.Search(company_name)

        quotes = search.quotes

        results = []

        for quote in quotes[:10]:
            results.append({
                "symbol": quote.get("symbol"),
                "name": quote.get("longname")
                    or quote.get("shortname"),
                "exchange": quote.get("exchange"),
                "type": quote.get("quoteType")
            })

        return {
            "success": True,
            "query": company_name,
            "results": results
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }