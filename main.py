from flask import Flask,render_template,request
import sqlite3
import yfinance as yf


conn = sqlite3.connect("stocks.db")
conn.row_factory = sqlite3.Row
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS stocks(
id INTEGER PRIMARY KEY,
symbol varchar(5),
price FLOAT)''')
conn.commit()
app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('stocks.db')
    conn.row_factory = sqlite3.Row
    return conn

def fetch_stocks(symbol):
    try:
        stocks_data = yf.Ticker(symbol).history(period="1mo")
        if not stocks_data.empty:
            latest_price = stocks_data['Close'].iloc[-1]
            return symbol, latest_price
    except Exception as e:
        print(f"Eror fetching data for {symbol}: {e}")
    return None,None
@app.route('/fetch_stock',methods=['post'])
def fetch_and_store_stock():
    symbol = request.form.get('symbol')
    if symbol:
        symbol, price = fetch_stocks(symbol)
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute( "INSERT INTO stocks (symbol,price)VALUES (?,?)",(symbol,price))
        conn.commit()
        return f"stock data fetched and stored: {symbol} - {price}"
    return "Failed to fetch and store stock data"
@app.route('/')
def display_stocks():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM stocks")
    stocks = cursor.fetchall()
    return render_template('stocks.html',stocks=stocks)

if __name__ == '__main__':
    app.run(debug=True)

