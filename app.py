import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

df = pd.read_excel("data/test.xlsx")

df.head()

def main():
    st.title("Health Inequalities in Streamlit")

    with st.sidebar:
        st.header("Choose and ICB")