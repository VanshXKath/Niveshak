import time

from backend.app.portfolio_analysis.analyzer import analyze_broker_file

SAMPLE_CSV = b"""Symbol,Quantity,Avg Cost,Invested,LTP,Cur. Val
TCS,10,3500,35000,3600,36000
INFY,20,1500,30000,1550,31000
HDFCBANK,5,1600,8000,1650,8250
"""


def test_analyze_broker_csv_without_live_prices():
    start = time.perf_counter()
    result = analyze_broker_file(SAMPLE_CSV, "zerodha.csv", live_prices=False)
    elapsed = time.perf_counter() - start

    assert result["row_count"] == 3
    assert result["total_invested"] == 73000
    assert result["total_current_value"] == 75250
    assert len(result["holdings"]) == 3
    assert len(result["insights"]) >= 1
    assert "sector_chart_html" in result
    assert elapsed < 5, f"Analysis took too long: {elapsed:.1f}s"
