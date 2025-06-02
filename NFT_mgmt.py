import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import uuid
import numpy as np

# Page configuration
st.set_page_config(
    page_title="QALY Impact Token Dashboard",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state for data persistence
if 'qaly_nfts' not in st.session_state:
    # Demo QALY NFT data
    st.session_state.qaly_nfts = pd.DataFrame({
        'NFT_ID': ['QTK-001', 'QTK-002', 'QTK-003', 'QTK-004', 'QTK-005', 'QTK-006', 
                   'QTK-007', 'QTK-008', 'QTK-009', 'QTK-010', 'QTK-011', 'QTK-012'],
        'Program_Name': ['HeartHealth2025', 'StopHIVNow', 'LDLFix', 'DiabetesCare+', 
                        'HeartHealth2025', 'VaxProtect', 'StopHIVNow', 'LungClear', 
                        'DiabetesCare+', 'HeartHealth2025', 'LDLFix', 'VaxProtect'],
        'Disease': ['Hypertension', 'HIV', 'Hypercholesterolemia', 'Type 2 Diabetes',
                   'Hypertension', 'Influenza', 'HIV', 'COPD', 
                   'Type 2 Diabetes', 'Hypertension', 'Hypercholesterolemia', 'Influenza'],
        'Intervention': ['Thiazide', 'ART', 'Statin', 'Metformin',
                        'ACE Inhibitor', 'Vaccination', 'PrEP', 'Bronchodilator',
                        'Insulin', 'Beta Blocker', 'PCSK9 Inhibitor', 'Vaccination'],
        'QALY_Value': [1.25, 3.40, 0.75, 2.10, 1.45, 0.95, 2.80, 1.60, 2.35, 1.30, 0.85, 0.90],
        'Owner': ['General Hospital', 'Dr. Alice Chen', 'MOH Singapore', 'Sunrise Medical Center',
                 'Dr. Raj Patel', 'WHO Program A', 'Dr. Alice Chen', 'General Hospital',
                 'Dr. Raj Patel', 'Sunrise Medical Center', 'MOH Singapore', 'WHO Program A'],
        'Minting_Date': ['2025-04-01', '2025-04-03', '2025-04-04', '2025-04-05',
                        '2025-04-07', '2025-04-10', '2025-04-12', '2025-04-15',
                        '2025-04-18', '2025-04-20', '2025-04-22', '2025-04-25'],
        'Status': ['Active'] * 12
    })
    
    # Convert date column
    st.session_state.qaly_nfts['Minting_Date'] = pd.to_datetime(st.session_state.qaly_nfts['Minting_Date'])

if 'transfer_history' not in st.session_state:
    # Demo transfer history
    st.session_state.transfer_history = pd.DataFrame({
        'Transfer_ID': ['TXN-001', 'TXN-002', 'TXN-003'],
        'NFT_ID': ['QTK-002', 'QTK-005', 'QTK-008'],
        'From': ['General Hospital', 'MOH Singapore', 'Dr. Alice Chen'],
        'To': ['Dr. Alice Chen', 'Dr. Raj Patel', 'General Hospital'],
        'Transfer_Date': ['2025-04-15', '2025-04-18', '2025-04-23'],
        'Reason': ['Specialist Care Assignment', 'Program Reallocation', 'Hospital Network Transfer']
    })
    
    st.session_state.transfer_history['Transfer_Date'] = pd.to_datetime(st.session_state.transfer_history['Transfer_Date'])

# Sidebar navigation
st.sidebar.title("🏥 QALY Token Dashboard")
page = st.sidebar.selectbox(
    "Navigate to:",
    ["🏠 Dashboard Overview", "📊 QALY Inventory", "🔍 NFT Details", "↔️ Transfer QALYs", "📈 Analytics"]
)

# Helper functions
def generate_nft_id():
    """Generate unique NFT ID"""
    return f"QTK-{str(uuid.uuid4())[:8].upper()}"

def get_entity_options():
    """Get list of unique entities for transfers"""
    return sorted(st.session_state.qaly_nfts['Owner'].unique())

def calculate_total_qalys():
    """Calculate total QALY value"""
    return st.session_state.qaly_nfts['QALY_Value'].sum()

# Main content based on page selection
if page == "🏠 Dashboard Overview":
    st.title("🏥 QALY Impact Token Management Dashboard")
    st.markdown("### Quality-Adjusted Life Years (QALYs) as Verified Impact NFTs")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total QALYs Minted",
            value=f"{calculate_total_qalys():.2f}",
            delta="Impact Units"
        )
    
    with col2:
        st.metric(
            label="Active Programs",
            value=len(st.session_state.qaly_nfts['Program_Name'].unique()),
            delta="Health Initiatives"
        )
    
    with col3:
        st.metric(
            label="Total Transfers",
            value=len(st.session_state.transfer_history),
            delta="Ownership Changes"
        )
    
    with col4:
        st.metric(
            label="Diseases Targeted",
            value=len(st.session_state.qaly_nfts['Disease'].unique()),
            delta="Health Conditions"
        )
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 QALY Distribution by Disease")
        disease_dist = st.session_state.qaly_nfts.groupby('Disease')['QALY_Value'].sum().reset_index()
        fig_pie = px.pie(disease_dist, values='QALY_Value', names='Disease', 
                        title="Total QALY Impact by Disease Category")
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        st.subheader("🏥 Ownership Distribution")
        owner_dist = st.session_state.qaly_nfts.groupby('Owner')['QALY_Value'].sum().reset_index()
        fig_bar = px.bar(owner_dist, x='Owner', y='QALY_Value',
                        title="QALY Holdings by Entity")
        #fig_bar.update_xaxis(tickangle=45)
        st.plotly_chart(fig_bar, use_container_width=True)
    
    # Recent activity
    st.subheader("🔄 Recent Transfer Activity")
    if len(st.session_state.transfer_history) > 0:
        recent_transfers = st.session_state.transfer_history.tail(3)
        st.dataframe(recent_transfers, use_container_width=True)
    else:
        st.info("No recent transfers recorded.")

