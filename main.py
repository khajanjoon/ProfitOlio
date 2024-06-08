# import images
import streamlit as st 
import sqlite3
from sqlite3 import Error
import hashlib
import pandas as pd
from plotly.subplots import make_subplots
from streamlit_option_menu import option_menu
from openai import OpenAI
from datetime import date
import yfinance as yf
from prophet import Prophet
from prophet.plot import plot_plotly
from plotly import graph_objs as go
import plotly.graph_objects as go




# Connection to SQLite database
conn = sqlite3.connect('finance.db') 
c = conn.cursor()

# Create a table to store user information
c.execute('''
        CREATE TABLE IF NOT EXISTS users
        ([user_id] INTEGER PRIMARY KEY, [username] TEXT, [password] TEXT)
        ''')    

# Create a table to store portfolio information
c.execute('''
        CREATE TABLE IF NOT EXISTS portfolio
        ([entry_id] INTEGER PRIMARY KEY, [user_id] INTEGER, [stock_symbol] TEXT, 
        [currency] TEXT, [quantity] REAL, [average_purchase_price] REAL, 
        [date_of_purchase] DATE, [current_price] REAL, [current_value] REAL, 
        [amount_invested] REAL, [profit_loss] REAL, [profit_loss_percent] REAL)
        ''')   

conn.commit() # Commit the changes

# Set page title and layout
st.set_page_config(page_title="Portfolio Management System", layout="wide") 

# Hash the password using SHA-256
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest() 

# Function to register a new user
def register_user(username, password):
    c.execute('SELECT * FROM users WHERE username = ?', (username,))
    if c.fetchone() is not None:
        return False
    hashed_pw = hash_password(password)
    c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_pw))
    conn.commit()
    return True  

# Function to check if the user exists
def check_user(username, password):
    hashed_pw = hash_password(password)
    c.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, hashed_pw))
    return c.fetchone() is not None

# Function to get the user ID
def get_user_id(username):
    c.execute('SELECT user_id FROM users WHERE username = ?', (username,))
    result = c.fetchone()
    return result[0] if result else None

# For login sidebar
st.title('ProfitOlio')
menu = ["Home", "Login", "Signup", "Logout"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Home":
    st.subheader("Home")
    st.write("Welcome to the Portfolio Management System")

elif choice == "Login":
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type='password')
    if st.sidebar.button("Login"):
        if check_user(username, password):
            st.success(f"Logged In as {username}")
            user_id = get_user_id(username)
            st.session_state['user_id'] = user_id
        else:
            st.warning("Incorrect Username/Password")

elif choice == "Signup":
    new_username = st.sidebar.text_input("New Username")
    new_password = st.sidebar.text_input("New Password", type='password')
    if st.sidebar.button("Signup"):
        if register_user(new_username, new_password):
            st.success("You have successfully created a new account!")
            st.info("Go to the Login Menu to login")
        else:
            st.warning("Username already exists")

elif choice == "Logout":
    if st.sidebar.button("Logout"):
        if 'user_id' in st.session_state:
            del st.session_state.user_id  # Clear user session
            st.info("You have been logged out.")

