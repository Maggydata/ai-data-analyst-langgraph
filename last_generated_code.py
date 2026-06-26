import sys
import pandas as pd
import plotly.express as px

# Read CSV with encoding fallback
file_path = sys.argv[1]
try:
    df = pd.read_csv(file_path, encoding='utf-8')
except UnicodeDecodeError:
    df = pd.read_csv(file_path, encoding='latin-1')

# Parse date columns
df['Order Date'] = pd.to_datetime(df['Order Date'])
df['Ship Date'] = pd.to_datetime(df['Ship Date'])

# Analysis 0: Sales and Profit Trend Over Time
sales_profit_time = df.groupby('Order Date', as_index=False).agg({'Sales':'sum', 'Profit':'sum'})
fig0 = px.line(sales_profit_time, x='Order Date', y=['Sales', 'Profit'],
               title='Sales and Profit Trend Over Time',
               labels={'value':'Amount', 'Order Date':'Order Date', 'variable':'Metric'})
fig0.write_json('fig0.json')

# Analysis 1: Profitability by Product Category
profit_by_category = df.groupby('Category', as_index=False)['Profit'].sum().sort_values(by='Profit', ascending=False)
fig1 = px.bar(profit_by_category, x='Category', y='Profit',
              title='Profitability by Product Category',
              labels={'Profit':'Total Profit', 'Category':'Product Category'})
fig1.write_json('fig1.json')

# Analysis 2: Sales Distribution Across Customer Segments
sales_by_segment = df.groupby('Segment', as_index=False)['Sales'].sum().sort_values(by='Sales', ascending=False)
fig2 = px.bar(sales_by_segment, x='Segment', y='Sales',
              title='Sales Distribution Across Customer Segments',
              labels={'Sales':'Total Sales', 'Segment':'Customer Segment'})
fig2.write_json('fig2.json')

# Analysis 3: Relationship Between Discount and Profit
fig3 = px.scatter(df, x='Discount', y='Profit',
                  title='Relationship Between Discount and Profit',
                  labels={'Discount':'Discount Level', 'Profit':'Profit'})
fig3.write_json('fig3.json')

# Analysis 4: Sales Breakdown by Region
sales_by_region = df.groupby('Region', as_index=False)['Sales'].sum()
fig4 = px.pie(sales_by_region, names='Region', values='Sales',
              title='Sales Breakdown by Region')
fig4.write_json('fig4.json')
