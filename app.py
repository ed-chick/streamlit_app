import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

df = pd.read_excel("data/test.xlsx")

def main():
    st.title("Health Inequalities in Streamlit")

    with st.sidebar:
        st.header("Choose and ICB")
        icb_options = ("QRL","QNQ","QSL","QNX","QU9")
        selected_icb = st.selectbox(
            label="ICB: ",
            options=icb_options,
        )

    df_filtered = df[df['ICB'] == selected_icb ]
    left_column, right_column = st.columns(2)
    

    with left_column:

        fig, ax = plt.subplots()
        ax = sns.barplot(data = df_filtered, x='Split', y='Activity')
        ax.plot()

        st.write(fig)     
    
    with right_column:
        st.write("A dataframe to display the whole dataset")
        st.write(
            df
        )

if __name__ == "__main__":
    st.set_page_config(
        page_title="Health Inequalities in Streamlit", page_icon=":chart_with_upwards_trend:"
    )

    main()