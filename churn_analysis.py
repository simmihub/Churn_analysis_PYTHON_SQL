import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import sqlite3

# Excel file path
excel_file = 'C:\\Users\\simmi\\OneDrive\\Documents\\\\churn_analysis_n_cus_intelligence_PROJECT\\\\customer_churn_data_raw.xlsx'

# Create SQLite database connection
conn = sqlite3.connect('customer_churn.db')

# Read all sheet names from Excel file
excel_data = pd.ExcelFile(excel_file)

# Loop through each sheet and store as separate table
for sheet in excel_data.sheet_names:
    df = pd.read_excel(excel_file, sheet_name=sheet) # Read sheet into dataframe
    # Write dataframe to SQLite table
    df.to_sql(
        name=sheet,          # Table name = Sheet name
        con=conn,
        if_exists='replace', # Replace table if already exists
        index=False
    )

# Close connection
conn.close()

print("All sheets successfully converted into SQLite tables.")

# Establishing connection to the SQLite database
conn = sqlite3.connect("customer_churn.db")

#query to get all table names from the database
sql_query = '''
               SELECT name FROM sqlite_master WHERE type='table'
            '''
#read sql query in pandas
tables = pd.read_sql(sql_query,conn)

# Creating dataframes for each table
for table_name in tables["name"]:
    df = pd.read_sql(f'SELECT * FROM {table_name}', conn)
    globals()[f"{table_name}_df"] = df
    print(f"Dataframe for table '{table_name}' created with shape: {df.shape}")

#connection close
conn.close()

# Print table names and column names
conn = sqlite3.connect('customer_churn.db')

for table_name in tables['name']:
    print(f"\nTable Name: {table_name}")
    # Get column information
    columns_query = f"PRAGMA table_info({table_name});"
    columns = pd.read_sql(columns_query, conn)
    print("Columns:")
    print(columns['name'].tolist())

# Close connection
conn.close()

#...................DATA CLEANING.....................

# Display the last 5 rows of the DataFrame
print(db_customer_df.tail())

# Check the number of duplicate rows
print(db_customer_df.duplicated().sum())

# Display DataFrame information (rows, columns, data types, null values)
db_customer_df.info()

# Drop unnecessary columns
db_customer_df.drop(columns=['interests', 'pincode'], inplace=True)

# Convert 'dob' column to datetime format
db_customer_df['dob'] = pd.to_datetime(db_customer_df['dob'], errors='coerce')

# Rename 'name' column to 'customer_name'
db_customer_df.rename(columns={'name': 'customer_name'}, inplace=True)

# Standardize gender values
db_customer_df['gender'] = db_customer_df['gender'].replace({'Men': 'Male', 'Women': 'Female'}, inplace=True)
print(db_customer_df['gender'].unique())


# Display unique values in the country column
print(db_customer_df['country'].unique())

# Display rows where country is missing
print(db_customer_df[db_customer_df['country'].isna()])

# Create a mapping of state to country using available data
state_country_mapping = (
    db_customer_df.dropna(subset=['country'])
    .set_index('state')['country']
    .to_dict()
)

# Fill missing country values based on the corresponding state
db_customer_df['country'] = db_customer_df['country'].fillna(
    db_customer_df['state'].map(state_country_mapping)
)

# Display DataFrame information after cleaning
db_customer_df.info()

# Display the last 5 rows of the DataFrame
print(db_subscription_df.tail())

# Check the number of duplicate rows
print(db_subscription_df.duplicated().sum())

# Display DataFrame information (rows, columns, data types, null values)
db_subscription_df.info()

# change data type to date - subscription_start_date , renewal_date, cancellation_date
db_subscription_df['subscription_start_date'] = pd.to_datetime(db_subscription_df['subscription_start_date'], errors='coerce')
db_subscription_df['renewal_date'] = pd.to_datetime(db_subscription_df['renewal_date'], errors='coerce')
db_subscription_df['cancellation_date'] = pd.to_datetime(db_subscription_df['cancellation_date'], errors='coerce')