elif page == "📊 QALY Inventory":
    st.title("📊 QALY NFT Inventory")
    st.markdown("### Complete registry of minted QALY tokens")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        disease_filter = st.selectbox(
            "Filter by Disease:",
            ["All"] + list(st.session_state.qaly_nfts['Disease'].unique())
        )
    
    with col2:
        owner_filter = st.selectbox(
            "Filter by Owner:",
            ["All"] + get_entity_options()
        )
    
    with col3:
        program_filter = st.selectbox(
            "Filter by Program:",
            ["All"] + list(st.session_state.qaly_nfts['Program_Name'].unique())
        )
    
    # Apply filters
    filtered_df = st.session_state.qaly_nfts.copy()
    
    if disease_filter != "All":
        filtered_df = filtered_df[filtered_df['Disease'] == disease_filter]
    if owner_filter != "All":
        filtered_df = filtered_df[filtered_df['Owner'] == owner_filter]
    if program_filter != "All":
        filtered_df = filtered_df[filtered_df['Program_Name'] == program_filter]
    
    # Search functionality
    search_term = st.text_input("🔍 Search NFTs:", placeholder="Search by NFT ID, intervention, etc.")
    if search_term:
        mask = filtered_df.astype(str).apply(lambda x: x.str.contains(search_term, case=False, na=False)).any(axis=1)
        filtered_df = filtered_df[mask]
    
    # Display results
    st.subheader(f"📋 Found {len(filtered_df)} QALY NFTs")
    
    if len(filtered_df) > 0:
        # Format the dataframe for display
        display_df = filtered_df.copy()
        display_df['Minting_Date'] = display_df['Minting_Date'].dt.strftime('%Y-%m-%d')
        display_df['QALY_Value'] = display_df['QALY_Value'].round(2)
        
        st.dataframe(
            display_df,
            use_container_width=True,
            column_config={
                "NFT_ID": st.column_config.TextColumn("NFT ID", width="small"),
                "QALY_Value": st.column_config.NumberColumn("QALY Value", format="%.2f"),
                "Minting_Date": st.column_config.DateColumn("Minted On")
            }
        )
        
        # Export functionality
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="📥 Download as CSV",
            data=csv,
            file_name=f"qaly_inventory_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    else:
        st.warning("No QALYs match your search criteria.")

