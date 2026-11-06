def run_proof_of_concept_simulation():
    # ---------------------------------------------------------
    # 1. CORE ARCHITECTURAL ENGINE CONSTANTS
    # ---------------------------------------------------------
    e = 1643.0          # Per capita annual cooking energy demand (MJ)
    g_pet = 4.95        # Macro petrol price shock (+495%)
    pass_through = 0.58 # Transposed cost transmission elasticity
    g_Y = -0.05         # Real income penalty change (-5%)
    
    # Segment Arrays: [Urban Segment, Rural Segment]
    h_segments = [4.50, 5.42]
    N_segments = [15000000.0, 34000000.0]
    
    # Sourced Fuel Constants: [Firewood (wood), Charcoal (char), LPG]
    heating_values = [18.0, 29.0, 46.0]  # MJ per kg
    efficiencies   = [0.18, 0.20, 0.60]  # Thermal stove yield shares
    
    # Baseline National Fuel Share Matrices (Market Distribution from NLSS)
    baseline_shares = [
        [0.10, 0.80],  # Firewood split
        [0.55, 0.15],  # Charcoal split
        [0.35, 0.05]   # LPG split
    ]
    
    # Haulage Price Transmission Fractions
    haulage_shares = [0.00, 0.25, 0.10]
    
    # Environmental Multipliers
    theta = 0.18           # Earth kiln conversion factor
    rho_w = 0.60           # Volumetric wood density (tonnes/m3)
    growing_stock = 100.16 # Official national growing stock density (m3/ha)
    fNRB = [0.05, 0.30]    # Biomass non-renewability fractions [Firewood, Charcoal]
    emission_factor = 281.64 # UNFCCC FREL constant (tCO2e/ha)

    Q0_totals = [0.0, 0.0, 0.0] # Computed absolute baseline fuel flows (kg/year)
    Q1_totals = [0.0, 0.0, 0.0] # Computed post-shock absolute fuel flows (kg/year)
    
    # Calculate fuel price changes based on haulage parameters
    g_prices = [0.0, 0.0, 0.0]
    for fuel_idx in range(3):
        g_prices[fuel_idx] = haulage_shares[fuel_idx] * pass_through * g_pet

    # Main processing loop across segments (Urban vs Rural)
    for seg_idx in range(2):
        h = h_segments[seg_idx]
        N = N_segments[seg_idx]
        
        for fuel_idx in range(3):
            # Equation 1: Baseline individual requirement calculations
            m_energy_share = 1.0 if fuel_idx < 2 else 0.30
            q_baseline = (e * h * m_energy_share) / (heating_values[fuel_idx] * efficiencies[fuel_idx])
            
            # Equation 2: Scaling up to segment baseline quantities
            Q0_segment = N * baseline_shares[fuel_idx][seg_idx] * q_baseline
            Q0_totals[fuel_idx] += Q0_segment
            
            # Equation 4: Process constant-elasticity substitution shifts (Cross-Elasticities)
            if fuel_idx == 0:  # Firewood rebalancing
                net_change = (0.40 * g_prices[2]) + (-0.15 * g_Y)
            elif fuel_idx == 1:  # Charcoal rebalancing
                net_change = (-0.30 * g_prices[1]) + (0.50 * g_prices[2]) + (-0.20 * g_Y)
            else:  # LPG own-price contraction
                net_change = (-0.90 * g_prices[2]) + (0.60 * g_Y)
            
            # Save final demand adjustments back to flow matrix
            Q1_segment = Q0_segment * (1.0 + net_change)
            Q1_totals[fuel_idx] += Q1_segment

    # ---------------------------------------------------------
    # 2. CONVERT FLOW DELTAS TO ECOSYSTEM COVER LOSS
    # ---------------------------------------------------------
    delta_wood_tonnes = (Q1_totals[0] - Q0_totals[0]) / 1000.0
    delta_char_tonnes = (Q1_totals[1] - Q0_totals[1]) / 1000.0
    
    raw_wood_firewood = max(0.0, delta_wood_tonnes)
    raw_wood_charcoal = max(0.0, delta_char_tonnes) / theta
    
    # Equation 6: Spatial area mapping equations
    hectares_lost_wood = raw_wood_firewood / (rho_w * growing_stock)
    hectares_lost_char = raw_wood_charcoal / (rho_w * growing_stock)
    total_spatial_deforestation = hectares_lost_wood + hectares_lost_char
    
    # Equation 7: Carbon footprint capitalization
    emissions_wood = fNRB[0] * hectares_lost_wood * emission_factor
    emissions_char = fNRB[1] * hectares_lost_char * emission_factor
    total_net_emissions_tCO2e = emissions_wood + emissions_char

    # ---------------------------------------------------------
    # 3. QUANTITATIVE REPORT INTERFACE TERMINAL PRINT
    # ---------------------------------------------------------
    print("="*65)
    print("   EFD NIGERIA MODEL PROOF OF CONCEPT: SIMULATION OUTPUTS")
    print("="*65)
    print(f"Baseline Firewood Consumption Vector : {Q0_totals[0]/1e3:14,.1f} Tonnes")
    print(f"Post-Shock Firewood Consumption Vector : {Q1_totals[0]/1e3:14,.1f} Tonnes")
    print(f"Baseline Charcoal Consumption Vector : {Q0_totals[1]/1e3:14,.1f} Tonnes")
    print(f"Post-Shock Charcoal Consumption Vector : {Q1_totals[1]/1e3:14,.1f} Tonnes")
    print("-"*65)
    print(" CORE ECOSYSTEM IMPACT METRIC OUTPUT BOUNDARIES (INDIRECT)")
    print("-"*65)
    print(f"Net Forest Area Lost (Firewood Extraction) : {hectares_lost_wood:14,.2f} Hectares")
    print(f"Net Forest Area Lost (Charcoal Production) : {hectares_lost_char:14,.2f} Hectares")
    print(f"TOTAL LAND-USE DEFORESTATION RUN VALUE    : {total_spatial_deforestation:14,.2f} Hectares")
    print(f"TOTAL COMPUTED CARBON FOOTPRINT PENALTY    : {total_net_emissions_tCO2e:14,.2f} tCO2e")
    print("="*65)

if __name__ == "__main__":
    run_proof_of_concept_simulation()
