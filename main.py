# import images
import yfinance as yf
import pandas as pd
import streamlit as st

import plotly.graph_objects as go
from plotly.subplots import make_subplots


# Streamlit interface for input
st.title('Portfolio Management System')

# Initialize 'portfolio' in session_state if it doesn't exist
if 'portfolio' not in st.session_state:
    st.session_state['portfolio'] = pd.DataFrame(columns=[
        'Stock Symbol', 'Currency', 'Quantity', 'Average Purchase Price', 
        'Date of Purchase', 'Current Price', 'Current Value', 
        'Amount Invested', 'Profit/ Loss', 'Profit/ Loss %', 
        'Current Value INR', 'Amount Invested INR'
    ])


# Display the total investment and current value prominently
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

def fetch_usd_to_inr_exchange_rate():
    exchange_rate_info = yf.Ticker("USDINR=X")
    try:
        # Attempt to fetch the exchange rate for the last day
        usd_to_inr = exchange_rate_info.history(period="1d")['Close'].iloc[-1]
    except IndexError:
        # If there's no data for the last day, try fetching for the last 5 days and get the most recent
        try:
            usd_to_inr = exchange_rate_info.history(period="5d")['Close'].dropna().iloc[-1]
        except IndexError:
            # If there's still no data, you might need a more robust fallback
            # This could be a static value or an error message indicating the data is not available
            st.error("Failed to fetch the USD to INR exchange rate. Please try again later.")
            usd_to_inr = None  # or a static fallback value if preferred
    return usd_to_inr

# Fetch the current USD to INR exchange rate
usd_to_inr_rate = fetch_usd_to_inr_exchange_rate()

# # Convert values from USD to INR
# st.session_state.portfolio['Current Value INR'] = st.session_state.portfolio['Current Value'] * usd_to_inr_rate
# st.session_state.portfolio['Amount Invested INR'] = st.session_state.portfolio['Amount Invested'] * usd_to_inr_rate


total_value_inr = st.session_state.portfolio['Current Value INR'].sum()
total_investment_inr = st.session_state.portfolio['Amount Invested INR'].sum()

col1, col2 = st.columns(2)
col1.metric("Total Amount Invested (INR)", f"₹{total_investment_inr:,.2f}")
col2.metric("Current Portfolio Value (INR)", f"₹{total_value_inr:,.2f}")


# # Use st.metric to display the total amount invested and current value
# col1, col2 = st.columns(2)
# col1.metric("Total Amount Invested", f"₹ {total_investment:,.2f}")
# col2.metric("Current Portfolio Value", f"₹ {total_value:,.2f}")








stock_symbol = st.text_input('Stock Symbol', 'AAPL')
currency = st.selectbox('Currency', ['USD', 'INR'])
quantity = st.number_input('Quantity', min_value=0.01, step=0.01, format="%.2f")
average_price = st.number_input('Average Purchase Price', min_value=0.01)
purchase_date = st.date_input("Date of Purchase")  # Date of purchase input
add_button = st.button('Add to Portfolio')

# Initialize portfolio in session state if it doesn't exist
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = pd.DataFrame(columns=['Stock Symbol', 'Currency', 'Quantity', 'Average Purchase Price', 'Date of Purchase', 'Current Price', 'Current Value', 'Amount Invested', 'Profit/ Loss', 'Profit/ Loss %'])

# # Check if the 'Currency' column exists, and add it if it doesn't
# if 'Currency' not in st.session_state.portfolio.columns:
#     # Assuming default currency is USD for existing stocks, adjust as needed
#     if stock_symbol.endswith('.NS') or stock_symbol.endswith('.ns'):
#         st.session_state.portfolio['Currency'] = 'INR'
#     else:
#         st.session_state.portfolio['Currency'] = 'USD'


