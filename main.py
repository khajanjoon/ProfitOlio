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
    st.session_state.portfolio = pd.DataFrame(columns=['Stock Symbol', 'Quantity', 'Average Purchase Price', 'Date of Purchase', 'Current Price', 'Current Value', 'Amount Invested', 'Profit/ Loss', 'Profit/ Loss %'])

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
    profit_loss = current_value - amount_invested
    profit_loss_percent = (profit_loss / amount_invested) * 100

    # Create a new entry for this stock as a DataFrame
    new_stock = pd.DataFrame([{
        'Stock Symbol': stock_symbol, 
        'Quantity': quantity, 
        'Average Purchase Price': average_price,
        'Date of Purchase': purchase_date, 
        'Current Price': current_price, 
        'Current Value': current_value,
        'Amount Invested': amount_invested,
        'Profit/ Loss': profit_loss,
        'Profit/ Loss %': profit_loss_percent
    }])
    
    # Add this entry to the portfolio DataFrame in the session state
    st.session_state.portfolio = pd.concat([st.session_state.portfolio, new_stock], ignore_index=True)

if add_button:
    add_stock_to_portfolio(stock_symbol, quantity, average_price, purchase_date)


# Function to sell stocks
def sell_stock_from_portfolio(index, sell_quantity):
    # Assuming 'index' is the index of the stock in the DataFrame and 'sell_quantity' is how much to sell
    stock = st.session_state.portfolio.loc[index]
    if sell_quantity >= stock['Quantity']:
        # If selling more or equal to what's in portfolio, remove the stock
        st.session_state.portfolio = st.session_state.portfolio.drop(index)
    else:
        # Adjust the quantity and recalculate metrics
        st.session_state.portfolio.at[index, 'Quantity'] -= sell_quantity
        # Recalculate metrics like current value, profit/loss, etc. based on the new quantity
        # This is a simplified example; you'll need to adjust it according to your specific calculations

    # After modifications, reset the index and update the session state
    st.session_state.portfolio.reset_index(drop=True, inplace=True)

# Display the updated portfolio and add "Sell" buttons
for index, row in st.session_state.portfolio.iterrows():
    cols = st.columns([0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.2])
    # Example of displaying stock info - adjust according to your needs
    cols[0].write(row['Stock Symbol'])
    cols[1].write(row['Quantity'])
    # Continue for other columns...
    sell_quantity = cols[9].number_input('Sell Qty', min_value=1, max_value=row['Quantity'], key=f"sell_{index}")
    if cols[9].button('Sell', key=f"sell_btn_{index}"):
        sell_stock_from_portfolio(index, sell_quantity)

# Ensure this section is not within the loop

# Display the updated portfolio
st.write('Your Portfolio', st.session_state.portfolio)