**ProfitOlio - Portfolio Management System**

ProfitOlio is a comprehensive finance application built using Streamlit, designed to offer robust tools for portfolio management. It features a sophisticated financial chatbot (FinBot), future price prediction capabilities, and various visualizations to assist users in managing their investments effectively. It also includes a viewer for detailed financial statements.


**Table of Contents**

1. Portfolio Management System
2. Charts
3. Indian Market Overview
4. FinBot
5. P&L to Date
6. Stock Metrics
7. Price Predictor
8. Financial Statement Viewer
9. Widgets
8. Installation and Usage
9. Demo

**Portfolio Management System**

	This module enables users to manage their stock portfolio comprehensively. Users can track investments, calculate profits or losses, and visualize how their investments are distributed.

**Features**

- Add stocks to the portfolio, including US stocks and cryptocurrencies.

- Monitor the current value, total amount invested, and profit or loss on investments.

- Sell stocks either partially or completely.

- Convert investments from USD to INR for accurate tracking.

- Employ pie charts for a 
visual breakdown of portfolio distribution.

**Features**


**Charts**

	Offer detailed visual representations of stock trends and profitability within the user’s portfolio.

**Features**

- Track and visualize historical stock prices over various periods (30 days, 3 months, 1 year, or 5 years).
- Display annual (Year-over-Year) or quarterly (Quarter-over-Quarter) gross profit of the stocks.

**Indian Market Overview**

	This module provides a daily overview of major Indian stock indices, including Nifty50 and Sensex. It Forms a 5-min live candlestick chart for the Indian indices, displaying the day's high, low, open, and current levels.

**Features**

- Give a daily overview of major Indian Stock Indices; Nifty50 and Sensex. 
- Forms a 5-min live candlestick for the Indian Indices and show their Day's High, Low and Open as well as current levels.

**FinBot**

	FinBot is a finance chatbot powered by OpenAI GPT, providing insights into stock market analysis, company financials, and personalized investment strategies.

**Features**

- Interact with the bot to get analyses of stock market trends.
- Obtain detailed technical and fundamental analysis.

**P&L to Date**

	Utilizes Yahoo Finance and Plotly to visualize the profit/loss of a company based on the amount invested over the last 10 years.

**Features**

- Check the profit or loss of a company for any amount invested up to the last 10 years.

**Stock Metrics**

	Give certain important metrics like Beta, CAGR Var of stocks.

**Features**

- Calculates different stock metrics like Beta, CAGR, VaR etc and then show charts as well as provide information on them.

**Price Predictor**

	The Price Predictor uses Prophet to forecast future stock prices based on historical data.

**Features**

- Predict stock prices for up to 5 years.
- Visualize historical and forecasted stock prices.
- Customize the date input for the current day.
- Select from multiple stock options.

**Financial Statement Viewer**

	This viewer provides annual or quarterly financial statements of stocks in a user-friendly format.

**Features**

- View and download balance sheets, income statements, and cash flow statements.
- Obtain detailed graphs for gross profit QoQ and YoY, as well as a chart showing all financial metrics with an option to choose one.
- Data in crores of Indian Rupees (INR) or US Dollars (USD).
- Supports both Indian and US stock symbols.

**Widgets**

	Provides widgets for Indian Stocks, including:

	- Technicals
	- Checklist
	- QVT Score
	- SWOT Analysis

**Features**

- Generate widgets of Indian stocks based on input, assisted by Trendlyne.

**Installation and Usage**

1. Clone the repository:

    ```bash
    git clone https://github.com/harshsinha-12/ProfitOlio.git
    cd ProfitOlio
    ```

2. Install the required dependencies:

    ```bash
    pip install -r requirements.txt
    ```

3. Run the application:

    ```bash
    streamlit run main.py
    ```

**Demo**

- View the live app: [ProfitOlio](https://profitolio.streamlit.app/)
- Watch the YouTube Demo: [YouTube](https://youtu.be/54Zx-F9pf7A)

![ProfitOlio Stage - 2 Demo Screen Recording for Project Demonstration](https://github.com/harshsinha-12/ProfitOlio/blob/main/Stage-2Screenshot.png)