# Display DataFrame information after cleaning
db_subscription_df.info()

# Display the last 5 rows of the DataFrame
print(db_support_df.tail())

# Check the number of duplicate rows
print(db_support_df.duplicated().sum())

# Display DataFrame information (rows, columns, data types, null values)
db_support_df.info()

# drop columns
db_support_df.drop(columns=['col_1', 'comment'], inplace=True)

# change data type to date - complaint_date
db_support_df['complaint_date'] = pd.to_datetime(db_support_df['complaint_date'])

# Display DataFrame information after cleaning
db_support_df.info()

#.................FEATURE ENGINEERING.....................
import numpy as np

# Create churn flag (1 = Cancelled, 0 = Active)
db_subscription_df['churn_flag'] = np.where(
    db_subscription_df['cancellation_date'].notnull(), 1, 0
)

# Convert churn flag to integer
db_subscription_df['churn_flag'] = db_subscription_df['churn_flag'].astype(int)

# Merge subscription, customer, and support data
df = db_subscription_df.merge(db_customer_df, on='customerid', how='left') \
                       .merge(db_support_df, on='customerid', how='left')

# Display rows and columns
print(df.shape)

# Print unique customer IDs in each table
print('db_subscription_df unique value:', db_subscription_df['customerid'].nunique())
print('db_customer_df unique value:', db_customer_df['customerid'].nunique())
print('db_support_df unique value:', db_support_df['customerid'].nunique())

# Print total rows in support table
print('db_support_df all value:', db_support_df['customerid'].size)

# Count complaints for each customer
db_support_df['complaint_count'] = db_support_df.groupby('customerid')['customerid'].transform('count')

# Keep only the latest complaint for each customer
db_support_df = db_support_df.sort_values('complaint_date').drop_duplicates('customerid', keep='last')

# Print total customers after removing duplicates
print(db_support_df['customerid'].size)

# Merge cleaned support data with other tables
df = db_subscription_df.merge(db_customer_df, on='customerid', how='left') \
                       .merge(db_support_df, on='customerid', how='left')

# Display final dataset shape
print(df.shape)

df.to_csv("exported_churn_data.csv", index=False)

#................DATA ANALYSIS.....................

#churn_rate
churn_rate = df['churn_flag'].mean() * 100
print(f"Churn Rate: {churn_rate:.2f}%")

#retention_rate
retention_rate = 100 - churn_rate
print(f"Retention Rate: {retention_rate:.2f}%")

#churn rate by plan type
churn_rate_by_plan = (df.groupby('plan_type')['churn_flag'].mean().mul(100).round(2).reset_index(name='churn_rate_pct'))
print(churn_rate_by_plan)

# Churn by state + sum(revenue) & count of users 
churn_by_state = df.groupby('state').agg(
                 churn_rate_pct=('churn_flag',lambda x: round((x.mean()*100),2)),
                 revenue_sum = ('monthly_charges','sum'),
                 count_users = ('customerid','count')
).reset_index()

#Churn by subscription type + sum(revenue) & count of users
churn_by_subscription_type = df.groupby('subscription_type').agg(
                 churn_rate_pct=('churn_flag',lambda x: round((x.mean()*100),2)),
                 revenue_sum = ('monthly_charges','sum'),
                 count_users = ('customerid','count')
).reset_index()

#ARPU-avg revenue per user
arpu = df['monthly_charges'].mean()
print(f"Average Revenue Per User : {arpu:.2f}")

#avg customer tenure_days
today = pd.Timestamp.now()
df['tenure_days'] = np.where(df['cancellation_date'].notna(),
                             (df['cancellation_date'] - df['subscription_start_date']).dt.days,
                             (today - df['subscription_start_date']).dt.days
)
avg_tenure_days = df['tenure_days'].mean()
print(f"Avg tenure days: {avg_tenure_days:.2f}")

# revenue lost from churned users
revenue_at_risk = df.loc[df['churn_flag']==1, 'monthly_charges'].sum()
print("Revenue at Risk (Rs 'K') =", revenue_at_risk)

