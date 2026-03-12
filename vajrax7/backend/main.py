from fastapi import FastAPI, HTTPException, Depends, File, UploadFile
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
import os
import json
import csv
import io

from database import engine, get_db
import db_models
from models import SystemInput
from engine.inventory_exposure import run_phase2
from engine.predictive_risk import run_phase3
from engine.risk_integration import run_phase4
from engine.prescriptive_engine import run_phase5

# Create tables
db_models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="VAJRA AI System", description="Supply Chain Intelligence Engine")

# CORS middleware to allow static frontend 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/analyze")
def analyze_supply_chain(data: SystemInput, db: Session = Depends(get_db)):
    """
    Phase 1 to Phase 5 Pipeline Execution
    """
    # Phase 2
    phase2_res = run_phase2(data.operational)
    
    # Phase 3
    phase3_res = run_phase3(data.risk, use_ml=True)
    
    # Phase 4
    phase4_res = run_phase4(
        inventory_cover=phase2_res["inventory_cover"],
        exposure_gap=phase2_res["exposure_gap"],
        lead_time=data.operational.supplier_lead_time,
        srp=phase3_res["supplier_risk_probability"],
        days_of_delay=data.operational.days_of_delay
    )
    
    # Phase 5
    phase5_res = run_phase5(
        lead_time=data.operational.supplier_lead_time,
        daily_demand=data.operational.daily_demand,
        current_inventory=data.operational.current_inventory,
        inventory_cover=phase2_res["inventory_cover"],
        srp=phase3_res["supplier_risk_probability"],
        exposure_gap=phase2_res["exposure_gap"]
    )
    
    # Save to Database
    db_assessment = db_models.Assessment(
        supplier_id=data.supplier_id,
        location=data.location,
        days_of_delay=data.operational.days_of_delay,
        inventory_cover=phase2_res["inventory_cover"],
        exposure_gap=phase2_res["exposure_gap"],
        is_exposed=str(phase2_res["is_exposed"]),
        supplier_risk_probability=phase3_res["supplier_risk_probability"],
        risk_classification=phase3_res["risk_classification"],
        cvi_score=phase4_res["composite_vulnerability_index"],
        alert_level=phase4_res["alert_level"],
        recommendations=json.dumps(phase5_res["suggested_actions"])
    )
    db.add(db_assessment)
    db.commit()
    db.refresh(db_assessment)
    
    # Compile Final Report
    return {
        "assessment_id": db_assessment.id,
        "supplier_id": data.supplier_id,
        "inventory_exposure": phase2_res,
        "predictive_risk": phase3_res,
        "vulnerability_integration": phase4_res,
        "prescriptive_decision": phase5_res
    }

@app.get("/api/suppliers")
def get_suppliers(db: Session = Depends(get_db)):
    """
    Returns the latest risk assessment for each supplier.
    """
    # SQLite doesn't support generic DISTINCT ON, so we do grouped queries
    # or simple subquery for max id per supplier.
    subquery = db.query(db_models.Assessment.supplier_id, func.max(db_models.Assessment.id).label('max_id')).group_by(db_models.Assessment.supplier_id).subquery()
    
    latest_assessments = db.query(db_models.Assessment).join(
        subquery,
        (db_models.Assessment.supplier_id == subquery.c.supplier_id) & 
        (db_models.Assessment.id == subquery.c.max_id)
    ).all()
    
    return latest_assessments

@app.get("/api/suppliers/{supplier_id}/history")
def get_supplier_history(supplier_id: str, db: Session = Depends(get_db)):
    """
    Returns the historical risk assessments for a specific supplier, ordered by time.
    """
    history = db.query(db_models.Assessment).filter(
        db_models.Assessment.supplier_id == supplier_id
    ).order_by(db_models.Assessment.timestamp.asc()).all()
    
    if not history:
        raise HTTPException(status_code=404, detail="Supplier not found")
        
    return history