def add_stock_to_portfolio(stock_symbol, quantity, average_price, purchase_date):
    stock_info = yf.Ticker(stock_symbol)
    try:
        current_price = stock_info.history(period='1d')['Close'][-1]
    except IndexError:
        st.error("Failed to fetch current price. Please check the stock symbol.")
        return
    
    # Calculate current value and amount invested for the new stock
    current_value_new_stock = quantity * current_price
    amount_invested_new_stock = quantity * average_price
    profit_loss_new_stock = current_value_new_stock - amount_invested_new_stock
    profit_loss_percent_new_stock = (profit_loss_new_stock / amount_invested_new_stock) * 100 if amount_invested_new_stock != 0 else 0
    
    # Check if the stock symbol already exists in the portfolio
    if stock_symbol in st.session_state.portfolio['Stock Symbol'].values:
        # Get the index of the existing stock
        index = st.session_state.portfolio[st.session_state.portfolio['Stock Symbol'] == stock_symbol].index[0]
        
        # Get existing values
        existing_quantity = st.session_state.portfolio.at[index, 'Quantity']
        existing_average_price = st.session_state.portfolio.at[index, 'Average Purchase Price']
        existing_amount_invested = st.session_state.portfolio.at[index, 'Amount Invested']
        
        # Calculate new values
        new_quantity = existing_quantity + quantity
        new_average_price = ((existing_average_price * existing_quantity) + (average_price * quantity)) / new_quantity
        new_amount_invested = existing_amount_invested + amount_invested_new_stock
        new_current_value = new_quantity * current_price
        new_profit_loss = new_current_value - new_amount_invested
        new_profit_loss_percent = (new_profit_loss / new_amount_invested) * 100 if new_amount_invested != 0 else 0
        
        # Update the DataFrame
        st.session_state.portfolio.at[index, 'Quantity'] = new_quantity
        st.session_state.portfolio.at[index, 'Average Purchase Price'] = new_average_price
        st.session_state.portfolio.at[index, 'Current Price'] = current_price
        st.session_state.portfolio.at[index, 'Current Value'] = new_current_value
        st.session_state.portfolio.at[index, 'Amount Invested'] = new_amount_invested
        st.session_state.portfolio.at[index, 'Profit/ Loss'] = new_profit_loss
        st.session_state.portfolio.at[index, 'Profit/ Loss %'] = new_profit_loss_percent
        
    else:

        # Example of adding a stock priced in INR
        if stock_symbol.endswith('.NS'):  # Assuming '.NS' denotes Indian stocks on Yahoo Finance
            currency = 'INR'
        else:
            currency = 'USD'  # Default to USD for simplicity
        # Add this entry to the portfolio DataFrame in the session state
        new_stock = pd.DataFrame([{
            'Stock Symbol': stock_symbol, 
            'Currency' : currency,
            'Quantity': quantity, 
            'Average Purchase Price': average_price,
            'Date of Purchase': purchase_date, 
            'Current Price': current_price, 
            'Current Value': current_value_new_stock,
            'Amount Invested': amount_invested_new_stock,
            'Profit/ Loss': profit_loss_new_stock,
            'Profit/ Loss %': profit_loss_percent_new_stock
        }])
        
        st.session_state.portfolio = pd.concat([st.session_state.portfolio, new_stock], ignore_index=True)

# Reassign the DataFrame to ensure Streamlit recognizes the update
st.session_state.portfolio = st.session_state.portfolio.copy()


if add_button:
    add_stock_to_portfolio(stock_symbol, quantity, average_price, purchase_date)

# Fetch the current USD to INR exchange rate here if not already done
usd_to_inr_rate = fetch_usd_to_inr_exchange_rate()

# Adjusting conversion for each asset based on its currency
def adjust_currency(row):
    if row['Currency'] == 'USD':
        # Convert only if the asset is in USD
        row['Current Value INR'] = row['Current Value'] * usd_to_inr_rate
        row['Amount Invested INR'] = row['Amount Invested'] * usd_to_inr_rate
    else:
        # If the asset is already in INR, just copy the original values
        row['Current Value INR'] = row['Current Value']
        row['Amount Invested INR'] = row['Amount Invested']
    return row

# Apply the conversion adjustment to each row in the portfolio DataFrame
st.session_state.portfolio = st.session_state.portfolio.apply(adjust_currency, axis=1)

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
    cols = st.columns([0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.2, 0.1])
    # Example of displaying stock info - adjust according to your needs
    cols[0].write(row['Stock Symbol'])
    cols[1].write(row['Quantity'])
    # Continue for other columns...
    sell_quantity = cols[9].number_input('Sell Qty', min_value=0.01, max_value=float(row['Quantity']), step=0.01, format="%.2f", key=f"sell_{index}")
    if cols[9].button('Sell', key=f"sell_btn_{index}"):
        sell_stock_from_portfolio(index, sell_quantity)
    if cols[10].button('Sell All', key=f"sell_all_{index}"):
        sell_stock_from_portfolio(index, row['Quantity'])

def calculate_current_value():
    stock_values = {}
    for _, row in st.session_state.portfolio.iterrows():
        symbol = row['Stock Symbol']
        quantity = row['Quantity']
        # Fetch current stock price
        stock_info = yf.Ticker(symbol)
        try:
            current_price = (stock_info.history(period='1d')['Close'][-1])
            # Calculate current value for this stock and add to the dictionary
            stock_values[symbol] = current_price * quantity
        except IndexError:
            st.error(f"Failed to fetch current price for {symbol}.")
            continue  # Skip this stock if its current price can't be fetched
    return stock_values

