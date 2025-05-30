import streamlit as st
import json
import os
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# Custom CSS for professional styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f4e79;
        text-align: center;
        margin-bottom: 2rem;
        border-bottom: 3px solid #1f4e79;
        padding-bottom: 1rem;
    }
    
    .section-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #2c3e50;
        margin-top: 2rem;
        margin-bottom: 1rem;
        border-left: 4px solid #3498db;
        padding-left: 1rem;
    }
    
    .info-box {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .reference-item {
        background-color: #e8f4f8;
        border-left: 4px solid #17a2b8;
        padding: 0.75rem;
        margin: 0.5rem 0;
        border-radius: 4px;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Main header
st.markdown('<h1 class="main-header">QALY NFT Issuance</h1>', unsafe_allow_html=True)

# Initialize session state
if 'calculation_results' not in st.session_state:
    st.session_state.calculation_results = None
if 'selected_data' not in st.session_state:
    st.session_state.selected_data = None

def load_disease_files():
    """Load available disease JSON files from the diseases folder"""
    diseases_folder = "diseases"
    disease_files = []
    
    # Create mock data if folder doesn't exist (for demo purposes)
    if not os.path.exists(diseases_folder):
        st.info("📁 Diseases folder not found. Using demo data for Hypercholesterolemia.")
        return ["Hypercholesterolemia"]
    
    try:
        for file in os.listdir(diseases_folder):
            if file.endswith('.json'):
                disease_name = file.replace('.json', '')
                disease_files.append(disease_name)
        return disease_files
    except Exception as e:
        st.error(f"Error loading disease files: {e}")
        return []

def load_disease_data(disease_name):
    """Load data for a specific disease"""
    # For demo purposes, use the provided Hypercholesterolemia data
    if disease_name == "Hypercholesterolemia":
        return {
            "Statins": {
                "states": ["Healthy", "CVD", "Post-CVD", "Dead"],
                "transition_matrix": [
                    [0.87, 0.012, 0.00, 0.018],
                    [0.00, 0.82, 0.10, 0.08],
                    [0.00, 0.00, 0.91, 0.09],
                    [0.00, 0.00, 0.00, 1.00]
                ],
                "utilities": [0.85, 0.60, 0.70, 0.00],
                "mortality_vector": [0, 0, 0, 1],
                "References": {
                    "utilities": {
                        "literature": "International Systematic Review of Utility Values Associated with Cardiovascular Disease and Reflections on Selecting Evidence for a UK Decision-Analytic Model",
                        "link": "https://pmc.ncbi.nlm.nih.gov/articles/PMC10865747/"
                    },
                    "transition_matrix": {
                        "literature": "The effects of lowering LDL cholesterol with statin therapy in people at low risk of vascular disease: meta-analysis of individual data from 27 randomised trials",
                        "link": "https://www.thelancet.com/journals/lancet/article/PIIS0140-6736(12)60367-5/fulltext"
                    }
                }
            },
            "Baseline": {
                "states": ["Healthy", "CVD", "Post-CVD", "Dead"],
                "transition_matrix": [
                    [0.85, 0.020, 0.00, 0.03],
                    [0.00, 0.80, 0.10, 0.10],
                    [0.00, 0.00, 0.90, 0.10],
                    [0.00, 0.00, 0.00, 1.00]
                ],
                "utilities": [0.85, 0.60, 0.70, 0.00],
                "mortality_vector": [0, 0, 0, 1]
            }
        }
    
    # For actual implementation, load from file
    try:
        with open(f"diseases/{disease_name}.json", 'r') as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Error loading {disease_name} data: {e}")
        return None

def mock_markov_calculation(disease_data, intervention, cohort_size, duration):
    """Mock Markov model calculation (replace with your actual function)"""
    # This is a placeholder - replace with your actual Markov model function
    np.random.seed(42)  # For consistent demo results
    
    # Simulate state transitions over time
    states = disease_data[intervention]["states"]
    n_states = len(states)
    n_cycles = duration
    
    # Initialize state trace
    state_trace = np.zeros((n_cycles + 1, n_states))
    state_trace[0, 0] = cohort_size  # Start all patients in first state
    
    transition_matrix = np.array(disease_data[intervention]["transition_matrix"])
    utilities = np.array(disease_data[intervention]["utilities"])
    
    # Simulate transitions
    for cycle in range(n_cycles):
        current_state = state_trace[cycle]
        next_state = np.dot(current_state, transition_matrix)
        state_trace[cycle + 1] = next_state
    
    # Calculate QALYs and Life Years
    total_qalys = np.sum(state_trace * utilities)
    total_life_years = np.sum(state_trace[:, :-1])  # Exclude dead state
    
    return {
        "Total QALYs": round(total_qalys, 2),
        "Total Life Years": round(total_life_years, 2),
        "Final State Distribution": state_trace[-1],
        "State Trace": state_trace,
        "States": states
    }

def render():
    # Sidebar for inputs
    with st.sidebar:
        st.markdown('<h2 class="section-header">📊 Model Configuration</h2>', unsafe_allow_html=True)
        
        # Disease selection
        available_diseases = load_disease_files()
        selected_disease = st.selectbox("🦠 Select Disease", available_diseases)
        
        # Load disease data
        if selected_disease:
            disease_data = load_disease_data(selected_disease)
            
            if disease_data:
                # Intervention selection (exclude Baseline)
                interventions = [key for key in disease_data.keys() if key != "Baseline"]
                selected_intervention = st.selectbox("💊 Select Intervention", interventions)
                
                st.markdown("---")
                
                # Additional inputs
                st.markdown('<h3 class="section-header">⚙️ Program Parameters</h3>', unsafe_allow_html=True)
                program_name = st.text_input("📋 Program Name", value="Cardiovascular Risk Reduction Study")
                cohort_size = st.number_input("👥 Patient Cohort Size", min_value=100, max_value=100000, value=10000, step=100)
                simulation_duration = st.number_input("📅 Simulation Duration (years)", min_value=1, max_value=50, value=10, step=1)
                
                st.markdown("---")
                
                # Action buttons
                if st.button("🚀 Run Calculation", type="primary"):
                    with st.spinner("Running Markov model calculation..."):
                        results = mock_markov_calculation(disease_data, selected_intervention, cohort_size, simulation_duration)
                        st.session_state.calculation_results = results
                        st.session_state.selected_data = {
                            'disease': selected_disease,
                            'intervention': selected_intervention,
                            'program_name': program_name,
                            'cohort_size': cohort_size,
                            'duration': simulation_duration,
                            'disease_data': disease_data
                        }
                    st.success("✅ Calculation completed successfully!")
                
                if st.button("📤 Submit Results to Management System"):
                    st.info("🔄 Results submission functionality will be implemented in future versions.")

    # Main content area
    col1, col2 = st.columns([2, 1])

    with col1:
        if selected_disease and disease_data and selected_intervention:
            st.markdown('<h2 class="section-header">📚 Model Evidence</h2>', unsafe_allow_html=True)
            
            # Display references
            references = disease_data[selected_intervention].get("References", {})
            
            for param, ref_info in references.items():
                with st.expander(f"📖 {param.title()} References"):
                    st.markdown(f"""
                    <div class="reference-item">
                        <strong>Literature:</strong> {ref_info.get('literature', 'N/A')}<br>
                        <strong>Link:</strong> <a href="{ref_info.get('link', '#')}" target="_blank">{ref_info.get('link', 'N/A')}</a>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Markov model methodology reference
            st.markdown("""
            <div class="reference-item">
                <strong>Model Methodology:</strong> Sonnenberg FA, Beck JR. Markov models in medical decision making: a practical guide. Medical Decision Making. 1993;13(4):322-338.
            </div>
            """, unsafe_allow_html=True)

    with col2:
        if st.session_state.selected_data:
            st.markdown('<h2 class="section-header">Program Information</h2>', unsafe_allow_html=True)
            
            data = st.session_state.selected_data
            st.markdown(f"""
            <div class="info-box">
                <strong>Disease:</strong> {data['disease']}<br>
                <strong>Intervention:</strong> {data['intervention']}<br>
                <strong>Program:</strong> {data['program_name']}<br>
                <strong>Cohort Size:</strong> {data['cohort_size']:,}<br>
                <strong>Duration:</strong> {data['duration']} years
            </div>
            """, unsafe_allow_html=True)

    # Results visualization
    if st.session_state.calculation_results:
        results = st.session_state.calculation_results
        
        st.markdown('<h2 class="section-header">📊 Calculation Results</h2>', unsafe_allow_html=True)
        
        # Key metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <h3>💫 Total QALYs</h3>
                <h2>{results['Total QALYs']}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <h3>📆 Total Life Years</h3>
                <h2>{results['Total Life Years']}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            final_alive = sum(results['Final State Distribution'][:-1])
            st.markdown(f"""
            <div class="metric-card">
                <h3>👥 Final Alive</h3>
                <h2>{int(final_alive):,}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        # Visualizations
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<h3 class="section-header">State Transitions Over Time</h3>', unsafe_allow_html=True)
            
            # State trace visualization
            state_trace = results['State Trace']
            states = results['States']
            
            fig = go.Figure()
            
            for i, state in enumerate(states):
                fig.add_trace(go.Scatter(
                    x=list(range(len(state_trace))),
                    y=state_trace[:, i],
                    mode='lines',
                    name=state,
                    stackgroup='one' if state != 'Dead' else None,
                    line=dict(width=2)
                ))
            
            fig.update_layout(
                title="Patient State Distribution Over Time",
                xaxis_title="Cycle (Years)",
                yaxis_title="Number of Patients",
                hovermode='x unified',
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown('<h3 class="section-header">Final State Distribution</h3>', unsafe_allow_html=True)
            
            # Final state distribution pie chart
            final_dist = results['Final State Distribution']
            
            fig = go.Figure(data=[go.Pie(
                labels=states,
                values=final_dist,
                hole=0.3,
                textinfo='label+percent+value',
                texttemplate='%{label}<br>%{percent}<br>(%{value:,.0f})'
            )])
            
            fig.update_layout(
                title="Distribution of Patients at End of Simulation",
                height=400,
                showlegend=True,
                legend=dict(orientation="v", yanchor="middle", y=0.5)
            )
            
            st.plotly_chart(fig, use_container_width=True)
