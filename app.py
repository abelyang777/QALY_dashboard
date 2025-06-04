import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import random
from datetime import datetime, timedelta
import uuid
import os

# Page configuration
st.set_page_config(
    page_title="QALY NFT Management Platform",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
    }
    .metric-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        margin: 0.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .sidebar .sidebar-content {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding-left: 20px;
        padding-right: 20px;
        background-color: #f0f2f6;
        border-radius: 10px 10px 0px 0px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #667eea;
        color: white;
    }
</style>
""", unsafe_allow_html=True)


# Data loading and processing
def load_qaly_data(dataset):
    df = pd.read_csv(dataset + "QALY_data.csv")
    return df

def generate_nft_ledger(dataset):
    df = pd.read_csv(dataset + "nft_ledger.csv")
    df.loc[:, 'mint_date'] = pd.to_datetime(df['mint_date'], errors='coerce')
    return df

def generate_time_series_data(dataset):
    df = pd.read_csv(dataset + "time_series_data.csv")
    return df

def initialize_session_state(dataset):
    qaly_df = load_qaly_data(dataset)
    qaly_df['Cost per QALY'] = qaly_df['Cost'] / qaly_df['Avg QALY Gain']
    if 'qaly_df' not in st.session_state:
        st.session_state.qaly_df = qaly_df

    nft_df = generate_nft_ledger(dataset)
    nft_df['mint_date'] = pd.to_datetime(nft_df['mint_date'], errors='coerce')
    if 'nft_df' not in st.session_state:
        st.session_state.nft_df = nft_df

    time_series_df = generate_time_series_data(dataset)
    if 'time_series_df' not in st.session_state:
        st.session_state.time_series_df = time_series_df



# Sidebar navigation
st.sidebar.markdown("""
<div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1rem; border-radius: 10px; margin-bottom: 1rem;'>
    <h2 style='color: white; text-align: center; margin: 0;'>QALY NFT Platform</h2>
