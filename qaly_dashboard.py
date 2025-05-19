import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import io

st.set_page_config(layout="wide", page_title="QALY Analysis Dashboard", page_icon="📊")

# Add custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E3A8A;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: bold; 
        color: #2563EB;
        margin-top: 1rem;
    }
    .metric-card {
        background-color: #F3F4F6;
        border-radius: 10px;
        padding: 1rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .plotly-chart {
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #F3F4F6;
        border-radius: 4px 4px 0px 0px;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #DBEAFE;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# ----- DATA LOADING AND PREPARATION -----

@st.cache_data
def load_default_data():
    """Load the default QALY data embedded in the app"""
    data = {
        "ID": ["BP1", "BP2", "BP3", "BP4", "BP5", "LDL1", "LDL2", "LDL3"],
        "Disease": ["Hypertension", "Hypertension", "Hypertension", "Hypertension", "Hypertension", 
                   "Hypercholesterolemia", "Hypercholesterolemia", "Hypercholesterolemia"],
        "Intervention": ["Thiazide diuretics", "ACE Inhibitors", "ARBs", "Calcium Channel Blockers", "Beta Blockers", 
                        "Statins", "Ezetimibe", "PCSK9"],
        "Population": [5000, 4000, 10000, 12000, 4000, 14000, 1000, 100],
        "Non-treated Pop": [3981, 3184, 7962, 9554, 3184, 11672, 834, 83],
        "Treated Pop": [4485, 3654, 9135, 10862, 3555, 12789, 905, 92],
        "Avg QAlY Gain": [1.31, 1.49, 1.58, 1.23, 1.05, 1.41, 1.14, 1.67],
        "Tot QALY Gain": [7699, 7059, 18489, 17809, 5049, 22061, 1295, 186],
        "Cost": [12, 72, 72, 60, 60, 54, 120, 7200]
    }
    return pd.DataFrame(data)

@st.cache_data
def process_data(df):
    """Process the dataframe to add calculated metrics"""
    # Calculate additional metrics
    df['QALY per 1000 People'] = (df['Tot QALY Gain'] * 1000) / df['Population']
    df['Cost per QALY'] = df['Cost'] / df['Avg QAlY Gain']
    df['Treatment Rate %'] = (df['Treated Pop'] / df['Population']) * 100
    df['Intervention Label'] = df['Disease'] + ': ' + df['Intervention']
    df['Total Cost (Thousands)'] = (df['Cost'] * df['Treated Pop']) / 1000
    
    # Add color mapping for consistent colors across charts
    disease_colors = {
        "Hypertension": "#3B82F6",  # Blue
        "Hypercholesterolemia": "#10B981"  # Green
    }
    df['Disease Color'] = df['Disease'].map(disease_colors)
    
    return df

# ----- APP LAYOUT AND FUNCTIONS -----

def render_header():
    """Render the dashboard header"""
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown('<div class="main-header">QALY Analysis Dashboard</div>', unsafe_allow_html=True)
        st.markdown("""
        This dashboard analyzes Quality-Adjusted Life Year (QALY) data across different medical interventions.
        Use the tabs below to explore various visualizations and insights.
        """)
    
    with col2:
        st.write("")
        #upload_data()

def upload_data():
    """Allow users to upload their own CSV data"""
    uploaded_file = st.file_uploader("Upload your own QALY data (CSV)", type="csv", help="Upload a CSV file with the same column structure as the default data",key = "file1")
    
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            required_columns = ["ID", "Disease", "Intervention", "Population", "Non-treated Pop", 
                                "Treated Pop", "Avg QAlY Gain", "Tot QALY Gain", "Cost"]
            
            # Check if all required columns are present
            missing_cols = [col for col in required_columns if col not in df.columns]
            if missing_cols:
                st.error(f"Missing required columns: {', '.join(missing_cols)}")
                return load_default_data()
            
            return df
        except Exception as e:
            st.error(f"Error loading data: {e}")
            return load_default_data()
    else:
        return load_default_data()

def display_key_metrics(df):
    """Display key summary metrics"""
    st.markdown('<div class="sub-header">Key Metrics</div>', unsafe_allow_html=True)
    
    total_qaly = df['Tot QALY Gain'].sum()
    avg_cost_per_qaly = (df['Cost'] * df['Treated Pop']).sum() / total_qaly
    max_qaly_intervention = df.loc[df['Tot QALY Gain'].idxmax()]
    most_efficient = df.loc[df['QALY per 1000 People'].idxmax()]
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total QALY Gain", f"{int(total_qaly):,}")
    
    with col2:
        st.metric("Avg Cost per QALY", f"${avg_cost_per_qaly:.2f}")
    
    with col3:
        st.metric("Highest Impact Intervention", 
                 f"{max_qaly_intervention['Intervention']} ({max_qaly_intervention['Disease']})")
    
    with col4:
        st.metric("Most Efficient Intervention", 
                 f"{most_efficient['Intervention']} ({most_efficient['Disease']})")

def create_total_qaly_chart(df):
    """Bar chart of total QALY gains by intervention"""
    # Sort by Total QALY Gain within disease groups
    df_sorted = df.sort_values(['Disease', 'Tot QALY Gain'], ascending=[True, False])
    
    fig = px.bar(
        df_sorted,
        x='Intervention Label',
        y='Tot QALY Gain',
        color='Disease',
        color_discrete_map=dict(zip(df['Disease'].unique(), df['Disease Color'].unique())),
        labels={'Tot QALY Gain': 'Total QALY Gain', 'Intervention Label': 'Intervention'},
        title='Total QALY Gains by Intervention',
        height=500,
        text='Tot QALY Gain'
    )
    
    fig.update_layout(
        xaxis_title='Intervention',
        yaxis_title='Total QALY Gain',
        legend_title='Disease Category',
        font=dict(family="Arial", size=12),
        hovermode="x unified",
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    fig.update_traces(
        texttemplate='%{text:.0f}',
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>Total QALY Gain: %{y:,.0f}<extra></extra>'
    )
    
    fig.update_xaxes(tickangle=45)
    
    return fig

def create_bubble_chart(df):
    """Bubble chart for population size vs QALY gain"""
    fig = px.scatter(
        df,
        x='Population',
        y='Avg QAlY Gain',
        size='Tot QALY Gain',
        color='Disease',
        color_discrete_map=dict(zip(df['Disease'].unique(), df['Disease Color'].unique())),
        hover_name='Intervention',
        size_max=60,
        labels={
            'Population': 'Population Size',
            'Avg QAlY Gain': 'QALY Gain per Person',
            'Tot QALY Gain': 'Total QALY Gain'
        },
        title='Population Size vs QALY Gain per Person',
        height=500
    )
    
    fig.update_layout(
        xaxis_title='Population Size',
        yaxis_title='QALY Gain per Person',
        legend_title='Disease Category',
        font=dict(family="Arial", size=12),
        hovermode="closest",
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    fig.update_traces(
        hovertemplate='<b>%{hovertext}</b><br>Population: %{x:,}<br>QALY Gain per Person: %{y:.2f}<br>Total QALY Gain: %{marker.size:,.0f}<extra></extra>'
    )
    
    return fig

def create_disease_comparison_chart(df):
    """Stacked bar chart of QALY gains by disease and intervention"""
    # Group by disease and sum the total QALY gains
    disease_df = df.groupby(['Disease', 'Intervention']).agg({
        'Tot QALY Gain': 'sum',
        'Disease Color': 'first'
    }).reset_index()
    
    # Sort within each disease group
    disease_df = disease_df.sort_values(['Disease', 'Tot QALY Gain'], ascending=[True, False])
    
    fig = px.bar(
        disease_df,
        x='Disease',
        y='Tot QALY Gain',
        color='Intervention',
        title='QALY Gains by Disease Category and Intervention',
        height=500,
        barmode='stack',
        labels={
            'Tot QALY Gain': 'Total QALY Gain',
            'Disease': 'Disease Category'
        }
    )
    
    # Customize the color of the bars based on disease
    disease_colors = df[['Disease', 'Disease Color']].drop_duplicates().set_index('Disease')['Disease Color'].to_dict()
    
    fig.update_layout(
        xaxis_title='Disease Category',
        yaxis_title='Total QALY Gain',
        legend_title='Intervention',
        font=dict(family="Arial", size=12),
        coloraxis_showscale=False,
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    # Custom styling for hover
    fig.update_traces(
        hovertemplate='<b>%{x}</b><br>Intervention: %{color}<br>QALY Gain: %{y:,.0f}<extra></extra>'
    )
    
    return fig

def create_efficiency_chart(df):
    """Horizontal bar chart of efficiency (QALY per 1000 people)"""
    # Sort by efficiency metric
    df_sorted = df.sort_values('QALY per 1000 People', ascending=True)
    
    fig = px.bar(
        df_sorted,
        y='Intervention Label',
        x='QALY per 1000 People',
        color='Disease',
        color_discrete_map=dict(zip(df['Disease'].unique(), df['Disease Color'].unique())),
        orientation='h',
        title='Efficiency (QALY Gain per 1,000 People)',
        height=500,
        text='QALY per 1000 People'
    )
    
    fig.update_layout(
        xaxis_title='QALY per 1,000 People',
        yaxis_title='Intervention',
        legend_title='Disease Category',
        font=dict(family="Arial", size=12),
        hovermode="closest",
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    fig.update_traces(
        texttemplate='%{x:.2f}',
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>QALY per 1,000 people: %{x:.2f}<extra></extra>'
    )
    
    return fig

def create_treemap(df):
    """Treemap of relative health impact by intervention"""
    fig = px.treemap(
        df,
        path=[px.Constant("All Interventions"), 'Disease', 'Intervention'],
        values='Tot QALY Gain',
        color='Disease',
        color_discrete_map=dict(zip(df['Disease'].unique(), df['Disease Color'].unique())),
        title='Relative Health Impact by Intervention',
        height=600
    )
    
    fig.update_layout(
        font=dict(family="Arial", size=12),
        margin=dict(l=20, r=20, t=50, b=20)
    )
    
    fig.update_traces(
        hovertemplate='<b>%{label}</b><br>Total QALY Gain: %{value:,.0f}<extra></extra>'
    )
    
    return fig

def create_cost_effectiveness_chart(df):
    """Combined chart showing QALY vs Cost"""
    # Sort by cost-effectiveness (Cost per QALY)
    df_sorted = df.sort_values('Cost per QALY')
    
    # Create subplot with shared x-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Add bar chart for Total QALY Gain
    fig.add_trace(
        go.Bar(
            x=df_sorted['Intervention Label'],
            y=df_sorted['Tot QALY Gain'],
            name='Total QALY Gain',
            marker_color=df_sorted['Disease Color'],
            hovertemplate='<b>%{x}</b><br>Total QALY Gain: %{y:,.0f}<extra></extra>'
        ),
        secondary_y=False
    )
    
    # Add line chart for Cost per QALY
    fig.add_trace(
        go.Scatter(
            x=df_sorted['Intervention Label'],
            y=df_sorted['Cost per QALY'],
            name='Cost per QALY ($)',
            mode='lines+markers',
            line=dict(color='red', width=3),
            marker=dict(size=8),
            hovertemplate='<b>%{x}</b><br>Cost per QALY: $%{y:.2f}<extra></extra>'
        ),
        secondary_y=True
    )
    
    # Customize the layout
    fig.update_layout(
        title_text='QALY Gains vs Cost Effectiveness',
        xaxis_title='Intervention',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        font=dict(family="Arial", size=12),
        height=500,
        hovermode="x unified",
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    # Set y-axes titles
    fig.update_yaxes(title_text="Total QALY Gain", secondary_y=False)
    fig.update_yaxes(title_text="Cost per QALY ($)", secondary_y=True)
    
    fig.update_xaxes(tickangle=45)
    
    return fig

def create_treatment_rate_chart(df):
    """Bar chart showing treatment rates by intervention"""
    fig = px.bar(
        df,
        x='Intervention Label',
        y='Treatment Rate %',
        color='Disease',
        color_discrete_map=dict(zip(df['Disease'].unique(), df['Disease Color'].unique())),
        labels={'Treatment Rate %': 'Treatment Rate (%)', 'Intervention Label': 'Intervention'},
        title='Treatment Rates by Intervention',
        height=500,
        text='Treatment Rate %'
    )
    
    fig.update_layout(
        xaxis_title='Intervention',
        yaxis_title='Treatment Rate (%)',
        legend_title='Disease Category',
        font=dict(family="Arial", size=12),
        hovermode="x unified",
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    fig.update_traces(
        texttemplate='%{text:.1f}%',
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>Treatment Rate: %{y:.1f}%<extra></extra>'
    )
    
    fig.update_xaxes(tickangle=45)
    
    return fig

def create_cost_impact_chart(df):
    """Scatter plot of cost vs impact"""
    fig = px.scatter(
        df,
        x='Cost',
        y='Avg QAlY Gain',
        size='Tot QALY Gain',
        color='Disease',
        color_discrete_map=dict(zip(df['Disease'].unique(), df['Disease Color'].unique())),
        hover_name='Intervention',
        size_max=60,
        labels={
            'Cost': 'Cost per Person ($)',
            'Avg QAlY Gain': 'QALY Gain per Person',
            'Tot QALY Gain': 'Total QALY Gain'
        },
        title='Cost vs Impact Analysis',
        height=500,
        log_x=True  # Using log scale for better visualization with wide cost range
    )
    
    # Add quadrant lines
    x_mean = np.log10(df['Cost'].median())  # For log scale, use median instead of mean and take log
    y_mean = df['Avg QAlY Gain'].mean()
    
    fig.add_shape(
        type="line", line=dict(dash="dash", color="gray"),
        x0=x_mean, y0=df['Avg QAlY Gain'].min(),
        x1=x_mean, y1=df['Avg QAlY Gain'].max()
    )
    
    fig.add_shape(
        type="line", line=dict(dash="dash", color="gray"),
        x0=np.log10(df['Cost'].min()), y0=y_mean,
        x1=np.log10(df['Cost'].max()), y1=y_mean
    )
    
    # Add annotations for quadrants
    fig.add_annotation(
        x=np.log10(df['Cost'].min()) + (x_mean - np.log10(df['Cost'].min()))/2,
        y=y_mean + (df['Avg QAlY Gain'].max() - y_mean)/2,
        text="High Impact<br>Low Cost",
        showarrow=False,
        font=dict(size=12, color="green")
    )
    
    fig.add_annotation(
        x=x_mean + (np.log10(df['Cost'].max()) - x_mean)/2,
        y=y_mean + (df['Avg QAlY Gain'].max() - y_mean)/2,
        text="High Impact<br>High Cost",
        showarrow=False,
        font=dict(size=12, color="blue")
    )
    
    fig.add_annotation(
        x=np.log10(df['Cost'].min()) + (x_mean - np.log10(df['Cost'].min()))/2,
        y=df['Avg QAlY Gain'].min() + (y_mean - df['Avg QAlY Gain'].min())/2,
        text="Low Impact<br>Low Cost",
        showarrow=False,
        font=dict(size=12, color="gray")
    )
    
    fig.add_annotation(
        x=x_mean + (np.log10(df['Cost'].max()) - x_mean)/2,
        y=df['Avg QAlY Gain'].min() + (y_mean - df['Avg QAlY Gain'].min())/2,
        text="Low Impact<br>High Cost",
        showarrow=False,
        font=dict(size=12, color="red")
    )
    
    fig.update_layout(
        xaxis_title='Cost per Person ($) [log scale]',
        yaxis_title='QALY Gain per Person',
        legend_title='Disease Category',
        font=dict(family="Arial", size=12),
        hovermode="closest",
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    # Custom styling for hover
    fig.update_traces(
        hovertemplate='<b>%{hovertext}</b><br>Cost: $%{x:.2f}<br>QALY Gain per Person: %{y:.2f}<br>Total QALY Gain: %{marker.size:,.0f}<extra></extra>'
    )
    
    return fig

def display_data_table(df):
    """Display the data table with calculated metrics"""
    st.markdown('<div class="sub-header">Data Table</div>', unsafe_allow_html=True)
    
    # Allow downloading processed data
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    csv_str = csv_buffer.getvalue()
    
    col1, col2 = st.columns([4, 1])
    with col2:
        st.download_button(
            label="Download Data as CSV",
            data=csv_str,
            file_name="qaly_analysis_data.csv",
            mime="text/csv",
        )
    
    # Define columns to display in the data table
    display_columns = [
        'ID', 'Disease', 'Intervention', 'Population', 'Treated Pop', 
        'Avg QAlY Gain', 'Tot QALY Gain', 'Cost', 'QALY per 1000 People', 
        'Cost per QALY', 'Treatment Rate %'
    ]
    
    # Show the data table with calculated metrics
    st.dataframe(
        df[display_columns].style.format({
            'Population': '{:,.0f}',
            'Treated Pop': '{:,.0f}',
            'Avg QAlY Gain': '{:.2f}',
            'Tot QALY Gain': '{:,.0f}',
            'Cost': '${:.2f}',
            'QALY per 1000 People': '{:.2f}',
            'Cost per QALY': '${:.2f}',
            'Treatment Rate %': '{:.1f}%'
        }),
        height=400,
        use_container_width=True
    )

# ----- MAIN APP -----

def main():
    """Main function to run the Streamlit app"""
    # Render the dashboard header
    render_header()
    
    # Load and process data
    #df_raw = upload_data()
    df_raw = pd.read_csv("QALY_data.csv")
    df = process_data(df_raw)
    
    # Display key metrics section
    display_key_metrics(df)
    
    # Create tabs for different visualizations
    tabs = st.tabs([
        "📊 Impact Analysis", 
        "💰 Cost-Effectiveness", 
        "🔍 Detailed Analysis",
        "📋 Data"
    ])
    
    # Tab 1: Impact Analysis
    with tabs[0]:
        col1, col2 = st.columns(2)
        
        with col1:
            st.plotly_chart(create_total_qaly_chart(df), use_container_width=True)
        
        with col2:
            st.plotly_chart(create_bubble_chart(df), use_container_width=True)
        
        col3, col4 = st.columns(2)
        
        with col3:
            st.plotly_chart(create_efficiency_chart(df), use_container_width=True)
        
        with col4:
            st.plotly_chart(create_disease_comparison_chart(df), use_container_width=True)
    
    # Tab 2: Cost-Effectiveness
    with tabs[1]:
        col1, col2 = st.columns(2)
        
        with col1:
            st.plotly_chart(create_cost_effectiveness_chart(df), use_container_width=True)
        
        with col2:
            st.plotly_chart(create_cost_impact_chart(df), use_container_width=True)
        
        st.plotly_chart(create_treemap(df), use_container_width=True)
    
    # Tab 3: Detailed Analysis
    with tabs[2]:
        st.markdown("""
        This section allows you to compare specific interventions and metrics of interest.
        """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            selected_diseases = st.multiselect(
                "Select Disease Categories",
                options=df['Disease'].unique(),
                default=df['Disease'].unique()
            )
        
        with col2:
            selected_metric = st.selectbox(
                "Select Primary Metric",
                options=[
                    "Tot QALY Gain",
                    "Avg QAlY Gain",
                    "Cost per QALY",
                    "QALY per 1000 People",
                    "Treatment Rate %"
                ],
                index=0
            )
        
        # Filter data based on selection
        if selected_diseases:
            filtered_df = df[df['Disease'].isin(selected_diseases)]
        else:
            filtered_df = df
        
        # Create custom chart based on selections
        metric_labels = {
            "Tot QALY Gain": "Total QALY Gain",
            "Avg QAlY Gain": "Average QALY Gain per Person",
            "Cost per QALY": "Cost per QALY ($)",
            "QALY per 1000 People": "QALY per 1,000 People",
            "Treatment Rate %": "Treatment Rate (%)"
        }
        
        custom_fig = px.bar(
            filtered_df,
            x='Intervention Label',
            y=selected_metric,
            color='Disease',
            color_discrete_map=dict(zip(df['Disease'].unique(), df['Disease Color'].unique())),
            labels={selected_metric: metric_labels[selected_metric], 'Intervention Label': 'Intervention'},
            title=f'{metric_labels[selected_metric]} by Intervention',
            height=500,
            text=selected_metric
        )
        
        custom_fig.update_layout(
            xaxis_title='Intervention',
            yaxis_title=metric_labels[selected_metric],
            legend_title='Disease Category',
            font=dict(family="Arial", size=12),
            hovermode="x unified",
            plot_bgcolor='rgba(0,0,0,0)'
        )
        
        if selected_metric == "Cost per QALY":
            custom_fig.update_traces(
                texttemplate='$%{text:.2f}',
                textposition='outside',
                hovertemplate='<b>%{x}</b><br>Cost per QALY: $%{y:.2f}<extra></extra>'
            )
        elif selected_metric == "Treatment Rate %":
            custom_fig.update_traces(
                texttemplate='%{text:.1f}%',
                textposition='outside',
                hovertemplate='<b>%{x}</b><br>Treatment Rate: %{y:.1f}%<extra></extra>'
            )
        else:
            custom_fig.update_traces(
                texttemplate='%{text:.2f}',
                textposition='outside',
                hovertemplate=f'<b>%{{x}}</b><br>{metric_labels[selected_metric]}: %{{y:.2f}}<extra></extra>'
            )
        
        custom_fig.update_xaxes(tickangle=45)
        
        st.plotly_chart(custom_fig, use_container_width=True)
        
        # Treatment Rate Chart
        st.plotly_chart(create_treatment_rate_chart(filtered_df), use_container_width=True)
    
    # Tab 4: Data
    with tabs[3]:
        display_data_table(df)
        
        st.markdown("""
        ### Data Dictionary
        
        | Column | Description |
        | ------ | ----------- |
        | ID | Unique identifier for each intervention |
        | Disease | Category of disease being treated |
        | Intervention | Specific medical intervention |
        | Population | Total population eligible for intervention |
        | Non-treated Pop | Population not receiving treatment |
        | Treated Pop | Population receiving treatment |
        | Avg QALY Gain | Average Quality-Adjusted Life Year gain per person |
        | Tot QALY Gain | Total QALY gain across the treated population |
        | Cost | Cost per person for the intervention |
        | QALY per 1000 People | QALY gain standardized to 1,000 people |
        | Cost per QALY | Cost effectiveness ratio |
        | Treatment Rate % | Percentage of eligible population receiving treatment |
        """)

if __name__ == "__main__":
    main()
