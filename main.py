import yfinance as yf
import pandas as pd
import streamlit as st

# Streamlit interface for input
st.title('Portfolio Management System')
stock_symbol = st.text_input('Stock Symbol', 'AAPL')
quantity = st.number_input('Quantity', min_value=1)
average_price = st.number_input('Average Purchase Price', min_value=0.01)
purchase_date = st.date_input("Date of Purchase")  # Date of purchase input
add_button = st.button('Add to Portfolio')

# Initialize portfolio in session state if it doesn't exist
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = pd.DataFrame(columns=['Stock Symbol', 'Quantity', 'Average Purchase Price', 'Date of Purchase', 'Current Price', 'Current Value', 'Amount Invested'])

def add_stock_to_portfolio(stock_symbol, quantity, average_price, purchase_date):
    stock_info = yf.Ticker(stock_symbol)
    try:
        current_price = stock_info.history(period='1d')['Close'][-1]
    except IndexError:
        st.error("Failed to fetch current price. Please check the stock symbol.")
        return

    # Calculate current value and amount invested
    current_value = quantity * current_price
    amount_invested = quantity * average_price

    # Create a new entry for this stock as a DataFrame
    new_stock = pd.DataFrame([{
        'Stock Symbol': stock_symbol, 
        'Quantity': quantity, 
        'Average Purchase Price': average_price,
        'Date of Purchase': purchase_date, 
        'Current Price': current_price, 
        'Current Value': current_value,
        'Amount Invested': amount_invested
    }])
    
    # Add this entry to the portfolio DataFrame in the session state
    st.session_state.portfolio = pd.concat([st.session_state.portfolio, new_stock], ignore_index=True)

if add_button:
    add_stock_to_portfolio(stock_symbol, quantity, average_price, purchase_date)

# Display the updated portfolio
st.write('Your Portfolio', st.session_state.portfolio)