</div>
""", unsafe_allow_html=True)

def main_app():

    query_params = st.query_params

    if "data" in query_params:
        encoded_json = query_params["data"]
        json_str = urllib.parse.unquote(encoded_json)

        try:
            incoming_data = json.loads(json_str)
            st.success("Received data successfully!")
            st.dataframe(incoming_data)

            program_id = st.text_input("Enter Program ID")
            program_name = st.text_input("Enter Program Name")

            if st.button("Submit and Save"):
                if not program_id or not program_name:
                    st.warning("Please fill in both Program ID and Name.")
                else:
                    # Add new fields to the incoming data
                    if isinstance(incoming_data, dict):
                        df_new = pd.DataFrame([incoming_data])
                    else:
                        df_new = pd.DataFrame(incoming_data)

                    df_new["Program ID"] = program_id
                    df_new["Program Name"] = program_name

                    file_path = "QALY_data.csv"

                    if os.path.exists(file_path):
                        df_existing = pd.read_csv(file_path)
                        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
                    else:
                        df_combined = df_new

                    df_combined.to_csv(file_path, index=False)
                    st.success("Data saved successfully.")
                    st.markdown("[Click here to return to index](./)", unsafe_allow_html=True)
                    st.cache_data.clear()

        except Exception as e:
            st.error(f"Failed to parse data: {e}")


    else:

        if "dataset" in query_params:
            dataset = query_params["dataset"] + "_"
        else:
            dataset = ""

        initialize_session_state(dataset)

        page = st.sidebar.selectbox(
            "Navigate to:",
            ["Overview", "Program Dashboard", "NFT Management", "Transfer NFTs"],
            index=0
        )

        # Main content based on page selection
        if page == "Overview":
            from overview import render
            render()

        elif page == "Program Dashboard":
            st.markdown("""
            <div class='main-header'>
                <h1>Program Dashboard</h1>
                <p>Comprehensive analysis of disease risk reduction programs</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Filters
            col1, col2, col3 = st.columns(3)
            with col1:
                selected_diseases = st.multiselect(
                    "Filter by Disease:",
                    options=qaly_df['Disease'].unique(),
                    default=qaly_df['Disease'].unique()[-1],
                )
            
            with col2:
                selected_interventions = st.multiselect(
                    "Filter by Intervention:",
                    options=qaly_df['Intervention'].unique(),
                    default=qaly_df[qaly_df['Disease']==qaly_df['Disease'].unique()[-1]]['Intervention'].unique()
                )
            
            with col3:
                date_range = st.date_input(
                    "Date Range:",
                    value=(datetime.now() - timedelta(days=365), datetime.now()),
                    help="Filter time series data by date range"
                )
            
            # Filter data
            filtered_df = qaly_df[
                (qaly_df['Disease'].isin(selected_diseases)) &
                (qaly_df['Intervention'].isin(selected_interventions))
            ]
            
            # Tabs for different views
            tab1, tab2, tab3, tab4 = st.tabs(["Time Series", "Program Map", "Bubble Analysis", "Data Table"])
            with tab1:
                st.subheader("QALY Accrual Over Time")
                
                # Filter time series data
                filtered_ts = time_series_df[
                    time_series_df['Program ID'].isin(filtered_df['Program ID'])
                ]
                
                fig = px.area(
                    filtered_ts,
                    x='Date',
                    y='Cumulative QALYs',
                    color='Program Name',
                    title="Cumulative QALY Generation Over 10-Year Program Span",
                    labels={'Cumulative QALYs': 'Cumulative QALYs', 'Date': 'Program Timeline'}
                )
                fig.update_layout(hovermode='x unified')
                st.plotly_chart(fig, use_container_width=True)
                
                # Annual breakdown
                st.subheader("Annual QALY Generation")
                annual_fig = px.bar(
                    filtered_ts,
                    x='Year',
                    y='Annual QALYs',
                    color='Disease',
                    facet_col='Program Name',
                    facet_col_wrap=4,
                    title="Annual QALY Generation by Program"
                )
                st.plotly_chart(annual_fig, use_container_width=True)
            
            with tab2:
                st.subheader("Program Distribution Treemap")
                
                # Create treemap data
                treemap_data = filtered_df.copy()
                treemap_data['Disease_Intervention'] = treemap_data['Disease'] + ' - ' + treemap_data['Intervention']
                
                fig = px.treemap(
                    treemap_data,
                    path=['Disease', 'Program Name'],
                    values='Tot QALY Gain',
                    color='Cost per QALY',
                    color_continuous_scale='RdYlGn_r',
                    title="Program Distribution by Disease and Intervention"
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with tab3:
                st.subheader("Multi-Dimensional Program Analysis")
                
                fig = px.scatter(
                    filtered_df,
                    x='Patient',
                    y='Tot QALY Gain',
                    size='Survival Pop',
                    color='Avg QALY Gain',
                    hover_name='Program Name',
                    hover_data=['Disease', 'Cost'],
                    title="Program Size vs QALY Impact (bubble size = survival population)",
                    labels={
                        'Patient': 'Total Patients',
                        'Tot QALY Gain': 'Total QALY Gain',
                        'Avg QALY Gain': 'Average QALY Gain'
                    }
                )
                fig.update_traces(marker=dict(line=dict(width=2, color='DarkSlateGrey')))
                st.plotly_chart(fig, use_container_width=True)
            
            with tab4:
                st.subheader("Program Data Table")
                
                # Enhanced data table with calculations
                display_df = filtered_df.copy()
                display_df['Survival Rate'] = (display_df['Survival Pop'] / display_df['Patient'] * 100).round(1)
                
                st.dataframe(
                    display_df,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Cost": st.column_config.NumberColumn(
                            "Cost ($)",
                            format="$%d"
                        ),
                        "Survival Rate": st.column_config.NumberColumn(
                            "Survival Rate (%)",
                            format="%.1f%%"
                        ),
                        "Tot QALY Gain": st.column_config.NumberColumn(
                            "Total QALY Gain",
                            format="%d"
                        )
                    }
                )

        elif page == "NFT Management":
            st.markdown("""
            <div class='main-header'>
                <h1>NFT Management Dashboard</h1>
                <p>Each NFT represents a single QALY from risk reduction programs</p>
            </div>
            """, unsafe_allow_html=True)
            
            # NFT Summary metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_nfts = len(nft_df)
                st.metric("Total NFTs", f"{total_nfts:,}")
            
            with col2:
                active_nfts = len(nft_df[nft_df['status'] == 'active'])
                st.metric("Active NFTs", f"{active_nfts:,}")
            
            with col3:
                unique_owners = nft_df['owner_id'].nunique()
                st.metric("Unique Owners", unique_owners)
            
            with col4:
                total_transfers = nft_df['transfer_count'].sum()
                st.metric("Total Transfers", f"{total_transfers:,}")
            
            # NFT Management tabs
            tab1, tab2, tab3, tab4 = st.tabs(["NFT Overview", "Ownership", "Analytics", "NFT Details"])
            
            with tab1:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("NFT Distribution by Disease")
                    disease_nft_count = nft_df.groupby('disease').size().reset_index(name='count')
                    fig = px.bar(
                        disease_nft_count,
                        x='disease',
                        y='count',
                        color='disease',
                        title="NFT Count by Disease Category"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    st.subheader("NFT Status Distribution")
                    status_count = nft_df['status'].value_counts().reset_index()
                    status_count.columns = ['status', 'count']
                    fig = px.pie(
                        status_count,
                        values='count',
                        names='status',
                        title="NFT Status Distribution"
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            with tab2:
                st.subheader("Ownership Distribution")
                
                ownership_stats = nft_df.groupby('owner_id').agg({
                    'nft_id': 'count',
                    'qaly_value': 'sum',
                    'transfer_count': 'sum'
                }).reset_index()
                ownership_stats.columns = ['Owner', 'NFT Count', 'Total QALY Value', 'Total Transfers']
                ownership_stats = ownership_stats.sort_values('NFT Count', ascending=False)
                
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    fig = px.bar(
                        ownership_stats,
                        x='Owner',
                        y='NFT Count',
                        color='Total QALY Value',
                        title="NFT Holdings by Owner",
                        color_continuous_scale='viridis'
                    )
                    fig.update_xaxes(tickangle=45)
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    st.subheader("Top Owners")
                    st.dataframe(
                        ownership_stats.head(10),
                        use_container_width=True,
                        hide_index=True
                    )
            
            with tab3:
                st.subheader("NFT Transfer Analytics")
                
                # Transfer timeline
                nft_df['mint_month'] = nft_df['mint_date'].dt.to_period('M')
                monthly_mints = nft_df.groupby('mint_month').size().reset_index(name='mints')
                monthly_mints['mint_month'] = monthly_mints['mint_month'].astype(str)
                
                fig = px.line(
                    monthly_mints,
                    x='mint_month',
                    y='mints',
                    title="NFT Minting Timeline",
                    markers=True
                )
                fig.update_xaxes(tickangle=45)
                st.plotly_chart(fig, use_container_width=True)
                
                # Transfer heatmap
                transfer_matrix = nft_df.groupby(['disease', 'intervention']).agg({
                    'nft_id': 'count',
                    'transfer_count': 'mean'
                }).reset_index()
                
                fig = px.scatter(
                    transfer_matrix,
                    x='disease',
                    y='intervention',
                    size='nft_id',
                    color='transfer_count',
                    title="NFT Transfer Activity Heatmap",
                    labels={'transfer_count': 'Avg Transfers per NFT'}
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with tab4:
                st.subheader("NFT Detailed View")
                
                # Search and filter
                col1, col2, col3 = st.columns(3)
                with col1:
                    search_owner = st.selectbox("Filter by Owner:", ['All'] + sorted(nft_df['owner_id'].unique()), key="search_owner")
                with col2:
                    search_disease = st.selectbox("Filter by Disease:", ['All'] + sorted(nft_df['disease'].unique()), key="search_disease")
                with col3:
                    search_status = st.selectbox("Filter by Status:", ['All'] + sorted(nft_df['status'].unique()), key="search_status")
                
                # Apply filters
                filtered_nfts = nft_df.copy()
                if search_owner != 'All':
                    filtered_nfts = filtered_nfts[filtered_nfts['owner_id'] == search_owner]
                if search_disease != 'All':
                    filtered_nfts = filtered_nfts[filtered_nfts['disease'] == search_disease]
                if search_status != 'All':
                    filtered_nfts = filtered_nfts[filtered_nfts['status'] == search_status]
                
                # Display filtered NFTs
                st.write(f"Showing {len(filtered_nfts)} NFTs")
                st.dataframe(
                    filtered_nfts[['nft_id', 'program_id', 'disease', 'intervention', 'owner_id', 
                                  'status', 'mint_date', 'transfer_count', 'qaly_value']],
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "mint_date": st.column_config.DatetimeColumn(
                            "Mint Date",
                            format="DD/MM/YYYY"
                        ),
                        "qaly_value": st.column_config.NumberColumn(
                            "QALY Value",
                            format="%.4f"
                        )
                    }
                )

        elif page == "Transfer NFTs":
            st.markdown("""
            <div class='main-header'>
                <h1>NFT Transfer Center</h1>
                <p>Transfer NFTs between owners with full audit trail</p>
            </div>
            """, unsafe_allow_html=True)
            
            tab1, tab2 = st.tabs(["Single Transfer", "Batch Transfer"])
            
            with tab1:
                st.subheader("Single NFT Transfer")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Select NFT to transfer
                    available_nfts = nft_df[nft_df['status'] == 'active']['nft_id'].tolist()[:50]
                    selected_nft = st.selectbox("Select NFT to Transfer:", available_nfts,key="selected_nft")
                    
                    if selected_nft:
                        nft_details = nft_df[nft_df['nft_id'] == selected_nft].iloc[0]
                        
                        st.info(f"""
                        **NFT Details:**
                        - Program: {nft_details['program_id']}
                        - Disease: {nft_details['disease']}
                        - Intervention: {nft_details['intervention']}
                        - Current Owner: {nft_details['owner_id']}
                        - QALY Value: {nft_details['qaly_value']:.4f}
                        """)
                
                with col2:
                    # Transfer details
                    all_owners = sorted(nft_df['owner_id'].unique())
                    current_owner = nft_details['owner_id'] if 'nft_details' in locals() else None
                    available_recipients = [owner for owner in all_owners if owner != current_owner]
                    
                    new_owner = st.selectbox("Transfer to:", available_recipients if 'nft_details' in locals() else all_owners, key="new_owner")
                    transfer_reason = st.text_area("Transfer Reason (optional):", placeholder="e.g., Hospital merger, Research collaboration...")
                    
                    if st.button("Execute Transfer", type="primary"):
                        if selected_nft and new_owner:
                            # Simulate transfer
                            st.success(f"Successfully transferred {selected_nft} from {current_owner} to {new_owner}")
                            st.balloons()
                            
                            # Show transfer confirmation
                            st.json({
                                "transaction_id": f"TXN-{uuid.uuid4().hex[:8].upper()}",
                                "nft_id": selected_nft,
                                "from": current_owner,
                                "to": new_owner,
                                "timestamp": datetime.now().isoformat(),
                                "reason": transfer_reason or "Not specified",
                                "status": "completed"
                            })
            
            with tab2:
                st.subheader("Batch NFT Transfer")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Batch transfer parameters
                    from_owner = st.selectbox("Transfer from:", sorted(nft_df['owner_id'].unique()))
                    to_owner = st.selectbox("Transfer to:", [owner for owner in sorted(nft_df['owner_id'].unique()) if owner != from_owner])
                    
                    # Show available NFTs for selected owner
                    owner_nfts = nft_df[(nft_df['owner_id'] == from_owner) & (nft_df['status'] == 'active')]
                    st.write(f"Available NFTs from {from_owner}: {len(owner_nfts)}")
                    
                    transfer_count = st.number_input(
                        "Number of NFTs to transfer:",
                        min_value=1,
                        max_value=len(owner_nfts),
                        value=min(5, len(owner_nfts))
                    )
                    
                with col2:
                    # Preview of NFTs to be transferred (oldest first)
                    if from_owner and len(owner_nfts) > 0:
                        nfts_to_transfer = owner_nfts.nsmallest(transfer_count, 'mint_date')
                        
                        st.subheader("NFTs to be transferred:")
                        st.dataframe(
                            nfts_to_transfer[['nft_id', 'program_id', 'disease', 'mint_date', 'qaly_value']],
                            use_container_width=True,
                            hide_index=True
                        )
                        
                        total_qaly_value = nfts_to_transfer['qaly_value'].sum()
                        st.metric("Total QALY Value", f"{total_qaly_value:.4f}")
                
                # Batch transfer execution
                st.markdown("---")
                batch_reason = st.text_area("Batch Transfer Reason:", placeholder="e.g., Department restructuring, Grant requirements...")
                
                if st.button("Execute Batch Transfer", type="primary"):
                    if from_owner and to_owner and transfer_count > 0:
                        # Simulate batch transfer
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        for i in range(transfer_count):
                            progress_bar.progress((i + 1) / transfer_count)
                            status_text.text(f'Transferring NFT {i + 1} of {transfer_count}...')
                        
                        st.success(f"Successfully transferred {transfer_count} NFTs from {from_owner} to {to_owner}")
                        st.balloons()
                        
                        # Show batch transfer summary
                        batch_summary = {
                            "batch_id": f"BATCH-{uuid.uuid4().hex[:8].upper()}",
                            "nfts_transferred": transfer_count,
                            "from_owner": from_owner,
                            "to_owner": to_owner,
                            "total_qaly_value": f"{total_qaly_value:.4f}",
                            "timestamp": datetime.now().isoformat(),
                            "reason": batch_reason or "Not specified",
                            "status": "completed"
                        }
                        
                        st.json(batch_summary)
                
                # Transfer history visualization
                st.markdown("---")
                st.subheader("Transfer Activity Visualization")
                
                # Simulate some transfer history data for visualization
                transfer_history = []
                for i in range(30):
                    transfer_history.append({
                        'date': datetime.now() - timedelta(days=i),
                        'transfers': random.randint(5, 50),
                        'volume': random.randint(100, 1000)
                    })
                
                transfer_df = pd.DataFrame(transfer_history)
                
                fig = make_subplots(
                    rows=2, cols=1,
                    subplot_titles=('Daily Transfer Count', 'Daily Transfer Volume (QALYs)'),
                    vertical_spacing=0.1
                )
                
                fig.add_trace(
                    go.Scatter(x=transfer_df['date'], y=transfer_df['transfers'], 
                              mode='lines+markers', name='Transfers', line=dict(color='#667eea')),
                    row=1, col=1
                )
                
                fig.add_trace(
                    go.Scatter(x=transfer_df['date'], y=transfer_df['volume'], 
                              mode='lines+markers', name='Volume', line=dict(color='#764ba2')),
                    row=2, col=1
                )
                
                fig.update_layout(height=400, showlegend=False, title_text="Recent Transfer Activity")
                st.plotly_chart(fig, use_container_width=True)

        
if __name__ == '__main__':
    main_app()

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem;'>
    <p>QALY NFT Management Platform</p>
    <p><em>This is a demonstration application for managing Quality-Adjusted Life Years as NFTs</em></p>
</div>
""", unsafe_allow_html=True)