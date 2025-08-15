from flask import Flask, render_template, request
import pandas as pd
import datetime

# Data fetching uses yfinance; keep import local in case it's unavailable during install
try:
    import yfinance as yf
except Exception:
    yf = None

try:
    import plotly.graph_objs as go
    from plotly.subplots import make_subplots
except Exception:
    go = None
    make_subplots = None

app = Flask(__name__)


def fetch_gold(period: str = '1y', interval: str = '1d') -> pd.DataFrame:
    """Fetch gold price history using yfinance ticker 'GC=F' (Gold futures).

    Returns a DataFrame with a `close` column indexed by date.
    """
    if yf is None:
        raise RuntimeError('yfinance is not installed')

    ticker = 'GC=F'
    # yfinance returns a DataFrame with DatetimeIndex; we only need Close
    df = yf.download(ticker, period=period, interval=interval, progress=False)
    if df is None or df.empty:
        return pd.DataFrame()
    df = df[['Close']].rename(columns={'Close': 'close'})
    return df


def compute_macd(df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
    """Compute MACD, signal line and histogram.

    Adds columns: ema_fast, ema_slow, macd, signal, hist
    """
    df = df.copy()
    df['ema_fast'] = df['close'].ewm(span=fast, adjust=False).mean()
    df['ema_slow'] = df['close'].ewm(span=slow, adjust=False).mean()
    df['macd'] = df['ema_fast'] - df['ema_slow']
    df['signal'] = df['macd'].ewm(span=signal, adjust=False).mean()
    df['hist'] = df['macd'] - df['signal']
    return df


@app.route('/')
def index():
    period = request.args.get('period', '1y')
    interval = request.args.get('interval', '1d')
    try:
        df = fetch_gold(period=period, interval=interval)
        if df.empty:
            raise RuntimeError('no data returned for the requested period')
        df = compute_macd(df)

        if go is None or make_subplots is None:
            raise RuntimeError('plotly is not installed')

        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.7, 0.3])
        fig.add_trace(go.Scatter(x=df.index, y=df['close'], name='Gold Close', line=dict(color='gold')), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['macd'], name='MACD', line=dict(color='orange')), row=2, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['signal'], name='Signal', line=dict(color='blue')), row=2, col=1)
        fig.add_trace(go.Bar(x=df.index, y=df['hist'], name='Histogram', marker_color='green'), row=2, col=1)
        fig.update_layout(height=700, title=f'Gold (GC=F) Close and MACD 	6 period={period} interval={interval}')
        graph_div = fig.to_html(full_html=False)
    except Exception as e:
        # Minimal error display on page
        graph_div = f"<div class='alert'>Error: {e}</div>"

    return render_template('index.html', graph_div=graph_div, period=period, interval=interval)


if __name__ == '__main__':
    # Development server
    app.run(host='0.0.0.0', port=5000, debug=True)
