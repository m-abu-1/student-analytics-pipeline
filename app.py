import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import io
from datetime import datetime

# Page Configuration
st.set_page_config(
    page_title="BIT Academic Performance Analytics Pipeline",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Header Section
st.title("📊 Educational Data Quality & Academic Performance Analytics Pipeline")
st.caption("Automated Ingestion, Pydantic-Style Validation, Pearson Correlation, Z-Score Normalization, & Deterministic Risk Profiling")

st.markdown("---")

# Sidebar - Template & Configuration
with st.sidebar:
    st.header("⚙️ Pipeline Controls")
    
    # Download Template Utility
    st.subheader("1. Standard Data Contract")
    template_df = pd.DataFrame({
        "student_id": ["STU_001", "STU_002", "STU_003"],
        "student_name": ["John Doe", "Jane Smith", "Alex Mercer"],
        "subject_id": ["MATH101", "CS201", "PHY102"],
        "attendance_percentage": [85.0, 62.5, 91.0],
        "marks_obtained": [78.5, 42.0, 88.0],
        "maximum_marks": [100.0, 100.0, 100.0],
        "assessment_date": ["2026-09-15", "2026-09-15", "2026-09-15"]
    })
    
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        template_df.to_excel(writer, index=False, sheet_name='Template')
    
    st.download_button(
        label="📥 Download Excel Ingestion Template",
        data=buffer.getvalue(),
        file_name="student_ingestion_template.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    
    st.markdown("---")
    st.subheader("2. Threshold Rules")
    attendance_cutoff = st.slider("Min Attendance Threshold (%)", 50.0, 90.0, 75.0, step=1.0)
    
# Main Upload Area
uploaded_file = st.file_uploader("Upload Raw Student Academic Dataset (.csv or .xlsx)", type=["csv", "xlsx"])

if uploaded_file is not None:
    # ---------------------------------------------------------
    # STAGE 1: INGESTION & DATA SANITATION
    # ---------------------------------------------------------
    try:
        if uploaded_file.name.endswith('.csv'):
            raw_df = pd.read_csv(uploaded_file)
        else:
            raw_df = pd.read_excel(uploaded_file)
    except Exception as e:
        st.error(f"File Read Error: {e}")
        st.stop()
        
    st.success(f"Successfully ingested `{uploaded_file.name}` containing {len(raw_df)} total records.")
    
    # Header Normalization
    raw_df.columns = raw_df.columns.str.strip().str.lower()
    
    clean_records = []
    audit_logs = []
    
    required_cols = {'student_id', 'subject_id', 'attendance_percentage', 'marks_obtained', 'maximum_marks'}
    missing_cols = required_cols - set(raw_df.columns)
    
    if missing_cols:
        st.error(f"Data Contract Violation: Missing required columns: {missing_cols}")
        st.stop()

    # Rule-Based Cleaning & Validation Engine
    for idx, row in raw_df.iterrows():
        row_num = idx + 2  # Account for header
        s_id = str(row.get('student_id', '')).strip()
        sub_id = str(row.get('subject_id', '')).strip()
        s_name = str(row.get('student_name', s_id)).strip()
        
        try:
            att = float(row.get('attendance_percentage', -1))
            marks = float(row.get('marks_obtained', -1))
            max_m = float(row.get('maximum_marks', 100.0))
            
            # Validation Rules
            rejections = []
            if not s_id or s_id == 'nan':
                rejections.append("Missing Student ID")
            if not sub_id or sub_id == 'nan':
                rejections.append("Missing Subject ID")
            if att < 0.0 or att > 100.0:
                rejections.append(f"Attendance out of range [0-100%]: {att}%")
            if marks < 0.0:
                rejections.append(f"Negative marks detected: {marks}")
            if marks > max_m:
                rejections.append(f"Marks ({marks}) exceed maximum limit ({max_m})")
                
            if rejections:
                audit_logs.append({
                    "Row Number": row_num,
                    "Student ID": s_id,
                    "Subject ID": sub_id,
                    "Rejection Reason": " | ".join(rejections),
                    "Raw Data": str(row.to_dict())
                })
            else:
                pct_mark = (marks / max_m) * 100.0
                clean_records.append({
                    "student_id": s_id,
                    "student_name": s_name,
                    "subject_id": sub_id,
                    "attendance_percentage": att,
                    "marks_obtained": marks,
                    "maximum_marks": max_m,
                    "normalized_mark_pct": pct_mark
                })
        except Exception as err:
            audit_logs.append({
                "Row Number": row_num,
                "Student ID": s_id,
                "Subject ID": sub_id,
                "Rejection Reason": f"Type Casting Error: {str(err)}",
                "Raw Data": str(row.to_dict())
            })
            
    clean_df = pd.DataFrame(clean_records)
    audit_df = pd.DataFrame(audit_logs)
    
    # Deduplication Step on Clean Records
    if not clean_df.empty:
        initial_clean_len = len(clean_df)
        clean_df = clean_df.drop_duplicates(subset=['student_id', 'subject_id'], keep='first')
        dedup_dropped = initial_clean_len - len(clean_df)
        if dedup_dropped > 0:
            st.warning(f"Detected and removed {dedup_dropped} duplicate records for identical (Student, Subject) pairs.")

    # Data Health Score
    total_received = len(raw_df)
    clean_count = len(clean_df)
    flagged_count = len(audit_df)
    health_score = round((clean_count / total_received) * 100, 2) if total_received > 0 else 0.0

    # ---------------------------------------------------------
    # STAGE 2: DATA HEALTH & AUDIT DISPLAY
    # ---------------------------------------------------------
    st.subheader("📋 Pipeline Sanitation & Health Audit")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Records Ingested", total_received)
    col2.metric("Clean Records Persisted", clean_count)
    col3.metric("Flagged / Rejected", flagged_count)
    col4.metric("Data Health Score", f"{health_score}%")
    
    if not audit_df.empty:
        with st.expander("⚠️ View Audit Log (Rejected Anomalous Records)", expanded=True):
            st.dataframe(audit_df[['Row Number', 'Student ID', 'Subject ID', 'Rejection Reason']], use_container_width=True)
            
            audit_csv = audit_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Export Audit Log (.CSV)",
                data=audit_csv,
                file_name=f"audit_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )

    if clean_df.empty:
        st.error("No valid clean records available for analytics. Please upload a corrected dataset.")
        st.stop()

    # ---------------------------------------------------------
    # STAGE 3: STATISTICAL ANALYTICS & Z-SCORE NORMALIZATION
    # ---------------------------------------------------------
    st.markdown("---")
    st.subheader("📐 Statistical Analytics & Difficulty Normalization")
    
    # Calculate Subject Level Metrics
    subject_stats = clean_df.groupby('subject_id').agg(
        subject_mean=('normalized_mark_pct', 'mean'),
        subject_std=('normalized_mark_pct', 'std'),
        avg_attendance=('attendance_percentage', 'mean'),
        student_count=('student_id', 'nunique')
    ).reset_index()
    
    subject_stats['subject_std'] = subject_stats['subject_std'].fillna(0.0)
    
    # Merge Subject Means back to calculate Z-Score
    clean_df = clean_df.merge(subject_stats[['subject_id', 'subject_mean', 'subject_std']], on='subject_id', how='left')
    
    # Z-Score Calculation: Z = (Mark % - Subject Mean) / Subject Std Dev
    clean_df['z_score'] = np.where(
        clean_df['subject_std'] > 0,
        (clean_df['normalized_mark_pct'] - clean_df['subject_mean']) / clean_df['subject_std'],
        0.0
    )

    # Calculate Pearson Correlation (Attendance vs Marks)
    overall_corr = clean_df['attendance_percentage'].corr(clean_df['normalized_mark_pct'], method='pearson')
    
    st.info(f"**Pearson Correlation Coefficient ($r$):** `{overall_corr:+.4f}` — " + 
            ("Strong Positive Relationship" if overall_corr > 0.6 else "Moderate Relationship" if overall_corr > 0.3 else "Weak / No Linear Relationship"))

    tab1, tab2 = st.tabs(["📈 Attendance vs Performance Regression", "📊 Subject Difficulty (Z-Scores)"])
    
    with tab1:
        fig_scatter = px.scatter(
            clean_df,
            x="attendance_percentage",
            y="normalized_mark_pct",
            color="subject_id",
            hover_data=["student_id", "student_name", "z_score"],
            trendline="ols",
            title="Pearson Bivariate Correlation & Trend Discovery",
            labels={"attendance_percentage": "Attendance Percentage (%)", "normalized_mark_pct": "Normalized Mark (%)"}
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
        
    with tab2:
        fig_box = px.box(
            clean_df,
            x="subject_id",
            y="normalized_mark_pct",
            points="all",
            title="Subject Mark Distribution & Difficulty Variation",
            labels={"subject_id": "Subject Code", "normalized_mark_pct": "Mark Percentage (%)"}
        )
        st.plotly_chart(fig_box, use_container_width=True)

    # ---------------------------------------------------------
    # STAGE 4: ACTION MATRIX & RISK CLASSIFICATION
    # ---------------------------------------------------------
    st.markdown("---")
    st.subheader("🎯 Deterministic At-Risk Action Matrix")
    
    # Student Aggregations
    student_summary = clean_df.groupby(['student_id', 'student_name']).agg(
        mean_attendance=('attendance_percentage', 'mean'),
        overall_mean_pct=('normalized_mark_pct', 'mean'),
        avg_z_score=('z_score', 'mean')
    ).reset_index()
    
    # Overall Batch Average
    batch_avg_mark = student_summary['overall_mean_pct'].mean()
    
    def classify_risk(row):
        att_low = row['mean_attendance'] < attendance_cutoff
        marks_low = row['overall_mean_pct'] < batch_avg_mark
        
        if att_low and marks_low:
            return "CRITICAL"
        elif att_low:
            return "ATTENDANCE RISK"
        elif marks_low:
            return "ACADEMIC RISK"
        return "ON TRACK"

    student_summary['Risk Category'] = student_summary.apply(classify_risk, axis=1)
    
    def recommend_action(risk):
        if risk == "CRITICAL":
            return "Schedule Mandatory Faculty Counseling & Send Parent Alert"
        elif risk == "ATTENDANCE RISK":
            return "Issue Official Low Attendance Warning Letter"
        elif risk == "ACADEMIC RISK":
            return "Assign Peer Tutor & Remedial Session"
        return "Regular Monitoring"

    student_summary['Recommended Action'] = student_summary['Risk Category'].apply(recommend_action)
    
    # Filter Tabs
    risk_filter = st.radio("Filter Student List by Risk Level:", ["ALL", "CRITICAL", "ATTENDANCE RISK", "ACADEMIC RISK", "ON TRACK"], horizontal=True)
    
    if risk_filter != "ALL":
        display_students = student_summary[student_summary['Risk Category'] == risk_filter]
    else:
        display_students = student_summary
        
    st.dataframe(
        display_students.style.format({
            "mean_attendance": "{:.1f}%",
            "overall_mean_pct": "{:.2f}%",
            "avg_z_score": "{:+.2f}"
        }),
        use_container_width=True
    )
    
    # Export Actions
    action_csv = student_summary.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Export At-Risk Action Matrix (.CSV)",
        data=action_csv,
        file_name=f"at_risk_action_matrix_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )

else:
    st.info("👆 Please upload a `.csv` or `.xlsx` file using the box above to trigger the pipeline.")