# Escalation Rate
escalation_rate = (df['escalations']=='Y').mean()*100
print("Escalation Rate = ", round(escalation_rate, 2), "%")

# Avg Complaint Per User
avg_complaints = df['complaint_count'].sum() / df['customerid'].nunique()
print("Avg Complaints Per User = ", round(avg_complaints, 2))

# Correlation Esclation vs Churn
df['escalations'] = np.where(df['escalations'] == 'Y', 1, 0) 
corr_df = df[['escalations', 'churn_flag']].dropna()

correlation = corr_df['escalations'].corr(df['churn_flag'])
print("Correlation between esclation vs churn is = ", round(correlation,2))

# Create a column using existing col - Churn risk
conditions = [
        (df['churn_score'] < 50),
        (df['churn_score'] >= 50) & (df['churn_score'] < 70),
        (df['churn_score'] >= 70)
]

choices = ['low', 'med', 'high']

df['churn_risk'] = np.select(conditions, choices, default='unknown')

#.................VISUALIZATION.....................

df_visual = df.copy()
print(df_visual.columns)
print(df_visual['gender'].unique())

#month wise churn
df_visual['cancellation_month'] = df_visual['cancellation_date'].dt.to_period('M')
churn_trend = df_visual[df_visual['churn_flag']==1].groupby('cancellation_month').size()

plt.figure(figsize=(6,3))
plt.plot(churn_trend.index.astype(str),churn_trend.values,marker='o',color='purple',linewidth=2,markersize=6,linestyle='dashed')
plt.title('Monthly Churn Trend')
plt.xlabel('Month')
plt.ylabel('Number of Churned Customers')
plt.show()

#churn rate by state
churn_rate_by_state = df_visual.groupby('state')['churn_flag'].mean()
plt.figure(figsize=(4,4))
plt.bar(churn_rate_by_state.index, churn_rate_by_state.values, color='pink')
plt.title('Churn Rate by State')
plt.xlabel('State')
plt.ylabel('Churn Rate')
plt.show()

#churn rate by plan_type
churn_rate_by_plan = df_visual.groupby('plan_type')['churn_flag'].mean()
plt.figure(figsize=(4,4))
plt.bar(churn_rate_by_plan.index, churn_rate_by_plan.values, color='blue')
plt.title('Churn Rate by Plan Type')
plt.xlabel('Plan Type')
plt.ylabel('Churn Rate')
plt.show()

#......................PIVOT TABLE.........................
pivot_table = pd.pivot_table(
                 df_visual,
                 index='plan_type',
                 values=['customerid','churn_flag','monthly_charges'],
                 aggfunc={'customerid':'count','churn_flag':'mean','monthly_charges':'sum'}
)
print(pivot_table)

#...........................VISUALIZATION.....................
df_encoded = df_visual[['plan_type', 'contract_type', 'churn_score', 'churn_flag', 'churn_risk', 'escalations']]
print("Plan type unique values:", df_encoded['plan_type'].unique())
print("Contract type unique values:", df_encoded['contract_type'].unique())
print("Churn risk unique values:", df_encoded['churn_risk'].unique())

order_mapp = {'plan_type': ['Basic', 'Standard', 'Premium'],
              'contract_type': ['Monthly', 'Annual'],
              'churn_risk': ['low', 'med', 'high']}

for col,order in order_mapp.items():
    df_encoded[col] = pd.Categorical(df_encoded[col].astype('category'), categories = order, ordered=True).codes

print(df_visual[['plan_type', 'contract_type', 'churn_score', 'churn_flag', 'churn_risk', 'escalations']].head())
print(df_encoded.head())

sns.heatmap(df_encoded.corr(),annot=True)
plt.show()

#catplot
sns.figure(figsize=(12,10))
sns.catplot(data=df_visual,
    x='plan_type',
    y='monthly_charges',
    hue='gender',
    col='churn_risk',
   )
plt.show()

#pairplot
sns.pairplot(df_visual)
plt.show()
