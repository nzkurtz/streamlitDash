import streamlit as st
import pandas as pd
import sqlite3
import os
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Company Funding Dashboard",
    page_icon="💰",
    layout="wide"
)

# Title and description
st.title("💰 Company Funding Dashboard")
st.markdown("Search and explore company funding data")

# Database connection
@st.cache_resource
def get_connection():
    return sqlite3.connect('funding_data.db', check_same_thread=False)

# Load data function with caching
@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_data():
    """Load data from SQLite database"""
    try:
        conn = get_connection()
        query = "SELECT * FROM funding_rounds"
        df = pd.read_sql(query, conn)
        return df
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return pd.DataFrame()

# Get last updated time from database
def get_last_updated():
    try:
        conn = get_connection()
        query = "SELECT MAX(updated_at) as last_update FROM funding_rounds"
        result = pd.read_sql(query, conn)
        return result['last_update'].iloc[0] if not result.empty and not pd.isna(result['last_update'].iloc[0]) else "Unknown"
    except:
        if os.path.exists('funding_data.db'):
            mod_time = os.path.getmtime('funding_data.db')
            return datetime.fromtimestamp(mod_time).strftime("%Y-%m-%d %H:%M:%S")
        return "Unknown"

# Load the data
df = load_data()

if not df.empty:
    # Display file info
    last_updated = get_last_updated()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Companies", df['Company'].nunique())
    with col2:
        st.metric("Total Records", len(df))
    with col3:
        st.info(f"Last Updated: {last_updated}")
    
    st.divider()
    
    # Search functionality
    st.subheader("🔍 Search Companies")
    
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
        st.subheader("📊 Company Data")
        
        # Display all columns from the database
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
        for old_col, new_col in column_mapping.items():
            if old_col in display_df.columns:
                display_df = display_df.rename(columns={old_col: new_col})
        
        # Remove metadata columns from display
        if 'created_at' in display_df.columns:
            display_df = display_df.drop(columns=['created_at'])
        if 'updated_at' in display_df.columns:
            display_df = display_df.drop(columns=['updated_at'])
        
        # Display the table with all columns
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Company": st.column_config.TextColumn("Company", width="medium"),
                "Raised": st.column_config.TextColumn("Raised", width="small"),
                "Round": st.column_config.TextColumn("Round", width="small"),
                "PR Announcement URL": st.column_config.LinkColumn("PR URL", width="medium") if "PR Announcement URL" in display_df.columns else None,
                "PrimaryURL": st.column_config.LinkColumn("Primary URL", width="medium") if "PrimaryURL" in display_df.columns else None,
                "Secondary_Source": st.column_config.LinkColumn("Secondary Source", width="medium") if "Secondary_Source" in display_df.columns else None,
                "PR Date": st.column_config.DateColumn("PR Date", width="small") if "PR Date" in display_df.columns else None,
                "Company Full Name": st.column_config.TextColumn("Full Name", width="medium") if "Company Full Name" in display_df.columns else None,
                "Funding Round": st.column_config.TextColumn("Funding Round", width="small") if "Funding Round" in display_df.columns else None,
                "Amount Raised (This Round)": st.column_config.TextColumn("Amount (This Round)", width="small") if "Amount Raised (This Round)" in display_df.columns else None,
                "Lead Investor": st.column_config.TextColumn("Lead Investor", width="medium") if "Lead Investor" in display_df.columns else None,
                "All Investors": st.column_config.TextColumn("All Investors", width="large") if "All Investors" in display_df.columns else None,
                "Total Raised (All Time)": st.column_config.TextColumn("Total Raised", width="small") if "Total Raised (All Time)" in display_df.columns else None
            }
        )
        
        # Download filtered data
        if st.button("📥 Download Filtered Data as CSV"):
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
    if st.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()

else:
    st.error("No data available. Please check if the database exists and contains data.")
    
    # Show instructions if database doesn't exist
    if not os.path.exists('funding_data.db'):
        st.info("""
        ### Database Not Found
        
        It looks like you need to create the database first. Run the following command:
        ```
        python create_database.py
        ```
        
        Or if you want to use the update script:
        ```
        python update_database.py create
        ```
        """)

# Footer
st.divider()
st.markdown("*Dashboard automatically updates when the database is updated*")