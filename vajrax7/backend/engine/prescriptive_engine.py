# 4.5 Phase 5 – Prescriptive Decision Engine

def calculate_inventory_requirements(lead_time_days: float, daily_demand: float, current_inventory: float) -> dict:
    """
    Required Inventory = L × D
    Additional Inventory Needed = Required Inventory − I
    """
    required_inventory = lead_time_days * daily_demand
    additional_needed = max(0, required_inventory - current_inventory)
    
    return {
        "required_inventory": required_inventory,
        "additional_inventory_needed": additional_needed
    }

def generate_recommendations(inventory_cover: float, lead_time: float, srp: float, exposure_gap: float) -> list:
    """
    Based on exposure and risk values, generate exact prescriptive actions.
    """
    recommendations = []
    
    # Standard exact rules provided by specifications
    if inventory_cover < lead_time and srp > 0.7:
        recommendations.append("Recommend safety stock increase to buffer against high risk.")
        
    if srp > 0.7:
        recommendations.append("Suggest alternate supplier due to high disruption probability.")
        
    if 0 < exposure_gap <= 7:  # "Small" exposure gap defined as > 0 and <= 7 days
        recommendations.append(f"Recommend expedited shipment to cover small exposure gap of {exposure_gap:.1f} days.")
    elif exposure_gap > 7:
        recommendations.append(f"Recommend reallocating procurement volumes to cover large exposure gap of {exposure_gap:.1f} days.")
        
    if not recommendations:
        recommendations.append("Maintain standard procurement cycles.")
        
    return recommendations

def run_phase5(lead_time: float, daily_demand: float, current_inventory: float, 
               inventory_cover: float, srp: float, exposure_gap: float) -> dict:
    
    reqs = calculate_inventory_requirements(lead_time, daily_demand, current_inventory)
    recs = generate_recommendations(inventory_cover, lead_time, srp, exposure_gap)
    
    return {
        "required_inventory": reqs["required_inventory"],
        "additional_inventory_needed": reqs["additional_inventory_needed"],
        "suggested_actions": recs
    }
