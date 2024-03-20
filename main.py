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





# Calculate the total value of the portfolio
total_value = st.session_state.portfolio['Current Value'].sum()
total_investment = st.session_state.portfolio['Amount Invested'].sum()
total_profit_loss = st.session_state.portfolio['Profit/ Loss'].sum()
total_profit_loss_percent = (total_profit_loss / total_investment) * 100

# Graph



import plotly.graph_objs as go

def fetch_historical_data(stock_symbol, period):
    stock_info = yf.Ticker(stock_symbol)
    return stock_info.history(period=period)['Close']
def calculate_portfolio_value_over_time():
    # Ensure we have a list of unique dates over the last month
    end_date = pd.Timestamp.now()
    start_date = end_date - pd.Timedelta(days=30)
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    portfolio_values = pd.Series(0, index=dates)

    for _, row in st.session_state.portfolio.iterrows():
        historical_prices = fetch_historical_data(row['Stock Symbol'], '1mo')
        # Calculate the portfolio value for each date
        for date in dates:
            if date in historical_prices.index:
                 portfolio_values[date] += row['Quantity'] * historical_prices[date]
        # Sum up the value for each stock in the portfolio
        for date in dates:
            date_str = date.strftime('%Y-%m-%d')
            if date_str in historical_prices.index:
                portfolio_values[date] += historical_prices[date_str] * row['Quantity']
    # Plot the portfolio value over time
    fig = go.Figure(data=go.Scatter(x=dates, y=portfolio_values, mode='lines'))
    st.plotly_chart(fig)

    # Check if portfolio_values has valid data
    st.write("Debug: Portfolio values calculated:", portfolio_values.head())  # Debug output

    return portfolio_values

if not st.session_state.portfolio.empty:
    portfolio_values = calculate_portfolio_value_over_time()
    if not portfolio_values.empty:
        # Plotting the portfolio value over time
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=portfolio_values.index, y=portfolio_values, mode='lines', name='Portfolio Value'))
        fig.update_layout(title='Portfolio Value Over Last Month', xaxis_title='Date', yaxis_title='Value')
        st.plotly_chart(fig)
    else:
        st.write("Unable to calculate portfolio values or no data available for the given period.")
else:
    st.write("Your portfolio is currently empty.")