@app.post("/api/upload")
async def upload_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Parses a CSV uploaded by the user, runs the 5-phase algorithm on each row, 
    and saves to the database. Expects exact header names matching SystemInput fields.
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed.")
        
    content = await file.read()
    decoded = content.decode('utf-8')
    reader = csv.DictReader(io.StringIO(decoded))
    
    processed = 0
    errors = 0
    
    # Required keys mapping back to our models
    for row in reader:
        try:
            # Reconstruct SystemInput schema from CSV
            parsed_data = SystemInput(
                supplier_id=row['supplier_id'],
                location=row.get('location', 'Unknown'),
                operational={
                    'daily_demand': float(row['daily_demand']),
                    'current_inventory': float(row['current_inventory']),
                    'safety_stock': float(row['safety_stock']),
                    'supplier_lead_time': float(row['supplier_lead_time']),
                    'days_of_delay': float(row.get('days_of_delay', 0.0))
                },
                risk={
                    'flood_severity': float(row['flood_severity']),
                    'earthquake_risk': float(row['earthquake_risk']),
                    'political_instability': float(row['political_instability']),
                    'transportation_disruption': float(row['transportation_disruption']),
                    'regional_infrastructure_risk': float(row['regional_infrastructure_risk'])
                }
            )
            
            # Execute Phase Pipeline
            phase2_res = run_phase2(parsed_data.operational)
            phase3_res = run_phase3(parsed_data.risk, use_ml=True)
            phase4_res = run_phase4(
                inventory_cover=phase2_res["inventory_cover"],
                exposure_gap=phase2_res["exposure_gap"],
                lead_time=parsed_data.operational.supplier_lead_time,
                srp=phase3_res["supplier_risk_probability"],
                days_of_delay=parsed_data.operational.days_of_delay
            )
            phase5_res = run_phase5(
                lead_time=parsed_data.operational.supplier_lead_time,
                daily_demand=parsed_data.operational.daily_demand,
                current_inventory=parsed_data.operational.current_inventory,
                inventory_cover=phase2_res["inventory_cover"],
                srp=phase3_res["supplier_risk_probability"],
                exposure_gap=phase2_res["exposure_gap"]
            )
            
            # Save Database record
            db_assessment = db_models.Assessment(
                supplier_id=parsed_data.supplier_id,
                location=parsed_data.location,
                days_of_delay=parsed_data.operational.days_of_delay,
                inventory_cover=phase2_res["inventory_cover"],
                exposure_gap=phase2_res["exposure_gap"],
                is_exposed=str(phase2_res["is_exposed"]),
                supplier_risk_probability=phase3_res["supplier_risk_probability"],
                risk_classification=phase3_res["risk_classification"],
                cvi_score=phase4_res["composite_vulnerability_index"],
                alert_level=phase4_res["alert_level"],
                recommendations=json.dumps(phase5_res["suggested_actions"])
            )
            db.add(db_assessment)
            processed += 1
            
        except Exception as e:
            # If a row is malformed, increment error and continue
            print(f"Error processing row: {row}. Error: {e}")
            errors += 1
            
    db.commit()
    
    return {"message": f"Batch process complete. {processed} successful, {errors} errors."}

@app.get("/api/export")
def export_suppliers_pdf(db: Session = Depends(get_db)):
    """
    Exports the latest risk assessment for each supplier as a PDF file.
    """
    latest_assessments = get_suppliers(db)
    
    if not latest_assessments:
        raise HTTPException(status_code=404, detail="No data available to export")
        
    from fpdf import FPDF
    
    pdf = FPDF()
    pdf.add_page(orientation='L')  # Landscape for better fit
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(280, 10, txt="VAJRA AI Supplier Risk Report", ln=True, align='C')
    pdf.ln(10)
    
    pdf.set_font("Arial", 'B', 10)
    
    # Set up columns for PDF table
    headers = ["Supplier ID", "Timestamp", "Inv Cover (Days)", "Exp Gap (Days)", "Risk (SRP)", "Class.", "CVI Score", "Alert Level"]
    col_widths = [30, 45, 30, 30, 25, 25, 25, 55]
    
    # Draw Headers
    for i, head in enumerate(headers):
        pdf.cell(col_widths[i], 10, txt=head, border=1, align='C')
    pdf.ln()
    
    pdf.set_font("Arial", size=9)
    for row in latest_assessments:
        pdf.cell(col_widths[0], 10, txt=str(row.supplier_id), border=1, align='C')
        pdf.cell(col_widths[1], 10, txt=row.timestamp.strftime("%Y-%m-%d %H:%M"), border=1, align='C')
        pdf.cell(col_widths[2], 10, txt=f"{row.inventory_cover:.2f}", border=1, align='C')
        pdf.cell(col_widths[3], 10, txt=f"{row.exposure_gap:.2f}", border=1, align='C')
        pdf.cell(col_widths[4], 10, txt=f"{row.supplier_risk_probability:.2f}", border=1, align='C')
        pdf.cell(col_widths[5], 10, txt=str(row.risk_classification), border=1, align='C')
        pdf.cell(col_widths[6], 10, txt=f"{row.cvi_score:.3f}", border=1, align='C')
        pdf.cell(col_widths[7], 10, txt=str(row.alert_level), border=1, align='C')
        pdf.ln()
        
    # Output to PDF bytes
    pdf_bytes = pdf.output(dest="S").encode("latin-1")
    
    return StreamingResponse(
        iter([pdf_bytes]),
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=vajra_risk_report.pdf"}
    )

# Ensure the frontend directory exists  
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
os.makedirs(frontend_dir, exist_ok=True)

# Mount the vanilla frontend directory to be served on root '/'
app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")
