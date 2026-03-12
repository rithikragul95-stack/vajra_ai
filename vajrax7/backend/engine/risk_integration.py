# 4.4 Phase 4 – Risk–Exposure Integration

def calculate_composite_vulnerability_index(srp: float, eg: float, lead_time: float, days_of_delay: float) -> float:
    """
    CVI = SRP × (EG / (L + Del))
    Handling edge cases where L is 0 to avoid division by zero.
    """
    if (lead_time + days_of_delay) <= 0:
        return 0.0
        
    cvi = srp * (eg / (lead_time + days_of_delay))
    return cvi

def generate_decision_logic(inventory_cover: float, lead_time: float, srp: float, days_of_delay: float) -> str:
    """
    IC < L+Del AND SRP > 0.7 → Critical Alert
    IC < L+Del AND 0.4 ≤ SRP ≤ 0.7 → Moderate Alert
    IC ≥ L+Del AND SRP > 0.7 → Preventive Monitoring
    Otherwise → Normal Operations
    """
    effective_lead = lead_time + days_of_delay

    if inventory_cover < effective_lead and srp > 0.7:
        return "Critical Alert"
    elif inventory_cover < effective_lead and 0.4 <= srp <= 0.7:
        return "Moderate Alert"
    elif inventory_cover >= effective_lead and srp > 0.7:
        return "Preventive Monitoring"
    else:
        return "Normal"

def run_phase4(inventory_cover: float, exposure_gap: float, lead_time: float, srp: float, days_of_delay: float) -> dict:
    cvi = calculate_composite_vulnerability_index(srp, exposure_gap, lead_time, days_of_delay)
    alert_level = generate_decision_logic(inventory_cover, lead_time, srp, days_of_delay)
    
    return {
        "composite_vulnerability_index": round(cvi, 4),
        "alert_level": alert_level
    }