elif page == "🔍 NFT Details":
    st.title("🔍 QALY NFT Details")
    st.markdown("### Detailed view of individual QALY tokens")
    
    # NFT selection
    nft_options = st.session_state.qaly_nfts['NFT_ID'].tolist()
    selected_nft = st.selectbox("Select NFT ID:", nft_options)
    
    if selected_nft:
        # Get NFT details
        nft_data = st.session_state.qaly_nfts[st.session_state.qaly_nfts['NFT_ID'] == selected_nft].iloc[0]
        
        # Display NFT card
        st.markdown("---")
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown(f"## 🏷️ {selected_nft}")
            st.markdown(f"**Program:** {nft_data['Program_Name']}")
            st.markdown(f"**Disease:** {nft_data['Disease']}")
            st.markdown(f"**Intervention:** {nft_data['Intervention']}")
            st.markdown(f"**QALY Value:** {nft_data['QALY_Value']:.2f}")
            st.markdown(f"**Current Owner:** {nft_data['Owner']}")
            st.markdown(f"**Minted:** {nft_data['Minting_Date'].strftime('%Y-%m-%d')}")
            st.markdown(f"**Status:** {nft_data['Status']}")
        
        with col2:
            st.markdown("### 📊 Impact Metrics")
            # Create a gauge chart for QALY value
            fig_gauge = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = nft_data['QALY_Value'],
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "QALY Impact"},
                gauge = {
                    'axis': {'range': [None, 5]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 1], 'color': "lightgray"},
                        {'range': [1, 2], 'color': "yellow"},
                        {'range': [2, 5], 'color': "green"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 3
                    }
                }
            ))
            fig_gauge.update_layout(height=300)
            st.plotly_chart(fig_gauge, use_container_width=True)
        
        # Transfer history for this NFT
        st.markdown("---")
        st.subheader("📋 Transfer History")
        nft_transfers = st.session_state.transfer_history[
            st.session_state.transfer_history['NFT_ID'] == selected_nft
        ]
        
        if len(nft_transfers) > 0:
            for _, transfer in nft_transfers.iterrows():
                st.markdown(f"""
                **{transfer['Transfer_Date'].strftime('%Y-%m-%d')}** - Transfer ID: {transfer['Transfer_ID']}
                - From: {transfer['From']} → To: {transfer['To']}
                - Reason: {transfer['Reason']}
                """)
        else:
            st.info("No transfer history for this NFT.")