def calculate_current_value_in_inr():
    usd_to_inr_rate = fetch_usd_to_inr_exchange_rate()  # Ensure this fetches the current exchange rate
    stock_values_in_inr = {}
    
    for _, row in st.session_state.portfolio.iterrows():
        symbol = row['Stock Symbol']
        quantity = row['Quantity']
        currency = row['Currency']  # Ensure your portfolio has a 'Currency' column

        # Fetch current stock price
        stock_info = yf.Ticker(symbol)
        try:
            current_price_usd = stock_info.history(period='1d')['Close'][-1]
            # If the stock is priced in USD, convert the price to INR
            if currency == 'USD':
                current_price_inr = current_price_usd * usd_to_inr_rate
            else:
                current_price_inr = current_price_usd  # Assuming the price is already in INR

            # Calculate current value for this stock in INR and add to the dictionary
            stock_values_in_inr[symbol] = current_price_inr * quantity
        except IndexError:
            st.error(f"Failed to fetch current price for {symbol}.")
            continue  # Skip this stock if its current price can't be fetched
    
    return stock_values_in_inr



# Display the updated portfolio
st.write('Your Portfolio', st.session_state.portfolio)





# Calculate the total value of the portfolio only if the portfolio is not empty
if not st.session_state.portfolio.empty:
    total_value = st.session_state.portfolio['Current Value INR'].sum()
    total_investment = st.session_state.portfolio['Amount Invested INR'].sum()
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


# Graph




if not st.session_state.portfolio.empty:
    stock_values = calculate_current_value_in_inr()
    invested_amounts = st.session_state.portfolio.groupby('Stock Symbol')['Amount Invested INR'].sum()

    if stock_values and not invested_amounts.empty:
        # Data for the first pie chart (Current Value)
        labels_value = list(stock_values.keys())
        values_value = list(stock_values.values())

        # Data for the second pie chart (Amount Invested)
        labels_invested = invested_amounts.index.tolist()
        values_invested = invested_amounts.values.tolist()

        # Create subplots: 1 row, 2 cols
        fig = make_subplots(rows=1, cols=2, specs=[[{'type': 'pie'}, {'type': 'pie'}]])

        # First pie chart
        fig.add_trace(
            go.Pie(labels=labels_value, values=values_value, hole=.3, title="Current Value INR"),
            row=1, col=1
        )

        # Second pie chart
        fig.add_trace(
            go.Pie(labels=labels_invested, values=values_invested, hole=.3, title="Amount Invested INR"),
            row=1, col=2
        )

        # Update layout for a cleaner look
        fig.update_layout(
            title_text="Portfolio Distribution",
            annotations=[dict(text='Distribution by Current Value', x=0.18, y=-0.1, font_size=12, showarrow=False),
                        dict(text='Distribution by Amount Invested', x=0.82, y=-0.1, font_size=12, showarrow=False)]
        )

        st.plotly_chart(fig)
    else:
        st.write("Unable to calculate values for the stocks in your portfolio.")
else:
    st.write("Your portfolio is currently empty.")



def calculate_current_value_for_last_month_plotly():
    for _, row in st.session_state.portfolio.iterrows():
        symbol = row['Stock Symbol']
        # Fetch current stock price
        stock_info = yf.Ticker(symbol)
        try:
            # Fetch stock history for the last month with daily intervals
            stock_history = stock_info.history(period='1mo', interval='1d')

            # Create a Plotly figure
            fig = go.Figure()

            # Add the time series data
            fig.add_trace(go.Scatter(x=stock_history.index, y=stock_history['Close'], mode='lines', name=symbol))

            # Update layout with title and axis labels
            fig.update_layout(title=f'Stock Price of {symbol} in Last 30 Days',
                            xaxis_title='Date',
                            yaxis_title='Stock Price')

            # Display the figure in the Streamlit app
            st.plotly_chart(fig)

        except Exception as e:
            # Handle errors and continue with the next iteration
            st.error(f"Failed to fetch current price for {symbol}. Error: {e}")
            continue

calculate_current_value_for_last_month_plotly()


# def calculate_current_value_for_last_month_plotly():
#     for _, row in st.session_state.portfolio.iterrows():
#         symbol = row['Stock Symbol']
#         # Fetch current stock price
#         stock_info = yf.Ticker(symbol)
#         try:
#             # Fetch stock history for the last month with daily intervals
#             stock_history = stock_info.history(period='1mo', interval='1d')

#             # Create a Plotly figure
#             fig = go.Figure()

#             # Add the time series data
#             fig.add_trace(go.Scatter(x=stock_history.index, y=stock_history['Close'], mode='lines', name=symbol))

#             # Update layout with title and axis labels
#             fig.update_layout(title=f'Stock Price of {symbol} in Last 30 Days',
#                             xaxis_title='Date',
#                             yaxis_title='Stock Price')

#             # Display the figure in the Streamlit app
#             st.plotly_chart(fig)

#         except Exception as e:
#             # Handle errors and continue with the next iteration
#             st.error(f"Failed to fetch current price for {symbol}. Error: {e}")
#             continue

# calculate_current_value_for_last_month_plotly()