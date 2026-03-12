from sqlalchemy import Column, Integer, String, Float, DateTime
import datetime
from database import Base

class Assessment(Base):
    __tablename__ = "assessments"

    id = Column(Integer, primary_key=True, index=True)
    supplier_id = Column(String, index=True)
    location = Column(String, default="Unknown")
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    days_of_delay = Column(Float, default=0.0)
    
    # Internal Exposure
    inventory_cover = Column(Float)
    exposure_gap = Column(Float)
    is_exposed = Column(String)  # Stored as string 'True'/'False' or use Boolean
    
    # External Risk
    supplier_risk_probability = Column(Float)
    risk_classification = Column(String)
    
    # Integration
    cvi_score = Column(Float)
    alert_level = Column(String)
    
    # Prescriptive Actions (JSON String)
    recommendations = Column(String)