# Initializing the session state and page layout
if 'user_id' in st.session_state:
            st.sidebar.success(f"Logged in successfully as {username}")
            selected = option_menu(
            menu_title = None,
            options = ['Portfolio', 'Charts', 'FinBot', 'P&L to Date', 'Price Predictor', 'Financial Statement','Widgets'],
            icons = ['🍎', '🍌', '🍊', '🫡', '📈', '₹', '🥳'],
            menu_icon = "cast",
            default_index = 0,
            orientation = "horizontal",
            )

            if selected == "Portfolio":
                st.title('Portfolio Management System')

                if 'portfolio' not in st.session_state:
                    st.session_state['portfolio'] = pd.DataFrame(columns=[
                        'Stock Symbol', 'Currency', 'Quantity', 'Average Purchase Price', 
                        'Date of Purchase', 'Current Price', 'Current Value', 
                        'Amount Invested', 'Profit/ Loss', 'Profit/ Loss %', 
                        'Current Value INR', 'Amount Invested INR'
                    ])

                if not st.session_state.portfolio.empty:

                    total_value = st.session_state.portfolio['Current Value'].sum()
                    total_investment = st.session_state.portfolio['Amount Invested'].sum()
                    total_profit_loss = st.session_state.portfolio['Profit/ Loss'].sum()
                    if total_investment > 0:
                        total_profit_loss_percent = (total_profit_loss / total_investment) * 100
                    else:
                        total_profit_loss_percent = 0
                else:
                    total_value = 0
                    total_investment = 0
                    total_profit_loss = 0
                    total_profit_loss_percent = 0

                def fetch_usd_to_inr_exchange_rate():
                    exchange_rate_info = yf.Ticker("USDINR=X")
                    try:
                        usd_to_inr = exchange_rate_info.history(period="1d")['Close'].iloc[-1]
                    except IndexError:
                        try:
                            usd_to_inr = exchange_rate_info.history(period="5d")['Close'].dropna().iloc[-1]
                        except IndexError:
                            st.error("Failed to fetch the USD to INR exchange rate. Please try again later.")
                            usd_to_inr = None
                    return usd_to_inr

                usd_to_inr_rate = fetch_usd_to_inr_exchange_rate()

                total_value_inr = st.session_state.portfolio['Current Value INR'].sum()
                total_investment_inr = st.session_state.portfolio['Amount Invested INR'].sum()
                s = total_value_inr - total_investment_inr
                sp = (s / total_investment_inr) * 100 if total_investment_inr != 0 else 0

                col1, col2 = st.columns(2)
                col1.metric("Total Amount Invested (INR)", f"₹{total_investment_inr:,.2f}")
                col2.metric("Current Portfolio Value (INR)", f"₹{total_value_inr:,.2f}", delta=f"₹{s:.2f} ({sp:.2f}%)")
                
                st.markdown(
                    """
                    <style>
                    .big-font {
                        font-size:20px !important;
                    }
                    </style>
                    """, 
                    unsafe_allow_html=True,
                )

                st.markdown('<p class="big-font">#Stock Symbol (in Caps 🅰)</p>', unsafe_allow_html=True)

                stock_symbol = st.text_input('Stock Symbol (in Caps 🅰)', 'AAPL').upper()
                st.text('Note: For Indian stocks, use the ".NS" extension. For US stocks, use the stock symbol only.')
                st.text('For example, for Reliance Industries, use "RELIANCE.NS" and for Apple Inc., use "AAPL", for Cryptocurrency like Bitcoin use "BTC-USD" as example.')
                st.text('For a list of stock symbols, visit https://in.finance.yahoo.com/ or https://finance.yahoo.com/')
                currency = st.selectbox('Currency', ['USD', 'INR'])
                st.text('Note: For Indian stocks, the currency is INR. For US stocks and cryptocurrencies, the currency is USD.')
                quantity = st.number_input('Quantity', min_value=0.01, step=0.01, format="%.2f")
                average_price = st.number_input('Average Purchase/Sell Price', min_value=0.01)
                purchase_date = st.date_input("Date of Purchase/Sell")
                # columns for button for alignment
                col1, col2 = st.columns(2)

                with col1:
                    add_button = st.button('Add to Portfolio')

                with col2:
                    sell_button = st.button('Sell from Portfolio')

                if 'portfolio' not in st.session_state:
                    st.session_state.portfolio = pd.DataFrame(columns=['Stock Symbol', 'Currency', 'Quantity', 'Average Purchase Price', 'Date of Purchase', 'Current Price', 'Current Value', 'Amount Invested', 'Profit/ Loss', 'Profit/ Loss %'])

                def add_stock_to_portfolio(stock_symbol, quantity, average_price, purchase_date):
                    stock_info = yf.Ticker(stock_symbol)
                    try:
                        current_price = stock_info.history(period='1d')['Close'][-1]
                    except IndexError:
                        st.error("Failed to fetch current price. Please check the stock symbol.")
                        return
                    
                    current_value_new_stock = quantity * current_price
                    amount_invested_new_stock = quantity * average_price
                    profit_loss_new_stock = current_value_new_stock - amount_invested_new_stock
                    profit_loss_percent_new_stock = (profit_loss_new_stock / amount_invested_new_stock) * 100 if amount_invested_new_stock != 0 else 0
                    
                    if stock_symbol in st.session_state.portfolio['Stock Symbol'].values:
                        index = st.session_state.portfolio[st.session_state.portfolio['Stock Symbol'] == stock_symbol].index[0]
                        existing_quantity = st.session_state.portfolio.at[index, 'Quantity']
                        existing_average_price = st.session_state.portfolio.at[index, 'Average Purchase Price']
                        existing_amount_invested = st.session_state.portfolio.at[index, 'Amount Invested']
                        
                        new_quantity = existing_quantity + quantity
                        new_average_price = ((existing_average_price * existing_quantity) + (average_price * quantity)) / new_quantity
                        new_amount_invested = existing_amount_invested + amount_invested_new_stock
                        new_current_value = new_quantity * current_price
                        new_profit_loss = new_current_value - new_amount_invested
                        new_profit_loss_percent = (new_profit_loss / new_amount_invested) * 100 if new_amount_invested != 0 else 0
                        
                        st.session_state.portfolio.at[index, 'Quantity'] = new_quantity
                        st.session_state.portfolio.at[index, 'Average Purchase Price'] = new_average_price
                        st.session_state.portfolio.at[index, 'Current Price'] = current_price
                        st.session_state.portfolio.at[index, 'Current Value'] = new_current_value
                        st.session_state.portfolio.at[index, 'Amount Invested'] = new_amount_invested
                        st.session_state.portfolio.at[index, 'Profit/ Loss'] = new_profit_loss
                        st.session_state.portfolio.at[index, 'Profit/ Loss %'] = new_profit_loss_percent
                    else:
                        if stock_symbol.endswith('.NS') or stock_symbol.endswith(".ns"): 
                            currency = 'INR'
                        else:
                            currency = 'USD'  
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

                st.session_state.portfolio = st.session_state.portfolio.copy()

                if add_button:
                    add_stock_to_portfolio(stock_symbol, quantity, average_price, purchase_date)

                usd_to_inr_rate = fetch_usd_to_inr_exchange_rate()


                def sell_stock_from_portfolio(stock_symbol, quantity, average_price, purchase_date):
                    stock_info = yf.Ticker(stock_symbol)
                    try:
                        current_price = stock_info.history(period='1d')['Close'][-1]
                    except Exception as e:  # Broader exception handling
                        st.error(f"Failed to fetch current price due to {e}. Please check the stock symbol.")
                        return
                    
                    current_value_new_stock = quantity * current_price
                    amount_invested_new_stock = quantity * average_price
                    profit_loss_new_stock = current_value_new_stock - amount_invested_new_stock
                    profit_loss_percent_new_stock = (profit_loss_new_stock / amount_invested_new_stock) * 100 if amount_invested_new_stock != 0 else 0
                    
                    if stock_symbol in st.session_state.portfolio['Stock Symbol'].values:
                        index = st.session_state.portfolio[st.session_state.portfolio['Stock Symbol'] == stock_symbol].index[0]
                        existing_quantity = st.session_state.portfolio.at[index, 'Quantity']
                        
                        if quantity > existing_quantity:
                            st.error("Not enough stock in portfolio to sell the specified quantity.")
                            return 
                        new_quantity = existing_quantity - quantity
                        if new_quantity == 0:
                            st.session_state.portfolio.drop(index, inplace=True)
                        else:
                            existing_average_price = st.session_state.portfolio.at[index, 'Average Purchase Price']
                            existing_amount_invested = st.session_state.portfolio.at[index, 'Amount Invested'] - amount_invested_new_stock
                            #new_quantity = existing_quantity - quantity
                        #new_average_price = ((existing_average_price * existing_quantity) + (average_price * quantity)) / new_quantity
                        #new_amount_invested = existing_amount_invested - (quantity * average_price)
                            new_current_value = new_quantity * current_price
                            new_profit_loss = new_current_value - existing_amount_invested
                            new_profit_loss_percent = (new_profit_loss / existing_amount_invested) * 100 if existing_amount_invested != 0 else 0
                        
                            st.session_state.portfolio.at[index, 'Quantity'] = new_quantity
                        #st.session_state.portfolio.at[index, 'Average Purchase Price'] = new_average_price
                            st.session_state.portfolio.at[index, 'Current Price'] = current_price
                            st.session_state.portfolio.at[index, 'Current Value'] = new_current_value
                            st.session_state.portfolio.at[index, 'Amount Invested'] = existing_amount_invested
                            st.session_state.portfolio.at[index, 'Profit/ Loss'] = new_profit_loss
                            st.session_state.portfolio.at[index, 'Profit/ Loss %'] = new_profit_loss_percent
                    else:
                        st.error("Stock not found in portfolio.")
                        return
                        # if stock_symbol.endswith('.NS') or stock_symbol.endswith(".ns"): 
                        #     currency = 'INR'
                        # else:
                        #     currency = 'USD'  
                        # new_stock = pd.DataFrame([{
                        #     'Stock Symbol': stock_symbol, 
                        #     'Currency' : currency,
                        #     'Quantity': quantity, 
                        #     'Average Purchase Price': average_price,
                        #     'Date of Purchase': purchase_date, 
                        #     'Current Price': current_price, 
                        #     'Current Value': current_value_new_stock,
                        #     'Amount Invested': amount_invested_new_stock,
                        #     'Profit/ Loss': profit_loss_new_stock,
                        #     'Profit/ Loss %': profit_loss_percent_new_stock
                        # }])

                        # st.session_state.portfolio = pd.concat([st.session_state.portfolio, new_stock], ignore_index=True)

                st.session_state.portfolio = st.session_state.portfolio.copy()

                if sell_button:
                    sell_stock_from_portfolio(stock_symbol, quantity, average_price, purchase_date)

                usd_to_inr_rate = fetch_usd_to_inr_exchange_rate()

                def adjust_currency(row):
                    if row['Currency'] == 'USD':
                        row['Current Value INR'] = row['Current Value'] * usd_to_inr_rate
                        row['Amount Invested INR'] = row['Amount Invested'] * usd_to_inr_rate
                    else:
                        row['Current Value INR'] = row['Current Value']
                        row['Amount Invested INR'] = row['Amount Invested']
                    return row

                st.session_state.portfolio = st.session_state.portfolio.apply(adjust_currency, axis=1)

                # def sell_stock_from_portfolio(index, sell_quantity):
                #     stock = st.session_state.portfolio.loc[index]
                #     if sell_quantity >= stock['Quantity']:
                #         st.session_state.portfolio = st.session_state.portfolio.drop(index)
                #     else:
                #         st.session_state.portfolio.at[index, 'Quantity'] -= sell_quantity

                #     st.session_state.portfolio.reset_index(drop=True, inplace=True)

                # for index, row in st.session_state.portfolio.iterrows():
                #     cols = st.columns([0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.2, 0.1])
                #     cols[0].write(row['Stock Symbol'])
                #     cols[1].write(row['Quantity'])
                #     sell_quantity = cols[9].number_input('Sell Qty', min_value=0.01, max_value=float(row['Quantity']), step=0.01, format="%.2f", key=f"sell_{index}")
                #     if cols[9].button('Sell', key=f"sell_btn_{index}"):
                #         sell_stock_from_portfolio(index, sell_quantity)
                #     if cols[10].button('Sell All', key=f"sell_all_{index}"):
                #         sell_stock_from_portfolio(index, row['Quantity'])

                def calculate_current_value():
                    stock_values = {}
                    for _, row in st.session_state.portfolio.iterrows():
                        symbol = row['Stock Symbol']
                        quantity = row['Quantity']
                        stock_info = yf.Ticker(symbol)
                        try:
                            current_price = (stock_info.history(period='1d')['Close'][-1])
                            stock_values[symbol] = current_price * quantity
                        except IndexError:
                            st.error(f"Failed to fetch current price for {symbol}.")
                            continue
                    return stock_values

                def calculate_current_value_in_inr():
                    usd_to_inr_rate = fetch_usd_to_inr_exchange_rate()
                    stock_values_in_inr = {}
                    for _, row in st.session_state.portfolio.iterrows():
                        symbol = row['Stock Symbol']
                        quantity = row['Quantity']
                        currency = row['Currency']
                        stock_info = yf.Ticker(symbol)

                        try:
                            current_price_usd = stock_info.history(period='1d')['Close'][-1]
                            if currency == 'USD':
                                current_price_inr = current_price_usd * usd_to_inr_rate
                            else:
                                current_price_inr = current_price_usd 
                            stock_values_in_inr[symbol] = current_price_inr * quantity
                        except IndexError:
                            st.error(f"Failed to fetch current price for {symbol}.")
                            continue
                    return stock_values_in_inr

                st.write('Your Portfolio', st.session_state.portfolio)

                if not st.session_state.portfolio.empty:
                    total_value = st.session_state.portfolio['Current Value INR'].sum()
                    total_investment = st.session_state.portfolio['Amount Invested INR'].sum()
                    total_profit_loss = st.session_state.portfolio['Profit/ Loss'].sum()
                    if total_investment > 0:
                        total_profit_loss_percent = (total_profit_loss / total_investment) * 100
                    else:
                        total_profit_loss_percent = 0
                else:
                    total_value = 0
                    total_investment = 0
                    total_profit_loss = 0
                    total_profit_loss_percent = 0

                if not st.session_state.portfolio.empty:
                    stock_values = calculate_current_value_in_inr()
                    invested_amounts = st.session_state.portfolio.groupby('Stock Symbol')['Amount Invested INR'].sum()
                    if stock_values and not invested_amounts.empty:
                        labels_value = list(stock_values.keys())
                        values_value = list(stock_values.values())
                        labels_invested = invested_amounts.index.tolist()
                        values_invested = invested_amounts.values.tolist()
                        
                        # Create a subplot with 1 row and 2 columns
                        fig = make_subplots(rows=1, cols=2, specs=[[{'type': 'pie'}, {'type': 'pie'}]])
                        
                        # Add the first pie chart for Current Value
                        fig.add_trace(
                            go.Pie(labels=labels_value, values=values_value, hole=.6, title="Current Value INR"),
                            row=1, col=1
                        )
                        
                        # Add the second pie chart for Amount Invested
                        fig.add_trace(
                            go.Pie(labels=labels_invested, values=values_invested, hole=.6, title="Amount Invested INR"),
                            row=1, col=2
                        )
                        
                        # Update the layout to adjust the appearance
                        fig.update_layout(
                            title_text="Portfolio Distribution",
                            margin=dict(l=80, r=140, t=80, b=80),  # Reducing left (l) and right (r) margins
                            width=800,
                            annotations=[
                                dict(text='Distribution by Current Value', x=0.09, y=-0.1, font_size=14, showarrow=False),
                                dict(text='Distribution by Amount Invested', x=0.94, y=-0.1, font_size=14, showarrow=False)
                            ]
                        )

                        # # Update the layout to adjust the appearance and center the graph
                        # fig.update_layout(
                        #     title_text="Portfolio Distribution",
                        #     margin=dict(l=20, r=20, t=50, b=20),  # Reducing left (l) and right (r) margins
                        #     width=800  # Adjust this width to fit your Streamlit page layout
                        # )
                        
                        # Display the figure in Streamlit
                        st.plotly_chart(fig)
                    else:
                        st.write("Unable to calculate values for the stocks in your portfolio.")
                else:
                    st.write("Your portfolio is currently empty.")

            if selected == "Charts":
                def calculate_current_value_for_last_month_plotly(period='1mo',interval='1d'):
                    for _, row in st.session_state.portfolio.iterrows():
                        symbol = row['Stock Symbol']
                        stock_info = yf.Ticker(symbol)
                        try:
                            stock_history = stock_info.history(period=period, interval=interval)
                            fig = go.Figure()
                            fig.add_trace(go.Scatter(x=stock_history.index, y=stock_history['Close'], mode='lines', name=symbol))
                            fig.update_layout(title=f'Stock Price Overview of {symbol}',
                                            xaxis_title='Date',
                                            yaxis_title='Stock Price')
                            st.plotly_chart(fig)

                        except Exception as e:
                            st.error(f"Failed to fetch current price for {symbol}. Error: {e}")
                            continue

                period = st.radio('Select Period', ['1mo', '3mo', '1y','5y'], index=0, key='Stock Price Plot')

                st.markdown(
                    """
                    <style>
                    .stRadio > div[role="radiogroup"] {
                        display: flex;
                        flex-direction: row;
                        flex-wrap: wrap;
                    }

                    .stRadio > div[role="radiogroup"] > label {
                        flex: 1;
                        margin-right: 10px;
                    }
                    </style>
                    """,
                    unsafe_allow_html=True
                )

                if period == '1mo':
                    calculate_current_value_for_last_month_plotly(period,'1d')
                if period == '3mo':
                    calculate_current_value_for_last_month_plotly(period,'1wk')
                if period == '1y':
                    calculate_current_value_for_last_month_plotly(period,'1wk')
                if period == '5y':
                    calculate_current_value_for_last_month_plotly(period,'1mo')
                

            if selected == "P&L to Date":
                def profit_loss_bar_plot(symbol, initial_investment, period='1y'):
                    stock_info = yf.Ticker(symbol)
                    try:
                        # Retrieve stock history
                        stock_history = stock_info.history(period='10y')  # Get 5 years of data initially

                        if period == '1y':
                            # Resample to get the last 4 quarters
                            stock_history = stock_history['Close'].resample('Q').last()
                        elif period == '5y':
                            # Resample to get the last 5 years
                            stock_history = stock_history['Close'].resample('A').last()
                        elif period == '10y':
                            # Resample to get the last 10 years
                            stock_history = stock_history['Close'].resample('A').last()

                        # Calculate profit or loss
                        profit_loss = stock_history.diff() * initial_investment
                        #profit_loss = stock_history - initial_investment
                        color = ['green' if val > 0 else 'red' for val in profit_loss]



                        # Create and customize the figure
                        fig = go.Figure()
                        fig.add_trace(go.Bar(x=profit_loss.index, y=abs(profit_loss), name='Profit/Loss', marker_color=color))
                        fig.update_layout(title=f'Profit/Loss Overview for {symbol}',
                                        xaxis_title='Date',
                                        yaxis_title='Profit/Loss Amount',
                                        barmode='group')

                        return fig

                    except Exception as e:
                        st.error(f"Failed to plot Profit Loss Overview for {symbol}. Error: {e}")
                        return None

                # Streamlit app layout
                def main():
                    st.title("Stock Profit/Loss Analysis")

                    symbol = st.text_input("Enter Stock Symbol", value='AAPL')
                    initial_investment = st.number_input("Amount Invested", value=150.0)

                    # Select period for analysis
                    period = st.radio('Select Period', ['1y', '5y', '10y'], index=0)

                    # Inline style for radio buttons
                    st.markdown(
                        """
                        <style>
                        .stRadio > div[role="radiogroup"] {
                            display: flex;
                            flex-direction: row;
                            flex-wrap: nowrap;
                            justify-content: flex-start;
                        }
                        .stRadio > div[role="radiogroup"] > label {
                            flex: 1;
                            margin-right: 10px;
                            white-space: nowrap;
                        }
                        </style>
                        """,
                        unsafe_allow_html=True
                    )

                    # Button to trigger the plot
                    if st.button('Analyze'):
                        fig = profit_loss_bar_plot(symbol, initial_investment, period)
                        if fig:
                            st.plotly_chart(fig)

                if __name__ == "__main__":
                    main()

            if selected == "Widgets":
                stock_name = st.text_input("Stock Name", "INFY")

                # Define the HTML content with the widget
                html_content = f"""
                <blockquote class="trendlyne-widgets" data-get-url="https://trendlyne.com/web-widget/technical-widget/Poppins/{stock_name}/?posCol=00A25B&primaryCol=006AFF&negCol=EB3B00&neuCol=F7941E" data-theme="light"></blockquote>
                <script async src="https://cdn-static.trendlyne.com/static/js/webwidgets/tl-widgets.js" charset="utf-8"> </script>
                """

                html_content4 = f"""
                <blockquote class="trendlyne-widgets" data-get-url="https://trendlyne.com/web-widget/swot-widget/Poppins/{stock_name}/?posCol=00A25B&primaryCol=006AFF&negCol=EB3B00&neuCol=F7941E" data-theme="light"></blockquote><script async src="https://cdn-static.trendlyne.com/static/js/webwidgets/tl-widgets.js" charset="utf-8"> </script>
                """

                html_content3 = f"""
                <blockquote class="trendlyne-widgets" data-get-url="https://trendlyne.com/web-widget/qvt-widget/Poppins/{stock_name}/?posCol=00A25B&primaryCol=006AFF&negCol=EB3B00&neuCol=F7941E" data-theme="light"></blockquote><script async src="https://cdn-static.trendlyne.com/static/js/webwidgets/tl-widgets.js" charset="utf-8"> </script>
                """

                html_content2 = f"""
                <blockquote class="trendlyne-widgets" data-get-url="https://trendlyne.com/web-widget/checklist-widget/Poppins/{stock_name}/?posCol=00A25B&primaryCol=006AFF&negCol=EB3B00&neuCol=F7941E" data-theme="light"></blockquote><script async src="https://cdn-static.trendlyne.com/static/js/webwidgets/tl-widgets.js" charset="utf-8"> </script>
                """





                def main():
                    st.title("Dashboard with Trendlyne Widget")

                    # Layout with 3 columns (adjust number of columns as needed)
                    col1, col2 = st.columns(2)

                    # Using the first column for the Trendlyne widget
                    with col1:
                        st.title("Stock Technicals")
                        st.components.v1.html(html_content, height=600, scrolling=True)

                    # You can use other columns for different content
                    with col2:
                        st.title("Stock Checklist")
                        st.components.v1.html(html_content2, height=600, scrolling=True)


                    col3, col4 = st.columns(2)

                    with col3:
                        st.title("QVT Score")
                        st.components.v1.html(html_content3, height=600, scrolling=True)


                    with col4:
                        st.title("SWOT Analysis")
                        st.components.v1.html(html_content4, height=600, scrolling=True)


                if __name__ == "__main__":
                    main()

            if selected == "FinBot":
                api_key = st.secrets["OPENAI_API_KEY"]
                client = OpenAI(api_key=api_key)
                def chat_with_gpt(prompt):
                    response = client.chat.completions.create(
                        model="gpt-4-turbo",
                        messages=[
                            {"role": "system", "content": "Hello! I'm your Finance Bot, an expert in stock market analysis. "
                                                        "I specialize in detailed technical and fundamental analysis to provide precise insights. "
                                                        "Whether you need help understanding stock charts, predicting upcoming market trends, "
                                                        "analyzing company financials, or seeking personalized investment strategies, I'm here to assist. "
                                                        "Please tell me about your current financial interests or ask a question directly related to your investment needs."},
                            {"role": "user", "content": prompt}
                        ]
                    )
                    return response.choices[0].message.content.strip()

                def main():
                    st.title('Finance Chatbot with OpenAI GPT')
                    user_input = st.text_input("Enter your question:", placeholder="Ask me about stocks, market trends, etc.")
                    if st.button('Submit'):
                        with st.spinner('Generating response...'):
                            response = chat_with_gpt(user_input)
                            st.write("Chatbot:", response)
                if __name__ == "__main__":
                    main()

            if selected == "Price Predictor":
                def main():
                    st.title("Future Price Predictor")

                    # Input selection
                    custom_today = st.date_input("Select a custom 'today' date:", date.today())
                    custom_stocks = st.text_input("Enter custom stock name (in format of Yahoo Finance like RELIANCE.NS or select from below select box):")
                    stocks = custom_stocks.split(',') if custom_stocks else ['^NYFANG', 'RELIANCE.NS', 'TATAMOTORS.NS', 'KPITTECH.NS', 'TATAPOWER.NS', 'TITAN.NS', 'BTC-USD']
                    selected_stock = st.selectbox('Select Stock:', stocks)
                    n_years = st.slider("Years of prediction:", 1, 5)
                    period = n_years * 365
                    START = "2011-01-01"

                    @st.cache_data
                    def load_data(ticker, custom_today):
                        data = yf.download(ticker, START, custom_today.strftime("%Y-%m-%d"))
                        data.reset_index(inplace=True)
                        return data

                    # Load data
                    data_load_state = st.text("Loading data...")
                    data = load_data(selected_stock, custom_today)
                    data_load_state.text("Data Loaded!")

                    df_train = data[['Date', 'Close']]
                    df_train = df_train.rename(columns={"Date": "ds", "Close": "y"})
                    m = Prophet()
                    m.fit(df_train)
                    future = m.make_future_dataframe(periods=int(period))
                    forecast = m.predict(future)

                    # Calculate and display prediction limits
                    last_date = forecast['ds'].iloc[-1]
                    last_yhat_lower = forecast['yhat_lower'].iloc[-1]
                    last_yhat_upper = forecast['yhat_upper'].iloc[-1]
                    col3, col4, col5 = st.columns(3)
                    col3.markdown(f"Predicted Price Range for {last_date.date()}:")
                    col4.metric("Lower Estimate:", f"{last_yhat_lower:.2f}")
                    col5.metric(" Upper Estimate:", f"{last_yhat_upper:.2f}")
                    
                    # st.markdown(f"### Predicted Price Range for {last_date.date()}:")
                    # st.markdown(f"#### Lower Estimate: ${last_yhat_lower:.2f}")
                    # st.markdown(f"#### Upper Estimate: ${last_yhat_upper:.2f}")

                    # Plotting raw data
                    st.subheader('Raw data')
                    st.write(data.tail())

                    def plot_raw_data(data):
                        fig = go.Figure()
                        fig.add_trace(go.Scatter(x=data['Date'], y=data['Open'], name='stock_open', line=dict(color='red')))
                        fig.add_trace(go.Scatter(x=data['Date'], y=data['Close'], name='stock_close', line=dict(color='green')))
                        fig.update_layout(title_text="Time Series Data", xaxis_rangeslider_visible=True)
                        st.plotly_chart(fig)
                    plot_raw_data(data)

                    # Display forecast
                    st.subheader('Forecast data')
                    st.write(forecast.tail())
                    fig1 = plot_plotly(m, forecast)
                    st.plotly_chart(fig1)

                if __name__ == "__main__":
                    main()

            if selected == "Financial Statement":
                # Function to convert DataFrame values to crores
                def convert_to_crores(df):
                    return df.apply(lambda x: x / 10000000)

                def main():
                    st.title('Financial Statement Viewer')

                    ticker_symbol = st.text_input('Enter the Stock Ticker Symbol (e.g., RELIANCE.NS)', 'RELIANCE.NS')
                    st.text('Note: For Indian stocks, use the ".NS" extension. For US stocks, use the stock symbol only.')
                    st.text('For example, for Reliance Industries, use "RELIANCE.NS" and for Apple Inc., use "AAPL"')
                    st.text('For a list of stock symbols, visit https://in.finance.yahoo.com/ or https://finance.yahoo.com/')
                    st.text("All data is in Crores of Indian Rupees (INR) or US Dollars (USD) as applicable.")
                    st.write('You entered:', ticker_symbol)
                    data_frequency = st.radio("Select Data Frequency", ('Annual', 'Quarterly'))

                    def fetch_financials(ticker_symbol, period='annual'):
                        ticker_symbol = yf.Ticker(ticker_symbol)
                        if period == 'annual':
                            financials = ticker_symbol.financials
                            period_label = 'Annual'
                        else:  # quarterly
                            financials = ticker_symbol.quarterly_financials
                            period_label = 'Quarterly'
                        
                        return financials, period_label

                    # Function to plot financials using Plotly
                    def plot_financials(financials, period_label, ticker_symbol):
                        # Convert to DataFrame and clean data
                        df = financials.T
                        df.index = pd.to_datetime(df.index).date

                        fig = go.Figure()
                        # Adding traces for significant P&L items
                        for column in df.columns:
                            fig.add_trace(go.Bar(x=df.index, y=df[column], name=column))

                        # Update the layout
                        fig.update_layout(
                            title=f'{period_label} Profit and Loss Statement for {ticker_symbol}',
                            xaxis_title='Period',
                            yaxis_title='Amount',
                            barmode='group',
                            legend_title_text='P&L Items'
                        )
                        
                        return fig
                    
                    def fetch_gross_profit(ticker_symbol, period='quarterly'):
                        ticker = yf.Ticker(ticker_symbol)
                        # Fetch the annual or quarterly financial statements as per the user's choice
                        if period == 'quarterly':
                            financials = ticker.quarterly_financials
                        else:
                            financials = ticker.financials
                        # Extract Gross Profit
                        gross_profit = financials.loc['Gross Profit'] if 'Gross Profit' in financials.index else None
                        return gross_profit

                    def plot_gross_profit(ticker_symbol, gross_profit, period):
                        # Create a bar chart
                        fig = go.Figure()
                        fig.add_trace(go.Bar(x=gross_profit.index, y=gross_profit.values, name='Gross Profit'))
                        fig.update_layout(
                            title=f'Gross Profit of {ticker_symbol} ({period})',
                            xaxis_title='Period',
                            yaxis_title='Gross Profit',
                            xaxis={'type': 'category'},
                        )
                        return fig

                    # Streamlit app layout
                    def main():

                        # Display financials
                        if st.button('Fetch Financials'):
                            financials, period_label = fetch_financials(ticker_symbol, data_frequency)
                            gross_profit = fetch_gross_profit(ticker_symbol, period=data_frequency)
                            if gross_profit is not None and not gross_profit.empty:
                                fig = plot_gross_profit(ticker_symbol, gross_profit, period=data_frequency)
                                st.plotly_chart(fig)
                            else:
                                st.error("Failed to fetch Gross Profit data. Check the stock ticker_symbol or data availability.")
                            if financials is not None:
                                fig = plot_financials(financials, period_label, ticker_symbol)
                                st.plotly_chart(fig)
                            tickerData = yf.Ticker(ticker_symbol)
                            if data_frequency == 'Annual':
                                balance_sheet = convert_to_crores(tickerData.balance_sheet)
                                income_statement = convert_to_crores(tickerData.financials)
                                cash_flow = convert_to_crores(tickerData.cashflow)
                            else:
                                balance_sheet = convert_to_crores(tickerData.quarterly_balance_sheet.iloc[:, :5])
                                income_statement = convert_to_crores(tickerData.quarterly_financials.iloc[:, :5])
                                cash_flow = convert_to_crores(tickerData.quarterly_cashflow.iloc[:, :5])

                            def convert_df_to_csv(data):
                                return data.to_csv().encode('utf-8')

                            def display_and_download_data(title, data):
                                st.write(title)
                                st.dataframe(data)
                                csv = convert_df_to_csv(data)
                                st.download_button(label=f"Download {title} as CSV",data=csv,file_name=f"{title.lower().replace(' ', '_')}_last_5_quarters_crores.csv",mime='text/csv')

                            display_and_download_data("Balance Sheet", balance_sheet)
                            display_and_download_data("Income Statement", income_statement)
                            display_and_download_data("Cash Flow Statement", cash_flow)
                    if __name__ == "__main__":
                        main()
                if __name__ == "__main__":
                        main()
conn.close()            
