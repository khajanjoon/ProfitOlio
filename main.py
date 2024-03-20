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

    # Check if the stock symbol already exists in the portfolio
    if stock_symbol in st.session_state.portfolio['Stock Symbol'].values:
        # Get the index of the existing stock
        index = st.session_state.portfolio[st.session_state.portfolio['Stock Symbol'] == stock_symbol].index[0]
        
        # Update the existing entry
        existing_quantity = st.session_state.portfolio.at[index, 'Quantity']
        existing_average_price = st.session_state.portfolio.at[index, 'Average Purchase Price']

        # Calculate the new average price
        total_cost = (existing_average_price * existing_quantity) + (average_price * quantity)
        new_quantity = existing_quantity + quantity
        new_average_price = total_cost / new_quantity
        
        # Update the DataFrame
        st.session_state.portfolio.at[index, 'Quantity'] = new_quantity
        st.session_state.portfolio.at[index, 'Average Purchase Price'] = new_average_price
        st.session_state.portfolio.at[index, 'Date of Purchase'] = purchase_date  # Assuming the most recent purchase date is desired
    else:
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





# Calculate the total value of the portfolio only if the portfolio is not empty
if not st.session_state.portfolio.empty:
    total_value = st.session_state.portfolio['Current Value'].sum()
    total_investment = st.session_state.portfolio['Amount Invested'].sum()
    total_profit_loss = st.session_state.portfolio['Profit/ Loss'].sum()
    if total_investment > 0:
        total_profit_loss_percent = (total_profit_loss / total_investment) * 100
    else:
        total_profit_loss_percent = 0
else:
    # Set default values to 0 if the portfolio is empty
    total_value = 0
    total_investment = 0
    total_profit_loss = 0
    total_profit_loss_percent = 0

# Continue with the rest of your code...


# Graph



import plotly.graph_objs as go

# Assuming 'portfolio' is a DataFrame with your stock symbols and quantities
# Function to calculate current value of each stock in the portfolio
def calculate_current_value():
    stock_values = {}
    for _, row in st.session_state.portfolio.iterrows():
        symbol = row['Stock Symbol']
        quantity = row['Quantity']
        # Fetch current stock price
        stock_info = yf.Ticker(symbol)
        try:
            current_price = stock_info.history(period='1d')['Close'][-1]
            # Calculate current value for this stock and add to the dictionary
            stock_values[symbol] = current_price * quantity
        except IndexError:
            st.error(f"Failed to fetch current price for {symbol}.")
            continue  # Skip this stock if its current price can't be fetched

    return stock_values

if not st.session_state.portfolio.empty:
    stock_values = calculate_current_value()
    if stock_values:
        # Prepare data for pie chart
        labels = list(stock_values.keys())
        values = list(stock_values.values())

        # Plot pie chart
        fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.3)])
        fig.update_layout(title_text="Portfolio Distribution by Current Value")
        st.plotly_chart(fig)
    else:
        st.write("Unable to calculate current values for the stocks in your portfolio.")
else:
    st.write("Your portfolio is currently empty.")
