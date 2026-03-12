from pydantic import BaseModel, Field

# Phase 1: Data Acquisition and Input Modeling

class OperationalInputs(BaseModel):
    daily_demand: float = Field(..., description="Daily Demand (D)")
    current_inventory: float = Field(..., description="Current Inventory (I)")
    safety_stock: float = Field(..., description="Safety Stock (SS)")
    supplier_lead_time: float = Field(..., description="Supplier Lead Time (L) in days")
    days_of_delay: float = Field(0.0, description="Days of Delay (Del)")

class RiskFeatureInputs(BaseModel):
    # Normalized to [0,1]
    flood_severity: float = Field(..., ge=0, le=1, description="Flood Severity (F)")
    earthquake_risk: float = Field(..., ge=0, le=1, description="Earthquake Risk (E)")
    political_instability: float = Field(..., ge=0, le=1, description="Political Instability (P)")
    transportation_disruption: float = Field(..., ge=0, le=1, description="Transportation Disruption (T)")
    regional_infrastructure_risk: float = Field(..., ge=0, le=1, description="Regional Infrastructure Risk (R)")

class SystemInput(BaseModel):
    supplier_id: str
    location: str = Field("Unknown", description="Supplier Location")
    operational: OperationalInputs
    risk: RiskFeatureInputs
