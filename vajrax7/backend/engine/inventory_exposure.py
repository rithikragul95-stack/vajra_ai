# 4.2 Phase 2 – Inventory Exposure Modeling
from models import OperationalInputs

def calculate_inventory_cover(inputs: OperationalInputs) -> float:
    """
    IC = (I − SS) / D
    Inventory Cover represents the number of days operations can continue without replenishment.
    """
    if inputs.daily_demand <= 0:
        return float('inf')  # No demand
    
    ic = (inputs.current_inventory - inputs.safety_stock) / inputs.daily_demand
    # Ensure IC doesn't drop below 0 contextually, but equation allows it physically 
    # if inventory is somehow below safety stock (deficit).
    return ic

def calculate_exposure_gap(inputs: OperationalInputs, inventory_cover: float) -> float:
    """
    EG = L − IC
    If EG > 0, the organization is exposed to potential disruption.
    """
    eg = inputs.supplier_lead_time - inventory_cover
    return eg

def run_phase2(inputs: OperationalInputs) -> dict:
    ic = calculate_inventory_cover(inputs)
    eg = calculate_exposure_gap(inputs, ic)
    
    return {
        "inventory_cover": round(ic, 2),
        "exposure_gap": round(eg, 2),
        "is_exposed": eg > 0
    }
