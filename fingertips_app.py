# fingertips app

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import fingertips_py as ftp

###################### GET FINGERTIPS DATA ######################

##### Enter Profile Name Here #####
profile_name = ('cancer services')
###################################

# get the metadata for named profile
cancer_profile_metadata = ftp.metadata.get_profile_by_name(profile_name)

#get the profile ID from the metadata
cancer_profile_id = cancer_profile_metadata['Id']

# get the list of metric IDs from the profile metadata using the profile ID
cancer_metadata = ftp.metadata.get_metadata_for_profile_as_dataframe(cancer_profile_id)

# get the list of metric IDs from the profile metadata dataframe
cancer_indicators = cancer_metadata['Indicator ID'].tolist()

# get a dataframe containing all the cancer services data
cancer_indicators_df = pd.DataFrame(
    ftp.retrieve_data.get_data_by_indicator_ids(
        cancer_indicators,
        221,                                        # ICB level data
        15,                                         # England as parent level
        include_sortable_time_periods= True,
        is_test= False
    )
)

# just get the cancer screening coverage metrics
screening_df = cancer_indicators_df[cancer_indicators_df['Indicator Name'].str.contains('screening')]

# remove England. Just keep the ICB-level figures
screening_df = screening_df[~(screening_df['Area Name'] == 'England')]


# get unique lists of fields for use in selection boxes. Sets are unordered by default, hence need to use sorted()
screening_metric_names = sorted(set(screening_df['Indicator Name'].tolist()))
# screening_time_periods = sorted(set(screening_df['Time period'].tolist())) # removed since it is done dynamically later.

# create a column to flag our customer ICBs. This is one way to do the equivalent of a SQL CASE statement.
def icb_flag(row):
    if row['Area Name'] in ['NHS Hampshire and Isle of Wight Integrated Care Board - QRL',
                            'NHS Sussex Integrated Care Board - QNX',
                            'NHS Frimley Integrated Care Board - QNQ',
                            'NHS Buckinghamshire, Oxfordshire and Berkshire West Integrated Care Board - QU9',
                            'NHS Somerset Integrated Care Board - QSL'
                            ]:
        value = 'Customer ICB'
    else:
        value = 'Non-Customer ICB'
    return value

screening_df['ICB flag'] = screening_df.apply(icb_flag, axis = 1)

# EDIT: those long ICB names make it difficult to read the chart; let's shorten them.
screening_df['Area Name'] = screening_df['Area Name'].str.replace('Integrated Care Board','ICB')

# hard-code colour-coding to customer / non-customer ICBs (otherwise seaborn will decide depending on which category comes first, 
# which can change depending on the values)
screening_df['ICB flag colour'] = screening_df['ICB flag'].map({'Customer ICB':'#AE2573','Non-Customer ICB':'#005EB8'})

# create a colour palette dictionary for seaborn to use in the chart. The dictionary contains an explicit key:value pair for seaborn to refer to.
# zip() combines separate columns into the dictionary
palette = dict(zip(screening_df['ICB flag'].unique(),screening_df['ICB flag colour'].unique()))

###################### STREAMLIT APP ######################

st.set_page_config(
        page_title="Fingertips in Streamlit", page_icon=":chart_with_upwards_trend:",
        layout='wide'
    )

# this section contains HTML that fixes the sidebar width at 600px. It means that the whole metric name is always displayed fully in the selectbox
st.markdown(
    """
    <style>
    /* Adjust the sidebar width */
    [data-testid="stSidebar"] {
        min-width: 600px; /* Set your desired width */
        max-width: 600px;
    }
    </style>
    """,
    unsafe_allow_html=True # this is required to be able to use custom HTML and CSS in the app
)

def main():
    st.title("Fingertips Cancer Screening in Streamlit")

    with st.sidebar:
        st.header("Select options")
        selected_metric = st.selectbox(
            label = 'Metric',
            options = screening_metric_names
        )

        # this bit has been added to display only the available time periods for the selected metric
        available_time_periods = sorted(
            set(screening_df[screening_df['Indicator Name'] == selected_metric]['Time period'])
        )

        selected_time_period = st.selectbox(
            label = 'Time Period',
            options = available_time_periods
        )

    # filter the data based on the filter selections    
    df_filtered = screening_df[
        (screening_df['Indicator Name'] == selected_metric) & 
        (screening_df['Time period'] == selected_time_period)
        ].sort_values(by=['Value'], ascending= False)
    
    # return a warning when there is no data for the selection
    if df_filtered.empty:
        st.warning('No data available for the selected metric and time period.')
        return

    column = st.columns(1)[0]

    with column:
        fig, ax = plt.subplots(figsize=(16,8))
        ax = sns.barplot(data = df_filtered, x='Area Name', y='Value', hue= 'ICB flag', palette= palette)
        ax.set_xlabel('ICB Name')
        plt.xticks(rotation=90)
        ax.set_ylabel('Percentage')
        ax.set_title(f'{selected_metric}')
        st.pyplot(fig)


if __name__ == "__main__":

    main()