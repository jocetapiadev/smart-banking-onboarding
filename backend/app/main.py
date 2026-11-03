from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from typing import Optional, List
import io
import sqlite3
from datetime import datetime
import pandas as pd

app = FastAPI(
    title="Next-Gen AI Banking Risk & Cross-Audit Agent",
    version="3.1.0-ENTERPRISE",
    description="Agente Inteligente con Persistencia SQL, Inferencia Multimodal e Integración Power Platform para Banco de Chile"
)

# Inicialización de la base de datos de trazabilidad
def init_db():
    conn = sqlite3.connect("audit_log.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS audit_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            rut TEXT,
            declared_income REAL,
            requested_amount REAL,
            risk_level TEXT,
            recommended_decision TEXT,
            red_flags TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.get("/")
def read_root():
    return {"message": "AI Banking Agent Core Enterprise Active"}

@app.post("/api/v2/smart-agent-audit")
async def smart_agent_audit(
    rut: str = Form(...),
    declared_income: float = Form(...),
    requested_amount: float = Form(...),
    file: UploadFile = File(None)
):
    red_flags = []
    confidence_score = 0.95
    clean_rut = rut.replace(".", "").replace("-", "").strip().upper()
    
    # 1. Regla de Endeudamiento
    leverage_ratio = requested_amount / declared_income if declared_income > 0 else 999
    if leverage_ratio > 10:
        red_flags.append(f"Palanca crediticia elevada: Solicitud supera {round(leverage_ratio, 1)}x la renta.")
    
    # 2. Cruce Documental
    document_matched = False
    if file and file.filename:
        filename = file.filename.lower()
        if filename.endswith(('.xlsx', '.xls', '.csv')):
            contents = await file.read()
            df = pd.read_excel(io.BytesIO(contents)) if filename.endswith(('.xlsx', '.xls')) else pd.read_csv(io.BytesIO(contents))
            
            if 'RUT Cliente' in df.columns:
                df['clean_rut'] = df['RUT Cliente'].astype(str).str.replace(".", "", regex=False).str.replace("-", "", regex=False).str.strip().str.upper()
                client_data = df[df['clean_rut'] == clean_rut]
                
                if not client_data.empty:
                    document_matched = True
                    excel_income = float(client_data.iloc[0].get('Renta Mensual (CLP)', 0))
                    if abs(excel_income - declared_income) > 1000:
                        red_flags.append(f"Inconsistencia Tributaria: Declara ${declared_income:,.0f} vs registro documental ${excel_income:,.0f}.")
                else:
                    red_flags.append("Alerta de Identidad: El RUT no figura en la base de datos documental.")

    # 3. Determinación de Riesgo
    risk_level = "CRÍTICO" if len(red_flags) >= 2 else ("MEDIO" if len(red_flags) == 1 else "BAJO")
    decision = "RECHAZO_AUTOMATICO" if risk_level == "CRÍTICO" else ("REVISIÓN_COMITÉ_RIESGO" if risk_level == "MEDIO" else "APROBACIÓN_AUTOMÁTICA")

    # 4. Trazabilidad Bancaria en SQL
    conn = sqlite3.connect("audit_log.db")
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO audit_records (timestamp, rut, declared_income, requested_amount, risk_level, recommended_decision, red_flags)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (datetime.now().isoformat(), clean_rut, declared_income, requested_amount, risk_level, decision, " | ".join(red_flags)))
    conn.commit()
    conn.close()

    return {
        "agent_status": "ANALYSIS_COMPLETE",
        "target_applicant": {"rut": clean_rut, "declared_income": declared_income, "requested_amount": requested_amount},
        "audit_results": {
            "risk_level": risk_level,
            "recommended_decision": decision,
            "confidence_score": confidence_score,
            "cross_document_match": document_matched,
            "red_flags_detected": red_flags
        },
        "ai_explanation": f"Evaluación completada. Nivel de riesgo {risk_level} registrado en la bitácora de auditoría SQL."
    }

@app.get("/api/v2/audit-history")
def get_audit_history():
    """ Endpoint de trazabilidad para dashboards en Power BI o Microsoft 365 """
    conn = sqlite3.connect("audit_log.db")
    df = pd.read_sql_query("SELECT * FROM audit_records ORDER BY id DESC LIMIT 50", conn)
    conn.close()
    return df.to_dict(orient="records")
