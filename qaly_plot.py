import numpy as np
import matplotlib.pyplot as plt
import pandas as pd


def plot_individual_qaly(results):
    """Create and save individual QALY comparison plot."""
    years = results['years']
    qaly_ill_vec = results['individual']['qaly_ill_vec']
    qaly_trt_vec = results['individual']['qaly_trt_vec']
    qaly_gain = results['individual']['qaly_gain']
    params = results['params']
    treatment_end = params['treatment_duration']
    
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.plot(years, qaly_ill_vec, 'r-', label='No Treatment')
    ax.plot(years, qaly_trt_vec, 'g-', label='Treatment')
    ax.fill_between(years, qaly_ill_vec, qaly_trt_vec,
                   where=qaly_trt_vec > qaly_ill_vec,
                   facecolor='green', alpha=0.3, label=f'QALY Gain: {qaly_gain:.2f}')
    ax.axvline(treatment_end, color='blue', linestyle='--', alpha=0.5)
    ax.text(treatment_end / 2, 0.05, 'Treatment Period', ha='center', backgroundcolor='lightblue', alpha=0.7)
    if treatment_end < params['calculation_period']:
        ax.text((treatment_end + params['calculation_period']) / 2, 0.05,
               'Post-Treatment Period', ha='center', backgroundcolor='lightyellow', alpha=0.7)

    ax.set(xlabel='Years', ylabel='Discounted Utility', title='Individual QALY Comparison')
    ax.legend(loc='upper right')
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, params['calculation_period'])
    ax.set_ylim(0, 1.1)
    plt.tight_layout()
    
    #fig.savefig('individual_qaly_comparison.png')
    return fig

def plot_population_survival(results):
    """Create and save population survival comparison plot."""
    years = results['years']
    pop_no_trt = results['population']['pop_no_trt']
    pop_trt = results['population']['pop_trt']
    lives_saved = pop_trt[-1] - pop_no_trt[-1]
    params = results['params']
    treatment_end = params['treatment_duration']
    initial_population = params['initial_population']
    
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.plot(years, pop_no_trt, 'r-', label='No Treatment')
    ax.plot(years, pop_trt, 'g-', label='Treatment')
    ax.fill_between(years, pop_no_trt, pop_trt,
                   where=pop_trt > pop_no_trt,
                   facecolor='green', alpha=0.3, label=f'Lives Saved at End: {lives_saved:.0f}')
    ax.axvline(treatment_end, color='blue', linestyle='--', alpha=0.5)
    ax.text(treatment_end / 2, min(pop_no_trt[-1], pop_trt[-1])/2, 'Treatment Period', 
            ha='center', backgroundcolor='lightblue', alpha=0.7)
    if treatment_end < params['calculation_period']:
        ax.text((treatment_end + params['calculation_period']) / 2, min(pop_no_trt[-1], pop_trt[-1])/2,
               'Post-Treatment Period', ha='center', backgroundcolor='lightyellow', alpha=0.7)

    ax.set(xlabel='Years', ylabel='Surviving Population', title='Population Survival Comparison with Mortality')
    ax.legend(loc='upper right')
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, params['calculation_period'])
    ax.set_ylim(0, initial_population * 1.1)
    plt.tight_layout()
    
    #fig.savefig('population_survival_comparison.png')
    return fig

def plot_population_qaly(results):
    """Create and save population QALY comparison plot."""
    years = results['years']
    pop_qaly_ill_vec = results['population']['pop_qaly_ill_vec']
    pop_qaly_trt_vec = results['population']['pop_qaly_trt_vec']
    pop_qaly_gain = results['population']['pop_qaly_gain']
    params = results['params']
    treatment_end = params['treatment_duration']
    
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.plot(years, pop_qaly_ill_vec, 'r-', label='No Treatment')
    ax.plot(years, pop_qaly_trt_vec, 'g-', label='Treatment')
    ax.fill_between(years, pop_qaly_ill_vec, pop_qaly_trt_vec,
                   where=pop_qaly_trt_vec > pop_qaly_ill_vec,
                   facecolor='green', alpha=0.3, label=f'Total Population QALY Gain: {pop_qaly_gain:.0f}')
    ax.axvline(treatment_end, color='blue', linestyle='--', alpha=0.5)

    # Get y-axis limits first
    ymin, ymax = min(min(pop_qaly_ill_vec), min(pop_qaly_trt_vec)), max(max(pop_qaly_ill_vec), max(pop_qaly_trt_vec))

    # Use a fraction of ymax for label placement to ensure visibility
    text_y_pos = ymin + (ymax - ymin) * 0.3

    # Now place the labels more reliably
    ax.text(treatment_end / 2, text_y_pos, 'Treatment Period', 
            ha='center', backgroundcolor='lightblue', alpha=0.7)

    if treatment_end < params['calculation_period']:
        ax.text((treatment_end + params['calculation_period']) / 2, text_y_pos,
                'Post-Treatment Period', ha='center', backgroundcolor='lightyellow', alpha=0.7)

    ax.set(xlabel='Years', ylabel='Population QALYs', title='Population Total QALY Comparison')
    ax.legend(loc='upper right')
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, params['calculation_period'])
    plt.tight_layout()
    
    #fig.savefig('population_total_qaly_comparison.png')
    return fig