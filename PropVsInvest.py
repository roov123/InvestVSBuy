import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def property_vs_investment(own_params, rent_params, invest_params, savings_params, years=20):
    years_range = np.arange(1, years + 1)

    # Owner-Occupied Property
    own_cashflow = np.zeros(years)
    own_equity = np.zeros(years)
    loan_balance = own_params['loan_amount']
    for i in range(years):
        interest = loan_balance * own_params['interest_rate']
        principal = own_params['mortgage_payment'] - interest
        loan_balance -= principal
        own_cashflow[i] = -own_params['mortgage_payment'] - own_params['expenses']
        own_equity[i] = own_params['property_price'] * ((1 + own_params['appreciation_rate']) ** (i + 1)) - loan_balance

    # Investment Property
    rent_cashflow = np.zeros(years)
    rent_equity = np.zeros(years)
    loan_balance = rent_params['loan_amount']
    for i in range(years):
        rent_income = rent_params['rental_income'] * (1 + rent_params['rent_growth']) ** i
        interest = loan_balance * rent_params['interest_rate']
        principal = rent_params['mortgage_payment'] - interest
        loan_balance -= principal
        net_cashflow = rent_income - rent_params['expenses'] - rent_params['mortgage_payment']
        rent_cashflow[i] = net_cashflow
        rent_equity[i] = rent_params['property_price'] * ((1 + rent_params['appreciation_rate']) ** (i + 1)) - loan_balance

    # Investment Portfolio
    invest_cashflow = np.zeros(years)
    invest_balance = invest_params['initial_investment']
    savings_balance = 0
    monthly_savings = savings_params['monthly_savings']
    for i in range(years):
        invest_balance *= (1 + invest_params['return_rate'])
        savings_balance = (savings_balance + (monthly_savings * 12)) * (1 + invest_params['return_rate'])
        invest_cashflow[i] = invest_balance + savings_balance

    # DataFrames
    df_cashflow = pd.DataFrame({
        'Year': years_range,
        'Owner-Occupied Cashflow': own_cashflow.cumsum(),
        'Rental Property Cashflow': rent_cashflow.cumsum(),
        'Investment Portfolio Value (Incl. Savings)': invest_cashflow
    })

    df_equity = pd.DataFrame({
        'Year': years_range,
        'Equity in Owned Property': own_equity,
        'Equity in Rental Property': rent_equity,
        'Investment Portfolio Value': invest_cashflow
    })

    return df_cashflow, df_equity

# Streamlit UI
st.title("Property vs Investing Analysis")

# Inputs
st.sidebar.header("Property & Investment Assumptions")
property_price = st.sidebar.number_input("Property Price ($)", value=800000)
loan_amount = st.sidebar.number_input("Loan Amount ($)", value=600000)
interest_rate = st.sidebar.number_input("Loan Interest Rate (%)", value=5.0) / 100
mortgage_payment = st.sidebar.number_input("Annual Mortgage Payment ($)", value=40000)
expenses = st.sidebar.number_input("Annual Expenses ($)", value=5000)
appreciation_rate = st.sidebar.number_input("Annual Property Appreciation (%)", value=3.0) / 100

rental_income = st.sidebar.number_input("Annual Rental Income ($)", value=30000)
rent_growth = st.sidebar.number_input("Annual Rent Growth (%)", value=2.0) / 100

initial_investment = st.sidebar.number_input("Initial Investment in Portfolio ($)", value=200000)
return_rate = st.sidebar.number_input("Annual Investment Return (%)", value=7.0) / 100
monthly_savings = st.sidebar.number_input("Monthly Additional Savings ($)", value=1000)

# Define parameters
own_params = {
    'property_price': property_price,
    'loan_amount': loan_amount,
    'interest_rate': interest_rate,
    'mortgage_payment': mortgage_payment,
    'expenses': expenses,
    'appreciation_rate': appreciation_rate
}

rent_params = {
    'property_price': property_price,
    'loan_amount': loan_amount,
    'interest_rate': interest_rate,
    'mortgage_payment': mortgage_payment,
    'expenses': expenses,
    'rental_income': rental_income,
    'rent_growth': rent_growth,
    'appreciation_rate': appreciation_rate
}

invest_params = {
    'initial_investment': initial_investment,
    'return_rate': return_rate
}

savings_params = {
    'monthly_savings': monthly_savings
}

# Run Simulation
df_cashflow, df_equity = property_vs_investment(own_params, rent_params, invest_params, savings_params)

# Display Results


st.subheader("Equity Growth Over Time")
st.line_chart(df_equity.set_index("Year"))

st.subheader("Cashflow Table")
st.dataframe(df_cashflow)

st.subheader("Equity Table")
st.dataframe(df_equity)
