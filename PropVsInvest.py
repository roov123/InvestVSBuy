import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px

st.set_page_config(layout="wide")
st.info("👈 Use the sidebar to enter your assumptions. Adjust the values to see real-time updates.")


def calculate_mortgage(loan_amount, interest_rate, loan_term):
    monthly_rate = interest_rate / 12
    num_payments = loan_term * 12
    if monthly_rate > 0:
        mortgage_payment = (loan_amount * monthly_rate) / (1 - (1 + monthly_rate) ** -num_payments)
    else:
        mortgage_payment = loan_amount / num_payments
    return round(mortgage_payment, 2)

def property_vs_investment(own_params, rent_params, invest_params, savings_params, years=20):
    years_range = np.arange(1, years + 1)

    # Owner-Occupied Property
    own_cashflow = np.zeros(years)
    own_equity = np.zeros(years)
    inv_equity = np.zeros(years)
    loan_balance = own_params['loan_amount']
    other_exp=np.zeros(years)
    family_inc=np.zeros(years)
    
    for i in range(years):
        interest = loan_balance * own_params['interest_rate']
        principal = own_params['mortgage_payment']*12 - interest
        loan_balance -= principal
        other_exp[i]=own_params['other_expenses']* ((1 + 0.04) ** (i + 1))
        family_inc[i]=own_params['family_income']* ((1 + 0.04) ** (i + 1))
        own_cashflow[i] = family_inc[i]-other_exp[i]-own_params['mortgage_payment'] - own_params['expenses']
        own_equity[i] = own_params['property_price'] * ((1 + own_params['appreciation_rate']) ** (i + 1)) - loan_balance

    # Investment Property
    rent_cashflow = np.zeros(years)
    rent_equity = np.zeros(years)
    loan_balance = rent_params['loan_amount']
    for i in range(years):
        rent_exp = invest_params['rental_expense'] * (1 + rent_params['rent_growth']) ** i
        rent_income = rent_params['rental_income'] * (1 + rent_params['rent_growth']) ** i
        interest = loan_balance * rent_params['interest_rate']
        principal = rent_params['mortgage_payment']*12 - interest
        loan_balance -= principal
        other_exp[i]=own_params['other_expenses']* ((1 + 0.04) ** (i + 1))
        family_inc[i]=own_params['family_income']* ((1 + 0.04) ** (i + 1))
        rent_cashflow[i] = family_inc[i]-other_exp[i]+rent_income-rent_exp - rent_params['expenses'] - rent_params['mortgage_payment']
        
        rent_equity[i] = rent_params['property_price'] * ((1 + rent_params['appreciation_rate']) ** (i + 1)) - loan_balance

    # Investment Portfolio
    invest_cashflow = np.zeros(years)
    invest_balance = invest_params['initial_investment']
    savings_balance = 0
    monthly_savings = savings_params['monthly_savings']
    for i in range(years):
        rent_exp = invest_params['rental_expense'] * (1 + rent_params['rent_growth']) ** i
        invest_balance *= (1 + invest_params['return_rate']/100)
        savings_balance = (savings_balance + (monthly_savings * 12)) * (1 + invest_params['return_rate']/100)
        other_exp[i]=own_params['other_expenses']* ((1 + 0.04) ** (i + 1))
        family_inc[i]=own_params['family_income']* ((1 + 0.04) ** (i + 1))
        invest_cashflow[i] = family_inc[i]-other_exp[i]-rent_exp
        inv_equity[i] = invest_balance+savings_balance
        

    # DataFrames
    df_cashflow = pd.DataFrame({
        'Year': years_range,
       # 'Owner-Occupied Cashflow': own_cashflow.cumsum(),
       # 'Rental Property Cashflow': rent_cashflow.cumsum(),
        'Owner-Occupied Cashflow': own_cashflow,
        'Rental Property Cashflow': rent_cashflow,
        'Investment Portfolio Value (Incl. Savings)': invest_cashflow
    })

    df_equity = pd.DataFrame({
        'Year': years_range,
        'Scenario 1:Buy home': own_equity,
        'Scenario 2:Buy property investment': rent_equity,
        'Scenario 3:Invest': inv_equity
    })

    return df_cashflow, df_equity

# Streamlit UI
st.title("🏡 Property vs Investing Analysis 📈")
st.sidebar.header("📊 Assumptions")

# Inputs
#--------------------------------------------------------------------------------------------
st.sidebar.subheader("🏡 Your financial position")
family_income= st.sidebar.number_input("What is your monthly family take home income ($)", value=12000, step=200)
current_rent=st.sidebar.number_input("What is your current monthly rent ($)", value=4000, step=200)
monthly_savings=st.sidebar.number_input("What is your monthly family savings after expenses ($)", value=3000, step=200)

assets = st.sidebar.number_input("What is your total investable asset base ($)", value=500000, step=10000)
use_all_assets = st.sidebar.checkbox("Use all assets for property investment")

if use_all_assets:
    property_budget = assets
else:
    property_budget = st.sidebar.number_input("How much are you prepared to invest in property (deposit + upfront costs)?", value=200000, step=10000, min_value=0, max_value=assets)


investible_assets=assets-property_budget


#--------------------------------------------------------------------------------------------------------
st.sidebar.subheader("🏡 Costs of buying property")
# Sidebar for Property Costs