elif page == "↔️ Transfer QALYs":
    st.title("↔️ Transfer QALY NFTs")
    st.markdown("### Simulate ownership transfer between entities")
    
    # Transfer form
    with st.form("transfer_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            source_entity = st.selectbox("From (Source):", get_entity_options())
            
        with col2:
            dest_entity = st.selectbox("To (Destination):", get_entity_options())
        
        # Get NFTs owned by source entity
        available_nfts = st.session_state.qaly_nfts[
            st.session_state.qaly_nfts['Owner'] == source_entity
        ]['NFT_ID'].tolist()
        
        if available_nfts:
            selected_nft_transfer = st.selectbox("Select NFT to Transfer:", available_nfts)
            transfer_reason = st.text_input("Reason for Transfer:", placeholder="e.g., Program reallocation, Specialist assignment")
            
            submitted = st.form_submit_button("🔄 Execute Transfer")
            
            if submitted and source_entity != dest_entity:
                # Perform transfer
                transfer_id = f"TXN-{str(uuid.uuid4())[:8].upper()}"
                
                # Update ownership
                st.session_state.qaly_nfts.loc[
                    st.session_state.qaly_nfts['NFT_ID'] == selected_nft_transfer, 'Owner'
                ] = dest_entity
                
                # Add to transfer history
                new_transfer = pd.DataFrame({
                    'Transfer_ID': [transfer_id],
                    'NFT_ID': [selected_nft_transfer],
                    'From': [source_entity],
                    'To': [dest_entity],
                    'Transfer_Date': [datetime.now()],
                    'Reason': [transfer_reason if transfer_reason else "Manual Transfer"]
                })
                
                st.session_state.transfer_history = pd.concat([
                    st.session_state.transfer_history, new_transfer
                ], ignore_index=True)
                
                st.success(f"✅ Successfully transferred {selected_nft_transfer} from {source_entity} to {dest_entity}")
                st.balloons()
                
            elif submitted and source_entity == dest_entity:
                st.error("❌ Source and destination cannot be the same entity")
        else:
            st.warning(f"⚠️ No NFTs available for transfer from {source_entity}")
    
    # Recent transfers
    st.markdown("---")
    st.subheader("📊 Transfer Activity")
    
    if len(st.session_state.transfer_history) > 0:
        # Transfer timeline
        fig_timeline = px.line(
            st.session_state.transfer_history.groupby('Transfer_Date').size().reset_index(name='Count'),
            x='Transfer_Date', y='Count',
            title="Transfer Activity Over Time"
        )
        st.plotly_chart(fig_timeline, use_container_width=True)
        
        # All transfers table
        st.dataframe(st.session_state.transfer_history, use_container_width=True)
    else:
        st.info("No transfers recorded yet.")

elif page == "📈 Analytics":
    st.title("📈 QALY Analytics Dashboard")
    st.markdown("### Comprehensive insights into QALY distribution and impact")
    
    # Analytics tabs
    tab1, tab2, tab3 = st.tabs(["🎯 Impact Analysis", "🏥 Ownership Insights", "📊 Program Performance"])
    
    with tab1:
        st.subheader("Disease Impact Distribution")
        
        # QALY by disease and intervention
        impact_analysis = st.session_state.qaly_nfts.groupby(['Disease', 'Intervention'])['QALY_Value'].sum().reset_index()
        fig_sunburst = px.sunburst(
            impact_analysis, 
            path=['Disease', 'Intervention'], 
            values='QALY_Value',
            title="QALY Impact Hierarchy: Disease → Intervention"
        )
        st.plotly_chart(fig_sunburst, use_container_width=True)
        
        # Top interventions
        col1, col2 = st.columns(2)
        with col1:
            top_interventions = st.session_state.qaly_nfts.groupby('Intervention')['QALY_Value'].sum().sort_values(ascending=False).head(5)
            st.markdown("#### 🥇 Top 5 Interventions by QALY")
            for intervention, qaly in top_interventions.items():
                st.markdown(f"**{intervention}:** {qaly:.2f} QALYs")
        
        with col2:
            avg_qaly = st.session_state.qaly_nfts.groupby('Disease')['QALY_Value'].mean().sort_values(ascending=False)
            st.markdown("#### 📊 Average QALY per Disease")
            for disease, avg in avg_qaly.items():
                st.markdown(f"**{disease}:** {avg:.2f} avg QALY")
    
    with tab2:
        st.subheader("Ownership Concentration Analysis")
        
        # Ownership distribution
        ownership_stats = st.session_state.qaly_nfts.groupby('Owner').agg({
            'QALY_Value': ['sum', 'count', 'mean']
        }).round(2)
        ownership_stats.columns = ['Total_QALYs', 'NFT_Count', 'Avg_QALY']
        ownership_stats = ownership_stats.reset_index()
        
        # Ownership concentration chart
        fig_scatter = px.scatter(
            ownership_stats, 
            x='NFT_Count', 
            y='Total_QALYs', 
            size='Avg_QALY',
            hover_name='Owner',
            title="Ownership Analysis: NFT Count vs Total QALY Value",
            labels={'NFT_Count': 'Number of NFTs Owned', 'Total_QALYs': 'Total QALY Value'}
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
        
        # Entity type analysis
        entity_types = {
            'Hospital': ['General Hospital', 'Sunrise Medical Center'],
            'Doctor': ['Dr. Alice Chen', 'Dr. Raj Patel'],
            'Health Authority': ['MOH Singapore', 'WHO Program A']
        }
        
        type_analysis = []
        for entity_type, entities in entity_types.items():
            type_data = st.session_state.qaly_nfts[st.session_state.qaly_nfts['Owner'].isin(entities)]
            if len(type_data) > 0:
                type_analysis.append({
                    'Entity_Type': entity_type,
                    'Total_QALYs': type_data['QALY_Value'].sum(),
                    'Count': len(type_data)
                })
        
        if type_analysis:
            type_df = pd.DataFrame(type_analysis)
            fig_type = px.bar(type_df, x='Entity_Type', y='Total_QALYs', 
                             title="QALY Distribution by Entity Type")
            st.plotly_chart(fig_type, use_container_width=True)
    
    with tab3:
        st.subheader("Program Performance Metrics")
        
        # Program efficiency analysis
        program_stats = st.session_state.qaly_nfts.groupby('Program_Name').agg({
            'QALY_Value': ['sum', 'count', 'mean'],
            'Disease': 'nunique'
        }).round(2)
        program_stats.columns = ['Total_QALYs', 'NFT_Count', 'Avg_QALY', 'Diseases_Targeted']
        program_stats = program_stats.reset_index()
        
        # Program performance matrix
        fig_matrix = px.scatter(
            program_stats,
            x='Avg_QALY',
            y='Total_QALYs',
            size='NFT_Count',
            color='Diseases_Targeted',
            hover_name='Program_Name',
            title="Program Performance Matrix",
            labels={
                'Avg_QALY': 'Average QALY per NFT',
                'Total_QALYs': 'Total Program Impact',
                'Diseases_Targeted': 'Number of Diseases'
            }
        )
        st.plotly_chart(fig_matrix, use_container_width=True)
        
        # Program ranking
        st.markdown("#### 🏆 Program Rankings")
        program_ranking = program_stats.sort_values('Total_QALYs', ascending=False)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**By Total Impact:**")
            for i, (_, row) in enumerate(program_ranking.head(3).iterrows(), 1):
                st.markdown(f"{i}. **{row['Program_Name']}** - {row['Total_QALYs']:.2f} QALYs")
        
        with col2:
            efficiency_ranking = program_stats.sort_values('Avg_QALY', ascending=False)
            st.markdown("**By Efficiency (Avg QALY):**")
            for i, (_, row) in enumerate(efficiency_ranking.head(3).iterrows(), 1):
                st.markdown(f"{i}. **{row['Program_Name']}** - {row['Avg_QALY']:.2f} avg QALY")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.8em;'>
    🏥 QALY Impact Token Management System | Transforming Health Outcomes into Verifiable Assets
</div>
""", unsafe_allow_html=True)