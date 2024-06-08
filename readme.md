**ProfitOlio - Portfolio Management System**

This project is a multifunctional finance application built using Streamlit, offering a portfolio management system, a financial chatbot (FinBot), a future price predictor, with various visualizations to aid the user and a financial statement viewer.

**Major Contributors:**

- Harsh Sinha
- Sahil Advani
- Aditya Anshu
- Sandip Bala
- Deepak Ashok Modi

**Table of Contents**

1. Portfolio Management System
2. Charts
3. FinBot
4. P&L to Date
5. Price Predictor
6. Financial Statement Viewer
7. Widgets
8. Installation and Usage
9. Demo

**Portfolio Management System**

	This module allows users to manage their stock portfolio, track investments, calculate profits/losses, and visualize portfolio distribution.

**Features**

- Add stocks, including US stocks and cryptocurrencies, to the portfolio.
- View current value, amount invested, and profit/loss.
- Sell stocks partially or completely.
- Convert USD investments to INR.
- Visualize portfolio distribution with pie charts.

**Charts**

	This feature creates charts based on the stocks added to the portfolio, displaying price trends as well as gross profit.

**Features**

- Visualize historical stock prices for the last 30 days, 3 months, 1 year, or 5 years.
- Visualize annual (YoY) or quarterly (QoQ) gross profit of the stocks/companies.

**FinBot**

	FinBot is a finance chatbot powered by OpenAI GPT, providing insights into stock market analysis, company financials, and personalized investment strategies.

**Features**

- Interact with the bot to get analyses of stock market trends.
- Obtain detailed technical and fundamental analysis.

**P&L to Date**

	Utilizes Yahoo Finance and Plotly to visualize the profit/loss of a company based on the amount invested over the last 10 years.

**Features**

- Check the profit or loss of a company for any amount invested up to the last 10 years.

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
- Watch the YouTube Demo: [YouTube](https://youtu.be/5G_8I19g_-Q)

![ProfitOlio Stage - 2 Demo Screen Recording for Project Demonstration](https://github.com/harshsinha-12/ProfitOlio/blob/main/Stage-2Screenshot.png)