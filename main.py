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

import streamlit.components.v1 as components

# The HTML content, including the blockquote for the widget and the script tag for loading the JavaScript
html_content = '''
    <blockquote class="trendlyne-widgets" data-get-url="https://trendlyne.com/web-widget/swot-widget/Poppins/ZOMATO/?posCol=00A25B&primaryCol=006AFF&negCol=EB3B00&neuCol=F7941E" data-theme="light"></blockquote>
    <script async src="https://cdn-static.trendlyne.com/static/js/webwidgets/tl-widgets.js" charset="utf-8"> </script>
'''

# Use the components.html function to embed the HTML in your Streamlit app
components.html(html_content, height=600)