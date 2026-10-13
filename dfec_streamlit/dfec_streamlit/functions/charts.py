import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st

def display_charts(df, engine):

    df['finish_datetime'] = pd.to_datetime(df['finish_datetime'])
    
    daily_defects = df.resample('D', on='finish_datetime').agg({
        'all_defect_qty': 'sum',
        'input_qty':     'sum'
    }).reset_index()

    # 不良率の計算 (全体投入量に対する不良数量)
    daily_defects['failure_ratio'] = daily_defects['all_defect_qty'] / daily_defects['input_qty']

    # Streamlit アプリケーションタイトル
    st.title("Defect Analysis Over Time")

    fig, ax1 = plt.subplots(figsize=(14,6))
    # 棒グラフ（不良数）
    ax1.bar(daily_defects['finish_datetime'], daily_defects['all_defect_qty'], color='b', alpha=0.6, label='Total Defect Count')

    # 折れ線グラフ（不良率）
    ax2 = ax1.twinx()
    ax2.plot(daily_defects['finish_datetime'], daily_defects['failure_ratio'], marker='x', color='r', label='Failure Ratio')

    # 軸設定
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Total Defect Count', color='b')
    ax2.set_ylabel('Failure Ratio', color='r')

    plt.title("Daily Defect Count and Failure Ratio")
    ax1.tick_params(axis='y', colors='b')
    ax2.tick_params(axis='y', colors='r')

    fig.tight_layout()
    st.pyplot(fig)

    # 増加・減少の判定
    if daily_defects['all_defect_qty'].iloc[-1] > daily_defects['all_defect_qty'].iloc[0]:
        trend = "increasing"
    else:
        trend = "decreasing"

    st.write(f"The trend of defects qty is **{trend}**.")

    # 増加・減少の判定
    if daily_defects['failure_ratio'].iloc[-1] > daily_defects['failure_ratio'].iloc[0]:
        trend = "increasing"
    else:
        trend = "decreasing"

    st.write(f"The trend of defects ratio is **{trend}**.")

# パレート図
    defect_columns=None
    if defect_columns is None:
        possible_columns = [f'all_G{i:03d}' for i in range(1, 101)]  
        defect_columns = [col for col in possible_columns if col in df.columns] 

    defects_sum = df[defect_columns].sum().sort_values(ascending=False)
    cumulative_percentage = defects_sum.cumsum() / defects_sum.sum() * 100

    pareto_df = pd.DataFrame({
        'defect': [col.replace("all_", "") for col in defects_sum.index], 
        'count': defects_sum.values,
        'Cumulative Percentage': cumulative_percentage
    })

    fig, ax1 = plt.subplots(figsize=(12, 6))
    sns.barplot(x='defect', y='count', data=pareto_df, color='b')
    ax2 = ax1.twinx()
    sns.lineplot(x='defect', y='Cumulative Percentage', data=pareto_df, color='r', marker='o', ax=ax2)
    plt.title('Pareto Chart of defects')
    # X軸とY軸のラベル設定 
    plt.xlabel('Defects')
    plt.ylabel('Count of defects (Blue)')
    ax2.set_ylabel('Cumulative Percentage (%) (Red)')

    ax2.set_ylim(0, 100)

    # X軸ラベルの90度回転設定 
    plt.xticks(rotation=90)
    
    # 自動レイアウト調整
    plt.tight_layout()
    st.pyplot(fig)

    #不良名称を取得する
    df_f = None
    with engine.connect() as connection:
        query = """
            SELECT   
                defect_code,
                defect_name
            FROM prass_process_defect 
            WHERE defect_name is not NULL
            GROUP BY
                defect_code,
                defect_name
        """

        df_f = pd.read_sql_query(query, connection)

    if df_f is not None:
        pareto_df = pd.merge(
            pareto_df,
            df_f,
            left_on='defect',       
            right_on='defect_code',  
            how='left'
        )      
    st.dataframe(pareto_df)     