with st.sidebar.expander("Upfront Costs" , expanded=False):
    stamp_duty = st.number_input("Stamp Duty ($)", value=20000, step=1000, min_value=0)
    conveyancer_fees = st.number_input("Conveyancer Fees ($)", value=2000, step=500, min_value=0)
    inspection_fees = st.number_input("Inspections (Building & Pest) ($)", value=1000, step=500, min_value=0)

    # Total upfront costs
    upfront_costs = stamp_duty + conveyancer_fees + inspection_fees
    deposit=property_budget-upfront_costs
    st.write(f"### Total Upfront Costs: ${upfront_costs}")

with st.sidebar.expander("Ongoing monthly costs" , expanded=False):
    build_insurance = st.number_input("Building insurance ($)", value=200, step=10, min_value=0)
    strata_fees = st.number_input("Strata Fees ($)", value=200, step=10, min_value=0)
    council_fees = st.number_input("Council rates ($)", value=50, step=5, min_value=0)

    # Total ongoing monthly costs
    ongoing_costs = build_insurance + strata_fees + council_fees
    st.write(f"### Total ongoing monthly costs: ${ongoing_costs}")

with st.sidebar.expander("Mortgage costs" , expanded=False):
    property_price= st.number_input("Purchase price ($)", value=800000,step = 50000,format="%d")
    loan_amount=property_price-deposit
    st.number_input("Deposit:", value=deposit, disabled=True)
    st.number_input("Loan Amount ($):", value=loan_amount, disabled=True)
    interest_rate = st.number_input("Loan Interest Rate (%)", value=5.0) / 100
    mortgage_payment=calculate_mortgage(loan_amount, interest_rate, 30)
    st.number_input("Monthly Mortgage ($):", value=mortgage_payment, disabled=True)
    #mortgage_payment = st.sidebar.number_input("Monthly Mortgage Payment ($)", value=4000,format="%d")


st.sidebar.subheader("🏡 Other assumptions")
investment_return = st.sidebar.number_input("Expected Investment Return (%) on alternative assets", value=7.0, step=0.1)
rent_investment_prop=st.sidebar.number_input("Monthly rental income on investment property ($)", value=3000,format="%d")
rent_growth = st.sidebar.number_input("Annual Rent Growth (%)", value=2.0) / 100
appreciation_rate = st.sidebar.number_input("Annual Property Appreciation (%)", value=3.0) / 100
other_expenses=family_income-current_rent-monthly_savings

 

# Define parameters
own_params = {
    'property_price': property_price,
    'loan_amount': loan_amount,
    'interest_rate': interest_rate,
    'mortgage_payment': mortgage_payment,
    'expenses': ongoing_costs,
    'appreciation_rate': appreciation_rate,
    'other_expenses':other_expenses,
    'family_income':family_income
}

rent_params = {
    'property_price': property_price,
    'loan_amount': loan_amount,
    'interest_rate': interest_rate,
    'mortgage_payment': mortgage_payment,
    'expenses': ongoing_costs,
    'rental_income': rent_investment_prop,
    'rent_growth': rent_growth,
    'appreciation_rate': appreciation_rate
}

invest_params = {
    'initial_investment': assets,
    'return_rate': investment_return,
    'rental_expense':current_rent
}

savings_params = {
    'monthly_savings': monthly_savings
}

# Run Simulation
df_cashflow, df_equity = property_vs_investment(own_params, rent_params, invest_params, savings_params)

# Display Results


# Create a Plotly figure
st.subheader("📊 Equity Growth Over Time")

df_equity_long = df_equity.melt(id_vars=["Year"], var_name="Scenario", value_name="Equity Value")
#fig = px.area(df_equity_long, x="Year", y="Equity Value", color="Scenario",
   #           title="Total Equity Accumulation",
    #          labels={"Equity Value": "Equity ($)", "Year": "Years"},
      #        template="seaborn")




fig = px.bar(df_equity_long, x="Year", y="Equity Value", color="Scenario",
             title="Yearly Equity Growth",
             labels={"Equity Value": "Equity ($)", "Year": "Years"},
             template="seaborn",
             barmode="group")
fig.update_layout(width=1000)  # Increase width for readability
fig.update_layout(autosize=True)
fig.update_layout(
    legend=dict(
        orientation="h",  # Makes the legend horizontal
        yanchor="top",  # Aligns the legend to the top of its position
        y=-0.3,  # Moves it below the x-axis
        xanchor="center",  # Centers the legend
        x=0.5  # Places it in the middle
    )
)






st.plotly_chart(fig, use_container_width=True)

st.subheader("Cashflow Table")
st.dataframe(df_cashflow)

st.subheader("Equity Table")
st.dataframe(df_equity)




# Create a Plotly figure
#st.subheader("📊 Equity Growth Over Time")

#df_equity_long = df_equity.melt(id_vars=["Year"], var_name="Scenario", value_name="Equity Value")

#fig = px.line(df_equity_long, x="Year", y="Equity Value", color="Scenario",
              #title="Equity Growth Over Time",
              #labels={"Equity Value": "Equity ($)", "Year": "Years"},
             # template="plotly_dark")

#st.plotly_chart(fig, use_container_width=True)



#fig = px.bar(df_equity_long, x="Year", y="Equity Value", color="Scenario",
 #            title="Yearly Equity Growth",
 #            labels={"Equity Value": "Equity ($)", "Year": "Years"},
 #            template="seaborn")

#st.plotly_chart(fig, use_container_width=True)



