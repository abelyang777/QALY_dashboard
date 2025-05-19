import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from qaly_plot import plot_individual_qaly, plot_population_survival, plot_population_qaly


def calculate_qaly_data(params):
    """Calculate all QALY and population data based on input parameters."""
    years = np.arange(params['calculation_period'])
    treatment_end = params['treatment_duration']
    n = len(years)
    initial_population = params['initial_population']

    # --- Utility Arrays ---
    illness_util = np.full(n, params['illness_utility'])
    treatment_util = np.array([
        params['active_treatment_utility'] if i < treatment_end else params['post_treatment_utility']
        for i in range(n)
    ])

    # --- Discounting ---
    disc_illness = 1 / (1 + params['discount_rate_illness']) ** years
    treatment_disc = np.zeros(n)
    for i in range(n):
        if i < treatment_end:
            treatment_disc[i] = 1 / (1 + params['discount_rate_treatment']) ** i
        else:
            treatment_disc[i] = (1 / (1 + params['discount_rate_treatment']) ** treatment_end) * \
                                (1 / (1 + params['discount_rate_post_treatment']) ** (i - treatment_end))

    # --- Mortality Effects ---
    surv_no_trt = np.ones(n)
    surv_trt = np.ones(n)
    pop_no_trt = np.ones(n) * initial_population
    pop_trt = np.ones(n) * initial_population
    
    for i in range(1, n):
        surv_no_trt[i] = surv_no_trt[i-1] * (1 - params['mortality_rate_no_treatment'])
        pop_no_trt[i] = pop_no_trt[0] * surv_no_trt[i]
        
        if i < treatment_end:
            surv_trt[i] = surv_trt[i-1] * (1 - params['mortality_rate_during_treatment'])
        elif i == treatment_end:
            surv_trt[i] = surv_trt[i-1] * (1 - params['mortality_rate_during_treatment'])
        else:
            surv_trt[i] = surv_trt[i-1] * (1 - params['mortality_rate_post_treatment'])
        
        pop_trt[i] = pop_trt[0] * surv_trt[i]

    # --- QALY Calculations ---
    # Individual level
    qaly_ill_vec = illness_util * disc_illness
    qaly_trt_vec = treatment_util * treatment_disc
    
    qaly_ill = np.sum(qaly_ill_vec)
    qaly_trt = np.sum(qaly_trt_vec)
    qaly_gain_individual = qaly_trt - qaly_ill
    
    # Population level
    pop_qaly_ill_vec = illness_util * disc_illness * pop_no_trt
    pop_qaly_trt_vec = treatment_util * treatment_disc * pop_trt
    
    pop_qaly_ill = np.sum(pop_qaly_ill_vec)
    pop_qaly_trt = np.sum(pop_qaly_trt_vec)
    pop_qaly_gain = pop_qaly_trt - pop_qaly_ill
    
    # Create a dictionary to store all calculation results
    results = {
        'years': years,
        'individual': {
            'qaly_ill_vec': qaly_ill_vec,
            'qaly_trt_vec': qaly_trt_vec,
            'qaly_ill': qaly_ill,
            'qaly_trt': qaly_trt,
            'qaly_gain': qaly_gain_individual
        },
        'population': {
            'surv_no_trt': surv_no_trt,
            'surv_trt': surv_trt,
            'pop_no_trt': pop_no_trt,
            'pop_trt': pop_trt,
            'pop_qaly_ill_vec': pop_qaly_ill_vec,
            'pop_qaly_trt_vec': pop_qaly_trt_vec,
            'pop_qaly_ill': pop_qaly_ill,
            'pop_qaly_trt': pop_qaly_trt,
            'pop_qaly_gain': pop_qaly_gain
        },
        'params': params
    }
    
    return results

def export_qaly_timeseries_to_csv(results, filename='qaly_timeseries_output.csv'):
    """Export QALY time series data into a single CSV file."""
    years = results['years']
    data = {
        'Year': years,
        'Individual_QALY_Ill': results['individual']['qaly_ill_vec'],
        'Individual_QALY_Treated': results['individual']['qaly_trt_vec'],
        'Population_Survival_No_Treatment': results['population']['surv_no_trt'],
        'Population_Survival_Treatment': results['population']['surv_trt'],
        'Population_Count_No_Treatment': results['population']['pop_no_trt'],
        'Population_Count_Treatment': results['population']['pop_trt'],
        'Population_QALY_Ill': results['population']['pop_qaly_ill_vec'],
        'Population_QALY_Treated': results['population']['pop_qaly_trt_vec'],
    }
    df = pd.DataFrame(data)
    #df.to_csv(filename, index=False)
    print(f"Exported QALY time series data to '{filename}'")
    print("pop_no_trt:", results["population"]["pop_no_trt"][-1])
    print("pop_trt:", results["population"]["pop_trt"][-1])
    print("qaly_gain:", results["individual"]["qaly_gain"])
    print("pop_qaly_gain:", results["population"]["pop_qaly_gain"])

def run_qaly_analysis(params):
    """Run the complete QALY analysis pipeline."""
    # Calculate all data
    results = calculate_qaly_data(params)
    
    # Create and save plots
    fig1 = plot_individual_qaly(results)
    fig2 = plot_population_survival(results)
    fig3 = plot_population_qaly(results)
    
    return {
        'results': results,
        'figures': [fig1, fig2, fig3],
    }


# 1. STUNTING (Childhood Growth Intervention)
stunting_params = {
    'calculation_period': 50,  # Life expectancy from childhood
    'discount_rate_illness': 0.03,
    'discount_rate_treatment': 0.03,
    'discount_rate_post_treatment': 0.03,
    'illness_utility': 0.70,  # Reduced quality of life due to stunting
    'active_treatment_utility': 0.80,  # During nutritional intervention
    'post_treatment_utility': 0.85,  # Improvement but some lasting effects
    'treatment_duration': 5,  # 5-year nutritional intervention in early childhood
    'mortality_rate_no_treatment': 0.015,  # Higher mortality for stunted children
    'mortality_rate_during_treatment': 0.008,  # Reduced during intervention
    'mortality_rate_post_treatment': 0.01,  # Better than untreated but still elevated
    'initial_population': 1000,
}


import json
input_dict = "BP_parameters.json"
f = open(input_dict, "r")
param_dict = json.load(f)
for i in param_dict:
    print(i)
    params = param_dict[i]
    analysis_results = calculate_qaly_data(params)
    export_qaly_timeseries_to_csv(analysis_results)