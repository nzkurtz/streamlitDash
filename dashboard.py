import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Company Funding Dashboard",
    page_icon="💰",
    layout="wide"
)

# Title and description
st.title("Company Funding Dashboard")
st.markdown("Search and explore company funding data")

# Load data function with caching
@st.cache_data
def load_data():
    """Load data from Excel file"""
    try:
        df = pd.read_excel('output3.xlsx')
        return df
    except FileNotFoundError:
        st.error("Excel file 'output3.xlsx' not found. Please make sure the file is in the same directory.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return pd.DataFrame()

# Load the data
df = load_data()

if not df.empty:
    # Display file info
    file_mod_time = os.path.getmtime('output3.xlsx')
    last_updated = datetime.fromtimestamp(file_mod_time).strftime("%Y-%m-%d %H:%M:%S")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Companies", len(df))
    with col2:
        st.metric("Total Records", len(df))
    with col3:
        st.info(f"Last Updated: {last_updated}")
    
    st.divider()
    
    # Search functionality
    st.subheader("Search Companies")
    
    # Create search input
    search_term = st.text_input(
        "Search by company name:",
        placeholder="Enter company name to search...",
        help="Search is case-insensitive and will match partial names"
    )
    
    # Filter data based on search
    if search_term:
        # Case-insensitive search in Company column
        filtered_df = df[df['Company'].str.contains(search_term, case=False, na=False)]
        st.info(f"Found {len(filtered_df)} companies matching '{search_term}'")
    else:
        filtered_df = df
        st.info(f"Showing all {len(filtered_df)} companies")
    
    # Display the filtered data
    if not filtered_df.empty:
        st.subheader("Company Data")
        
        # Display all columns from the spreadsheet
        display_df = filtered_df.copy()
        
        # Clean up column names for better readability
        column_mapping = {
            'Reviewed/CONFIRMED PR Annoucement URL': 'PR Announcement URL',
            'Name-long version': 'Company Full Name',
            'Amount Raised-this funding round': 'Amount Raised (This Round)',
            'Total Amount Raised-all time': 'Total Raised (All Time)',
            'Date of PR': 'PR Date'
        }
        
        # Rename columns for better display
        display_df = display_df.rename(columns=column_mapping)
        
        # Display the table with all columns
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Company": st.column_config.TextColumn("Company", width="medium"),
                "Raised": st.column_config.TextColumn("Raised", width="small"),
                "Round": st.column_config.TextColumn("Round", width="small"),
                "PR Announcement URL": st.column_config.LinkColumn("PR URL", width="medium"),
                "PrimaryURL": st.column_config.LinkColumn("Primary URL", width="medium"),
                "Secondary_Source": st.column_config.LinkColumn("Secondary Source", width="medium"),
                "PR Date": st.column_config.DateColumn("PR Date", width="small"),
                "Company Full Name": st.column_config.TextColumn("Full Name", width="medium"),
                "Funding Round": st.column_config.TextColumn("Funding Round", width="small"),
                "Amount Raised (This Round)": st.column_config.TextColumn("Amount (This Round)", width="small"),
                "Lead Investor": st.column_config.TextColumn("Lead Investor", width="medium"),
                "All Investors": st.column_config.TextColumn("All Investors", width="large"),
                "Total Raised (All Time)": st.column_config.TextColumn("Total Raised", width="small")
            }
        )
        
        # Download filtered data
        if st.button("Download Filtered Data as CSV"):
            csv = filtered_df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"company_data_filtered_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    else:
        st.warning("No companies found matching your search criteria.")
        
    # Refresh button
    st.divider()
    if st.button("Refresh Data"):
        st.cache_data.clear()
        st.rerun()

else:
    st.error("No data available. Please check if the Excel file exists and contains data.")

# Footer
st.divider()
st.markdown("*Dashboard automatically updates when the Excel file is modified*")