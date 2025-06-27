import streamlit as st
import plotly.express as px
import numpy as np

def show_references_from_dict(references: dict, section_title: str = "References"):
    with st.expander(section_title):
        for name, link in references.items():
            st.markdown(f"- [{name}]({link})")

def render():
    dataset = st.session_state.dataset
    qaly_df = st.session_state.qaly_df
    nft_df = st.session_state.nft_df
    time_series_df = st.session_state.time_series_df
    color_map = st.session_state.color_map
    disease_colors = color_map
    intervention_colors = color_map

    # Header
    st.markdown("""
    <div class='main-header'>
        <h1>QALY NFT Management Platform</h1>
        <p>Quality-Adjusted Life Years from Risk Reduction Programs</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_qaly = qaly_df['Tot QALY Gain'].sum()
        st.metric(
            label="Total QALYs Generated",
            value=f"{total_qaly:,}",
            #delta=f"+{random.randint(100, 500)} this month"
        )
    
    with col2:
        total_nfts = len(nft_df)
        st.metric(
            label="Total NFTs Minted",
            value=f"{total_nfts:,}",
            #delta=f"+{random.randint(50, 200)} this week"
        )
    
    with col3:
        active_programs = len(qaly_df)
        st.metric(
            label="Active Programs",
            value=active_programs,
            #delta="2 new programs"
        )
    
    with col4:
        avg_cost_effectiveness = qaly_df['Cost per QALY'].mean()
        st.metric(
            label="Avg Cost per QALY",
            value=f"${avg_cost_effectiveness:.0f}",
            #delta="-5% improvement"
        )
    
    st.markdown("---")
    
    # Overview charts
    # Add drill-down controls at the top
    disease_summary = qaly_df.groupby('Disease')[['Tot QALY Gain','Patient']].sum().reset_index()
    #st.subheader("View Controls")
    drill_down_option = st.radio(
        "Select View Mode:",
        ["By Disease", "By Treatment"],
        horizontal=True,
        help="Choose how to display the data across both charts"
    )

    # Create two columns for the charts
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("QALY Attribution")
        
        if drill_down_option == "By Disease":
            # Main pie chart showing diseases
            fig1 = px.pie(
                disease_summary, 
                values='Tot QALY Gain', 
                names='Disease',
                color='Disease',
                color_discrete_map=disease_colors,
                title="Total QALYs by Disease Category"
            )
            fig1.update_traces(
                textposition='inside', 
                textinfo='percent+label',
                textfont_size=12,
                hovertemplate="<b>%{label}</b><br>" +
                             "Total QALY Gain: %{value}<br>" +
                             "Patients: %{customdata[0]:,}<br>" +
                             "Percentage: %{percent}<br>" +
                             "<extra></extra>",
                customdata=disease_summary[['Patient']]
            )
            fig1.update_layout(
                showlegend=True,
                height=400,
                font=dict(size=10)
            )
            st.plotly_chart(fig1, use_container_width=True)
            
        else:
            # Drill-down section
            selected_disease = st.selectbox(
                "Select a disease to drill down:",
                options=disease_summary['Disease'].tolist(),
                index=0
            )
            
            # Filter data for selected disease
            filtered_data = qaly_df[qaly_df['Disease'] == selected_disease]
            
            # Create drill-down pie chart with consistent colors
            fig1 = px.pie(
                filtered_data,
                values='Tot QALY Gain',
                names='Intervention',
                color='Intervention',
                color_discrete_map=intervention_colors,
                title=f"QALY Distribution: {selected_disease} Interventions"
            )
            fig1.update_traces(
                textposition='inside', 
                textinfo='percent+label',
                textfont_size=10,
                hovertemplate="<b>%{label}</b><br>" +
                             "QALY Gain: %{value}<br>" +
                             "Patients: %{customdata[0]:,}<br>" +
                             "Percentage: %{percent}<br>" +
                             "<extra></extra>",
                customdata=filtered_data[['Patient']]
            )
            fig1.update_layout(
                showlegend=True,
                height=400,
                font=dict(size=9)
            )
            st.plotly_chart(fig1, use_container_width=True)

    with col2:
        st.subheader("Cost-Effectiveness Analysis")
        
        if drill_down_option == "By Disease":
            # Scatter plot colored by disease
            fig2 = px.scatter(
                qaly_df,
                x='Avg QALY Gain',
                y='Cost per QALY',
                size='Tot QALY Gain',
                color='Disease',
                color_discrete_map=disease_colors,
                hover_name='Program Name',
                hover_data={'Patient': ':,', 'Cost': ':$,'},
                title="Cost per QALY vs Average QALY Gain (by Disease)",
                labels={
                    'Cost per QALY': 'Cost per QALY ($)', 
                    'Avg QALY Gain': 'Average QALY Gain per Patient',
                    'Tot QALY Gain': 'Total QALY Gain'
                }
            )
            
        else:
            # Filter data for selected disease and color by intervention
            filtered_data = qaly_df[qaly_df['Disease'] == selected_disease]
            
            fig2 = px.scatter(
                filtered_data,
                x='Avg QALY Gain',
                y='Cost per QALY',
                size='Tot QALY Gain',
                color='Intervention',
                color_discrete_map=intervention_colors,
                hover_name='Program Name',
                hover_data={'Patient': ':,', 'Cost': ':$,'},
                title=f"Cost-Effectiveness: {selected_disease} Interventions",
                labels={
                    'Cost per QALY': 'Cost per QALY ($)', 
                    'Avg QALY Gain': 'Average QALY Gain per Patient',
                    'Tot QALY Gain': 'Total QALY Gain'
                }
            )
        
        # Update scatter plot layout
        fig2.update_traces(
            hovertemplate="<b>%{hovertext}</b><br>" +
                         "Avg QALY Gain: %{x}<br>" +
                         "Cost per QALY: $%{y:,.0f}<br>" +
                         "Total QALY Gain: %{marker.size}<br>" +
                         "Patients: %{customdata[0]:,}<br>" +
                         "Total Cost: %{customdata[1]}<br>" +
                         "<extra></extra>"
        )
        fig2.update_layout(
            showlegend=True,
            height=400,
            yaxis_type="log",  # Log scale for better visualization of cost differences
            font=dict(size=10)
        )
        
        st.plotly_chart(fig2, use_container_width=True)

    import json
    f = open(dataset + "references.json","r", encoding = 'utf-8-sig')
    references = json.load(f)
    show_references_from_dict(references)