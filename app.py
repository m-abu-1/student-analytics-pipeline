import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import io

# ---------------------------------------------------------
# 1. ENTERPRISE CONFIGURATION & UI SETUP
# ---------------------------------------------------------
st.set_page_config(
    page_title="Academic Analytics Pipeline",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .kpi-card { background-color: #f8f9fa; padding: 20px; border-radius: 8px; border-left: 5px solid #004085; margin-bottom: 20px; }
    .kpi-title { font-size: 14px; color: #6c757d; font-weight: bold; text-transform: uppercase; }
    .kpi-value { font-size: 28px; font-weight: bold; color: #212529; }
    .risk-critical { border-left-color: #dc3545; }
    .risk-warning { border-left-color: #ffc107; }
</style>
""", unsafe_allow_html=True)

st.title("Academic Performance & Attendance Analytics")
st.markdown("### End-to-End Pipeline: Ingestion → Validation → Statistical Analysis → Risk Flagging")

# ---------------------------------------------------------
# 2. DEFINING THE PIPELINE PARAMETERS
# ---------------------------------------------------------
with st.sidebar:
    st.header("Institutional Thresholds")
    ATTENDANCE_CUTOFF = st.slider("Attendance Minimum (%)", 50, 90, 75, help="Threshold for Attendance Risk")
    st.markdown("---")
    st.markdown("**Risk Definitions:**")
    st.markdown("- **Attendance Risk:** $< 75\%$")
    st.markdown("- **Academic Risk:** Marks $<$ Subject Average")
    st.markdown("- **Critical Risk:** Meets both conditions above.")

# ---------------------------------------------------------
# 3. DATA INGESTION & VALIDATION MODULE (STAGE 1 & 2)
# ---------------------------------------------------------
@st.cache_data
def ingest_and_validate_data(file):
    if file.name.endswith('.csv'):
        df = pd.read_csv(file)
    else:
        df = pd.read_excel(file)
        
    # Schema check based on project requirements
    required_cols = ['student_id', 'name', 'subject_id', 'attendance_percentage', 'marks_obtained', 'maximum_marks']
    if not all(col in df.columns for col in required_cols):
        return None, None, f"Missing required columns. Expected: {required_cols}"
    
    # Validation Rules
    initial_count = len(df)
    
    # 1. Drop complete duplicates
    df = df.drop_duplicates()
    
    # 2. Flag missing values
    audit_missing = df[df.isnull().any(axis=1)].copy()
    audit_missing['anomaly_type'] = "Missing Values"
    df = df.dropna()
    
    # 3. Validate boundaries (0-100% attendance, marks <= maximum)
    audit_bounds = df[
        (df['attendance_percentage'] < 0) | 
        (df['attendance_percentage'] > 100) | 
        (df['marks_obtained'] < 0) | 
        (df['marks_obtained'] > df['maximum_marks'])
    ].copy()
    audit_bounds['anomaly_type'] = "Boundary Violation"
    
    # Keep only valid records for analysis
    df_clean = df[
        (df['attendance_percentage'] >= 0) & 
        (df['attendance_percentage'] <= 100) & 
        (df['marks_obtained'] >= 0) & 
        (df['marks_obtained'] <= df['maximum_marks'])
    ].copy()
    
    audit_log = pd.concat([audit_missing, audit_bounds], ignore_index=True)
    
    return df_clean, audit_log, None

# ---------------------------------------------------------
# 4. STATISTICAL ANALYSIS & NORMALIZATION MODULE (STAGE 3 & 4)
# ---------------------------------------------------------
@st.cache_data
def execute_statistical_pipeline(df):
    # Calculate Base Percentage
    df['mark_percentage'] = (df['marks_obtained'] / df['maximum_marks']) * 100
    
    # Subject-Wise Descriptive Statistics & Baselines
    subject_stats = df.groupby('subject_id')['mark_percentage'].agg(['mean', 'median', 'std']).reset_index()
    subject_stats = subject_stats.rename(columns={'mean': 'subject_mean', 'median': 'subject_median', 'std': 'subject_std'})
    
    # Handle zero standard deviation to prevent division by zero in Z-score
    subject_stats['subject_std'] = subject_stats['subject_std'].replace(0, 1)
    
    # Merge baselines back to main dataset
    df = df.merge(subject_stats, on='subject_id')
    
    # Calculate Subject Normalization (Z-Score)
    df['z_score'] = (df['mark_percentage'] - df['subject_mean']) / df['subject_std']
    
    return df, subject_stats

# ---------------------------------------------------------
# 5. RISK IDENTIFICATION ENGINE (STAGE 5)
# ---------------------------------------------------------
@st.cache_data
def identify_risks(df, att_cutoff):
    # Rule 1: Attendance Risk
    df['attendance_risk'] = df['attendance_percentage'] < att_cutoff
    
    # Rule 2: Academic Risk (Below subject mean)
    df['academic_risk'] = df['mark_percentage'] < df['subject_mean']
    
    # Rule 3: Critical At-Risk (Both conditions met)
    df['critical_risk'] = df['attendance_risk'] & df['academic_risk']
    
    # Categorize for UI
    def get_risk_label(row):
        if row['critical_risk']: return "Critical Risk"
        if row['attendance_risk']: return "Attendance Risk"
        if row['academic_risk']: return "Academic Risk"
        return "On Track"
        
    df['risk_category'] = df.apply(get_risk_label, axis=1)
    return df

# ---------------------------------------------------------
# UI ROUTING & EXECUTION
# ---------------------------------------------------------
uploaded_file = st.file_uploader("Ingest Raw Academic Data (CSV/Excel)", type=["csv", "xlsx", "xls"])

if uploaded_file is not None:
    # Execute Pipeline
    df_clean, df_audit, error = ingest_and_validate_data(uploaded_file)
    
    if error:
        st.error(error)
        st.stop()
        
    df_analyzed, subject_stats = execute_statistical_pipeline(df_clean)
    df_final = identify_risks(df_analyzed, ATTENDANCE_CUTOFF)
    
    # Top Level KPIs
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(f'<div class="kpi-card"><div class="kpi-title">Valid Records</div><div class="kpi-value">{len(df_final)}</div></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="kpi-card risk-warning"><div class="kpi-title">Anomalies Rejected</div><div class="kpi-value">{len(df_audit)}</div></div>', unsafe_allow_html=True)
    
    critical_count = df_final['critical_risk'].sum()
    c3.markdown(f'<div class="kpi-card risk-critical"><div class="kpi-title">Critical At-Risk</div><div class="kpi-value">{critical_count}</div></div>', unsafe_allow_html=True)
    
    overall_corr = df_final['attendance_percentage'].corr(df_final['mark_percentage'])
    c4.markdown(f'<div class="kpi-card"><div class="kpi-title">Global Pearson (r)</div><div class="kpi-value">{overall_corr:.2f}</div></div>', unsafe_allow_html=True)
    
    # Tabbed Interface
    tab1, tab2, tab3, tab4 = st.tabs(["Data Audit & Cleaning", "Statistical Trends & Regression", "Subject Normalization (Z-Score)", "Automated Risk Dashboard"])
    
    with tab1:
        st.subheader("Data Validation Log")
        if not df_audit.empty:
            st.warning(f"Identified {len(df_audit)} records violating schema boundaries or containing missing values. These were excluded from statistical calculations.")
            st.dataframe(df_audit, use_container_width=True)
        else:
            st.success("No anomalies detected during ingestion.")
            
    with tab2:
        st.subheader("Attendance vs Performance Regression Analysis")
        col1, col2 = st.columns([3, 1])
        with col1:
            # NumPy Polyfit Regression implementation
            x = df_final['attendance_percentage']
            y = df_final['mark_percentage']
            
            fig = px.scatter(df_final, x="attendance_percentage", y="mark_percentage", color="subject_id", 
                             hover_data=['student_id', 'name'], opacity=0.7,
                             title="Linear Association Analysis")
                             
            if len(x) > 1:
                # Calculate simple linear regression using NumPy
                slope, intercept = np.polyfit(x, y, 1)
                line_x = np.array([x.min(), x.max()])
                line_y = slope * line_x + intercept
                fig.add_trace(go.Scatter(x=line_x, y=line_y, mode='lines', name='Regression Line', line=dict(color='black', dash='dash')))
                
            fig.update_layout(xaxis_title="Attendance (%)", yaxis_title="Marks (%)")
            st.plotly_chart(fig, use_container_width=True)
            
        with col2:
            st.markdown("### Statistical Insight")
            st.markdown(f"**Pearson Correlation ($r$):** `{overall_corr:.3f}`")
            st.markdown("""
            A strong positive correlation indicates a statistical relationship where higher attendance is associated with higher academic performance. 
            *Note: This regression studies association only and is not implemented to claim absolute prediction of student success.*
            """)
            
    with tab3:
        st.subheader("Subject-Wise Comparison & Standardization")
        st.markdown("Raw marks are normalized using the formula: $Z = \\frac{\\text{Mark \\%} - \\text{Subject Mean}}{\\text{Subject Std. Dev.}}$")
        
        st.dataframe(subject_stats.style.format({'subject_mean': '{:.1f}%', 'subject_median': '{:.1f}%', 'subject_std': '{:.2f}'}), use_container_width=True)
        
        fig_box = px.box(df_final, x="subject_id", y="z_score", color="subject_id", title="Z-Score Distribution across Subjects")
        fig_box.add_hline(y=0, line_dash="dot", annotation_text="Subject Mean")
        st.plotly_chart(fig_box, use_container_width=True)
        
    with tab4:
        st.subheader("Automated Cohort Flagging")
        
        risk_summary = df_final['risk_category'].value_counts().reset_index()
        risk_summary.columns = ['Risk Category', 'Student Count']
        
        col_a, col_b = st.columns([1, 2])
        with col_a:
            fig_pie = px.pie(risk_summary, names='Risk Category', values='Student Count', 
                             color='Risk Category',
                             color_discrete_map={"Critical Risk": "#dc3545", "Attendance Risk": "#fd7e14", "Academic Risk": "#ffc107", "On Track": "#28a745"},
                             hole=0.4)
            st.plotly_chart(fig_pie, use_container_width=True)
            
        with col_b:
            st.markdown("### Actionable Roster (At-Risk Students)")
            at_risk_df = df_final[df_final['risk_category'] != "On Track"]
            st.dataframe(at_risk_df[['student_id', 'name', 'subject_id', 'attendance_percentage', 'mark_percentage', 'risk_category']].sort_values('risk_category'), use_container_width=True)
else:
    st.info("Awaiting Data Ingestion. Please upload a CSV or Excel file containing attendance and performance records to initialize the pipeline.")
