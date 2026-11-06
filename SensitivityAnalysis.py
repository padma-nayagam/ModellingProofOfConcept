import random

def run_sensitivity_analysis_monte_carlo(iterations=1000):
    # ---------------------------------------------------------
    # 1. FIXED ENGINE BASELINE PARAMETERS
    # ---------------------------------------------------------
    e = 1643.0          
    g_pet = 4.95        
    pass_through = 0.58 
    g_Y = -0.05         
    
    h_segments = [4.50, 5.42]
    N_segments = [15000000.0, 34000000.0]
    heating_values = [18.0, 29.0, 46.0]
    efficiencies   = [0.18, 0.20, 0.60]
    
    baseline_shares = [
        [0.10, 0.80],  
        [0.55, 0.15],  
        [0.35, 0.05]   
    ]
    
    haulage_shares = [0.00, 0.25, 0.10]
    rho_w = 0.60           
    growing_stock = 100.16 
    fNRB_wood = 0.05       
    emission_factor = 281.64 

    total_deforestation_results = []
    total_emissions_results = []

    # ---------------------------------------------------------
    # 2. RUNTIME SIMULATION LOOPS (DEMAND VECTORS)
    # ---------------------------------------------------------
    Q0_totals = [0.0, 0.0, 0.0]
    Q1_totals = [0.0, 0.0, 0.0]
    g_prices = [0.0, 0.0, 0.0]
    
    for i in range(3):
        g_prices[i] = haulage_shares[i] * pass_through * g_pet

    for seg_idx in range(2):
        h = h_segments[seg_idx]
        N = N_segments[seg_idx]
        
        for f_idx in range(3):
            m_share = 1.0 if f_idx < 2 else 0.30
            q_base = (e * h * m_share) / (heating_values[f_idx] * efficiencies[f_idx])
            Q0_seg = N * baseline_shares[f_idx][seg_idx] * q_base
            Q0_totals[f_idx] += Q0_seg
            
            if f_idx == 0:
                net_change = (0.40 * g_prices[2]) + (-0.15 * g_Y)
            elif f_idx == 1:
                net_change = (-0.30 * g_prices[1]) + (0.50 * g_prices[2]) + (-0.20 * g_Y)
            else:
                net_change = (-0.90 * g_prices[2]) + (0.60 * g_Y)
                
            Q1_totals[f_idx] += Q0_seg * (1.0 + net_change)

    delta_wood_t = (Q1_totals[0] - Q0_totals[0]) / 1000.0
    delta_char_t = (Q1_totals[1] - Q0_totals[1]) / 1000.0

    # ---------------------------------------------------------
    # 3. MONTE CARLO STOCHASTIC UNCERTAINTY SAMPLING
    # ---------------------------------------------------------
    for _ in range(iterations):
        # Sample fNRB across continuous bounds [0.24 to 0.36]
        sampled_fNRB_char = random.uniform(0.24, 0.36)
        # Sample conversion yield variance [0.16 to 0.22]
        sampled_theta = random.uniform(0.16, 0.22)
        
        raw_wood_firewood = max(0.0, delta_wood_t)
        raw_wood_charcoal = max(0.0, delta_char_t) / sampled_theta
        
        ha_lost_wood = raw_wood_firewood / (rho_w * growing_stock)
        ha_lost_char = raw_wood_charcoal / (rho_w * growing_stock)
        iter_deforestation = ha_lost_wood + ha_lost_char
        
        emissions_wood = fNRB_wood * ha_lost_wood * emission_factor
        emissions_char = sampled_fNRB_char * ha_lost_char * emission_factor
        iter_emissions = emissions_wood + emissions_char
        
        total_deforestation_results.append(iter_deforestation)
        total_emissions_results.append(iter_emissions)

    # ---------------------------------------------------------
    # 4. STATISTICAL ANALYSIS INTERFACE (CONFIDENCE METRICS)
    # ---------------------------------------------------------
    total_deforestation_results.sort()
    total_emissions_results.sort()
    
    median_deforestation = total_deforestation_results[int(iterations * 0.5)]
    median_emissions = total_emissions_results[int(iterations * 0.5)]
    
    ci_lower_def = total_deforestation_results[int(iterations * 0.025)]
    ci_upper_def = total_deforestation_results[int(iterations * 0.975)]
    ci_lower_em = total_emissions_results[int(iterations * 0.025)]
    ci_upper_em = total_emissions_results[int(iterations * 0.975)]

    print("="*65)
    print("   EFD NIGERIA: MONTE CARLO SENSITIVITY RUN ANALYSIS")
    print(f"   [Executing {iterations} Randomized Stochastic Parameter Permutations]")
    print("="*65)
    print(" METRIC DEFORESTATION OUTPUT BOUNDS (HECTARES)")
    print("-"*65)
    print(f" Minimum Sampled Hectares Cleared    : {total_deforestation_results[0]:14,.2f} ha")
    print(f" Median Expected Deforestation Value : {median_deforestation:14,.2f} ha")
    print(f" Maximum Sampled Hectares Cleared    : {total_deforestation_results[-1]:14,.2f} ha")
    print(f" 95% Confidence Bounds Interval      : [{ci_lower_def:,.2f} to {ci_upper_def:,.2f}] ha")
    print("-"*65)
    print(" METRIC CARBON LOSS EMISSIONS TRACKING (tCO2e)")
    print("-"*65)
    print(f" Minimum Sampled Net Emissions       : {total_emissions_results[0]:14,.2f} tCO2e")
    print(f" Median Expected Atmospheric Carbon  : {median_emissions:14,.2f} tCO2e")
    print(f" Maximum Sampled Net Emissions       : {total_emissions_results[-1]:14,.2f} tCO2e")
    print(f" 95% Confidence Bounds Interval      : [{ci_lower_em:,.2f} to {ci_upper_em:,.2f}] tCO2e")
    print("="*65)

if __name__ == "__main__":
    run_sensitivity_analysis_monte_carlo()
