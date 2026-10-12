import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from scipy import stats
import io
from datetime import datetime

# ---------------------------------------------------------
# 1. PAGE CONFIGURATION & GOOGLE/ZOHO SAAS DESIGN SYSTEM
# ---------------------------------------------------------
st.set_page_config(
    page_title="Academic Decision Intelligence Platform",
    page_icon="https://img.icons8.com/color/96/000000/google-code.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Session State for Data Persistence
if "raw_df" not in st.session_state:
    st.session_state["raw_df"] = None

# Global Empty State Placeholder HTML
EMPTY_BANNER_HTML = """
<div class="empty-banner">
    <div class="empty-banner-title">Awaiting Institutional Data Ingestion Stream</div>
    <div class="empty-banner-sub">Please upload an academic batch dataset (.csv or .xlsx) or click <strong>'Load Demo Data'</strong> above to compute statistical models, outcome attainment matrices, and financial retention forecasts.</div>
</div>
"""

# Custom High-Density CSS Architecture
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] { 
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; 
        background-color: #F8F9FA !important;
        -webkit-font-smoothing: antialiased;
    }
    
    .block-container {
        padding-top: 3.8rem !important;
        padding-bottom: 2.0rem !important;
        padding-left: 1.8rem !important;
        padding-right: 1.8rem !important;
        max-width: 100% !important;
    }
    
    [data-testid="stVerticalBlock"] { gap: 0.85rem !important; }

    header[data-testid="stHeader"] {
        background-color: rgba(248, 249, 250, 0.85) !important;
        backdrop-filter: blur(8px);
        z-index: 99 !important;
    }

    .workspace-navbar {
        width: 100%;
        box-sizing: border-box;
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: #0F172A;
        color: #FFFFFF;
        padding: 18px 24px;
        border-radius: 8px;
        margin-bottom: 16px;
        border-left: 6px solid #1A73E8;
        box-shadow: 0 2px 6px rgba(0,0,0,0.06);
    }
    .workspace-navbar .brand-title { font-size: 19px; font-weight: 800; color: #F8FAFC; letter-spacing: -0.02em; }
    .workspace-navbar .brand-sub { font-size: 13px; color: #94A3B8; font-weight: 400; margin-left: 8px; }
    .workspace-navbar .status-tag {
        background: rgba(26, 115, 232, 0.2); border: 1px solid rgba(56, 189, 248, 0.4); color: #38BDF8;
        padding: 5px 14px; border-radius: 9999px; font-size: 11px; font-weight: 700; text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 8px !important;
        border-bottom: 2px solid #DADCE0 !important;
        background-color: #FFFFFF;
        padding: 6px 16px 0px 16px !important;
        border-radius: 8px 8px 0 0;
        box-shadow: 0 1px 3px rgba(60,64,67,0.05);
        width: 100% !important;
        display: flex !important;
        flex-wrap: wrap !important;
    }
    .stTabs [data-baseweb="tab"] {
        height: 42px !important;
        padding: 0px 20px !important;
        font-size: 13.5px !important;
        font-weight: 600 !important;
        color: #5F6368 !important;
        border-radius: 4px 4px 0 0 !important;
        background-color: transparent !important;
        border: none !important;
        white-space: nowrap !important;
        transition: all 0.2s ease-in-out;
    }
    .stTabs [aria-selected="true"] {
        color: #1A73E8 !important;
        background-color: #E8F0FE !important;
        border-bottom: 3px solid #1A73E8 !important;
        font-weight: 700 !important;
    }

    .status-badge { display: inline-block; padding: 3px 10px; border-radius: 4px; font-size: 11px; font-weight: 700; text-transform: uppercase; }
    .badge-critical { background: #FCE8E6; color: #C5221F; border: 1px solid #F5C2C7; }
    .badge-warning { background: #FEF7E0; color: #B06000; border: 1px solid #FBE3B5; }
    .badge-academic { background: #E8F0FE; color: #1A73E8; border: 1px solid #C2E7FF; }
    .badge-success { background: #E6F4EA; color: #137333; border: 1px solid #C6EDD5; }

    .insight-banner {
        background-color: #FFFFFF; border: 1px solid #DADCE0; border-left: 5px solid #1A73E8;
        padding: 16px 20px; border-radius: 6px; font-size: 13.5px; color: #3C4043; line-height: 1.6;
        margin-top: 12px; margin-bottom: 12px; box-shadow: 0 1px 3px rgba(60,64,67,0.04);
    }

    .empty-banner {
        background: #FFFFFF; border: 2px dashed #DADCE0; border-radius: 8px;
        padding: 44px; text-align: center; color: #5F6368; margin: 20px 0;
    }
    .empty-banner-title { font-size: 16px; font-weight: 700; color: #202124; margin-bottom: 6px; }
    .empty-banner-sub { font-size: 13px; color: #70757A; }

    .main-section-lbl { font-size: 13px; font-weight: 800; color: #1E293B; text-transform: uppercase; letter-spacing: 0.05em; margin: 14px 0 8px 0; }
</style>
""", unsafe_allow_html=True)

# Top Header Banner
st.markdown("""
<div class="workspace-navbar">
    <div>
        <span class="brand-title">ACADEMIC DECISION INTELLIGENCE PLATFORM</span>
        <span class="brand-sub"> &nbsp;|&nbsp; Bannari Amman Institute of Technology — Outcome Governance & Retention Analytics</span>
    </div>
    <div class="status-tag">PIPELINE SECURE</div>
</div>
""", unsafe_allow_html=True)

PLOTLY_CONFIG = dict(
    font=dict(family="Inter, sans-serif", color="#3C4043", size=12),
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#FFFFFF",
    margin=dict(l=40, r=25, t=40, b=40),
    xaxis=dict(showgrid=True, gridcolor="#F1F3F4", linecolor="#DADCE0"),
    yaxis=dict(showgrid=True, gridcolor="#F1F3F4", linecolor="#DADCE0")
)

# ---------------------------------------------------------
# 2. SCHEMA NORMALIZATION & DEMO GENERATOR
# ---------------------------------------------------------
ALIAS_MAP = {
    'student_id': ['student_id', 'roll_no', 'register_no', 'usn', 'id', 'student_code'],
    'student_name': ['student_name', 'name', 'full_name', 'candidate_name'],
    'department': ['department', 'dept', 'branch', 'stream'],
    'subject_id': ['subject_id', 'subject_code', 'course_id', 'subject'],
    'attendance_percentage': ['attendance_percentage', 'attendance', 'attendance_pct', 'att_%', 'att'],
    'marks_obtained': ['marks_obtained', 'marks', 'score', 'obtained_marks', 'total_marks', 'internal_marks'],
    'maximum_marks': ['maximum_marks', 'max_marks', 'total_possible', 'max'],
    'academic_semester': ['academic_semester', 'semester', 'sem', 'semester_id']
}

def normalize_columns(df):
    renamed = {}
    cols_lower = {str(col).strip().lower(): col for col in df.columns}
    for target, aliases in ALIAS_MAP.items():
        for alias in aliases:
            if alias in cols_lower:
                renamed[cols_lower[alias]] = target
                break
    return df.rename(columns=renamed)

def generate_demo_dataset():
    np.random.seed(42)
    students = [f"BIT26CS{i:03d}" for i in range(1, 201)]
    names = [f"Student_{i}" for i in range(1, 201)]
    subjects = ["MA3151_Maths", "CS3351_DPCO", "CS3352_DataStructures", "CS3391_OOP", "GE3351_Environmental", "EC3351_Signals"]
    
    rows = []
    for s_id, name in zip(students, names):
        base_att = np.random.uniform(55, 98)
        base_mark = base_att * 0.7 + np.random.normal(15, 12)
        
        for sub in subjects:
            att = np.clip(base_att + np.random.normal(0, 4), 40, 100)
            marks = np.clip(base_mark + np.random.normal(0, 10), 20, 100)
            rows.append({
                "student_id": s_id, "student_name": name, "department": "CSE",
                "subject_id": sub, "attendance_percentage": round(att, 1),
                "marks_obtained": round(marks, 1), "maximum_marks": 100, "academic_semester": "SEM_05"
            })
    return pd.DataFrame(rows)

# ---------------------------------------------------------
# 3. SIDEBAR INSTITUTIONAL POLICY CONTROLS
# ---------------------------------------------------------
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/google-code.png", width=48)
    st.markdown("### Governance Policy Cutoffs")
    
    att_threshold = st.slider(
        "Attendance Cutoff (%)", 50.0, 90.0, 75.0, 1.0,
        key="sidebar_att_threshold",
        help="Mandatory university attendance threshold. Falling below triggers an Attendance Warning or Critical At-Risk flag."
    )
    z_risk_threshold = st.slider(
        "Critical Z-Score Cutoff (σ)", -2.0, 0.0, -0.5, 0.1,
        key="sidebar_z_threshold",
        help="Standard deviation cutoff relative to subject average. Scores below signal relative academic underperformance."
    )
    est_tuition_fee = st.number_input(
        "Annual Tuition Fee (₹)", value=125000, step=5000,
        key="sidebar_tuition_fee",
        help="Annual departmental tuition fee per student used to calculate total financial tuition revenue exposure."
    )
    
    if st.session_state["raw_df"] is not None:
        st.markdown("---")
        if st.button("Clear Uploaded Dataset", key="btn_clear_data", use_container_width=True):
            st.session_state["raw_df"] = None
            st.rerun()

# ---------------------------------------------------------
# 4. STATISTICAL & CALCULATIVE PIPELINE (REAL-TIME REACTIVE)
# ---------------------------------------------------------
def run_analytics_pipeline(df_raw, att_thresh, z_thresh):
    df = normalize_columns(df_raw)
    
    required_keys = {'student_id', 'subject_id', 'attendance_percentage', 'marks_obtained'}
    missing = required_keys - set(df.columns)
    if missing:
        return None, None, None, None, list(missing)

    if 'maximum_marks' not in df.columns: df['maximum_marks'] = 100.0
    if 'student_name' not in df.columns: df['student_name'] = df['student_id']
    if 'department' not in df.columns: df['department'] = "CSE/ECE"
    if 'academic_semester' not in df.columns: df['academic_semester'] = "SEM_05"

    clean_rows, audit_entries = [], []
    
    for idx, row in df.iterrows():
        r_num = idx + 2
        s_id = str(row.get('student_id', '')).strip()
        sub_id = str(row.get('subject_id', '')).strip()
        s_name = str(row.get('student_name', s_id)).strip()
        dept = str(row.get('department', 'CSE/ECE')).strip()
        sem = str(row.get('academic_semester', 'SEM_05')).strip()
        
        reasons = []
        if not s_id or s_id == 'nan': reasons.append("Missing Student ID")
        if not sub_id or sub_id == 'nan': reasons.append("Missing Subject ID")
            
        try:
            att = float(row.get('attendance_percentage', -1))
            marks = float(row.get('marks_obtained', -1))
            max_m = float(row.get('maximum_marks', 100.0))
            
            if pd.isna(att) or att < 0.0 or att > 100.0: reasons.append(f"Invalid Attendance [{att}%]")
            if pd.isna(marks) or marks < 0.0 or marks > max_m: reasons.append(f"Invalid Marks [{marks}/{max_m}]")
                
            if not reasons:
                pct_score = (marks / max_m) * 100.0
                clean_rows.append({
                    "student_id": s_id, "student_name": s_name, "department": dept,
                    "subject_id": sub_id, "academic_semester": sem,
                    "attendance_percentage": att, "marks_obtained": marks,
                    "maximum_marks": max_m, "normalized_mark_pct": pct_score
                })
        except (ValueError, TypeError):
            reasons.append("Non-numeric Data Type Failure")
            
        if reasons:
            audit_entries.append({
                "Row Number": r_num, "Student ID": s_id, "Subject ID": sub_id,
                "Rejection Reason": " | ".join(reasons), "Payload": str(row.to_dict())
            })

    clean_df = pd.DataFrame(clean_rows)
    audit_df = pd.DataFrame(audit_entries)
    
    if clean_df.empty:
        return clean_df, audit_df, None, None, None

    clean_df = clean_df.drop_duplicates(subset=['student_id', 'subject_id', 'academic_semester'], keep='first')

    # Subject Analytics & OBE Attainment Computation
    subject_summary = clean_df.groupby('subject_id').agg(
        subject_mean=('normalized_mark_pct', 'mean'),
        subject_median=('normalized_mark_pct', 'median'),
        subject_std=('normalized_mark_pct', 'std'),
        avg_attendance=('attendance_percentage', 'mean'),
        student_count=('student_id', 'nunique'),
        pass_count=('normalized_mark_pct', lambda x: (x >= 50.0).sum())
    ).reset_index()
    
    subject_summary['subject_std'] = subject_summary['subject_std'].fillna(1.0).replace(0, 1.0)
    subject_summary['Subject Difficulty Index (SDI)'] = (100.0 - subject_summary['subject_mean']).round(2)
    subject_summary['Pass Rate (%)'] = ((subject_summary['pass_count'] / subject_summary['student_count']) * 100.0).round(1)
    
    def get_obe_level(pass_rate):
        if pass_rate >= 70.0: return "Level 3 (High)"
        elif pass_rate >= 60.0: return "Level 2 (Moderate)"
        elif pass_rate >= 50.0: return "Level 1 (Low)"
        return "Level 0 (Unattained)"

    subject_summary['OBE Target Attainment'] = subject_summary['Pass Rate (%)'].apply(get_obe_level)
    
    # Standardize Scores using Z-Score Baseline
    clean_df = clean_df.merge(subject_summary[['subject_id', 'subject_mean', 'subject_std']], on='subject_id', how='left')
    clean_df['z_score'] = (clean_df['normalized_mark_pct'] - clean_df['subject_mean']) / clean_df['subject_std']
    clean_df['z_score'] = clean_df['z_score'].fillna(0.0)

    # Indian 10-Point Grade Point (SGPA Scale)
    def mark_to_gpa(pct):
        if pct >= 90: return 10.0
        elif pct >= 80: return 9.0
        elif pct >= 70: return 8.0
        elif pct >= 60: return 7.0
        elif pct >= 50: return 6.0
        return 0.0

    clean_df['grade_point'] = clean_df['normalized_mark_pct'].apply(mark_to_gpa)

    # Student Aggregation Matrix
    student_matrix = clean_df.groupby(['student_id', 'student_name', 'department']).agg(
        mean_attendance=('attendance_percentage', 'mean'),
        overall_mean_pct=('normalized_mark_pct', 'mean'),
        est_sgpa=('grade_point', 'mean'),
        avg_z_score=('z_score', 'mean'),
        subjects_count=('subject_id', 'nunique')
    ).reset_index()

    # Composite Academic Health Index (AHI = 60% Marks + 40% Attendance)
    student_matrix['Academic Health Index (AHI)'] = (
        (student_matrix['overall_mean_pct'] * 0.60) + (student_matrix['mean_attendance'] * 0.40)
    ).round(2)

    # Risk Quadrant Classification (Dynamically Driven by Sidebar Sliders)
    def classify_quadrant(row):
        att_low = row['mean_attendance'] < att_thresh
        z_low = row['avg_z_score'] < z_thresh
        if att_low and z_low: return "CRITICAL RISK (Q1)"
        elif att_low and not z_low: return "ATTENDANCE RISK (Q2)"
        elif not att_low and z_low: return "ACADEMIC RISK (Q3)"
        return "HIGH PERFORMER (Q4)"

    student_matrix['Risk Quadrant'] = student_matrix.apply(classify_quadrant, axis=1)

    return clean_df, audit_df, subject_summary, student_matrix, None

# ---------------------------------------------------------
# 5. INGESTION CONSOLE & SESSION PERSISTENCE
# ---------------------------------------------------------
st.markdown("<div class='main-section-lbl'>1. Data Ingestion & Sanitation Audit Console</div>", unsafe_allow_html=True)

col_ingest, col_template = st.columns([3, 1], vertical_alignment="bottom")
with col_ingest:
    uploaded_file = st.file_uploader(
        "Ingest Academic Data File (.csv or .xlsx)", type=["csv", "xlsx"],
        key="main_data_file_uploader",
        help="Upload raw academic dataset containing student marks, attendance, and subject details."
    )
    if uploaded_file is not None:
        st.session_state["raw_df"] = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)

with col_template:
    st.markdown("**Actions & Schema Contract**")
    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
        if st.button("Load Demo Data", key="btn_load_demo", use_container_width=True):
            st.session_state["raw_df"] = generate_demo_dataset()
            st.rerun()
            
    with btn_col2:
        template_data = pd.DataFrame({
            "student_id": ["BIT26CS001"], "student_name": ["Aarav Sharma"], "department": ["CSE"],
            "subject_id": ["MA3151_Maths"], "attendance_percentage": [88.5],
            "marks_obtained": [82.0], "maximum_marks": [100.0], "academic_semester": ["SEM_05"]
        })
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine='openpyxl') as writer:
            template_data.to_excel(writer, index=False, sheet_name='Data_Contract')
        st.download_button("Schema Contract (.xlsx)", data=buf.getvalue(), file_name="academic_schema_contract.xlsx", key="dl_contract_schema", use_container_width=True)

clean_df, audit_df, subject_summary, student_matrix = None, None, None, None

if st.session_state["raw_df"] is not None:
    raw_df = st.session_state["raw_df"]
    clean_df, audit_df, subject_summary, student_matrix, missing = run_analytics_pipeline(raw_df, att_threshold, z_risk_threshold)
    
    if missing:
        st.error(f"Data Contract Violation: Could not resolve required fields {missing}. Download and use the standard schema template above.")
        st.stop()
        
    total_received = len(raw_df)
    clean_count = len(clean_df) if clean_df is not None else 0
    flagged_count = len(audit_df) if audit_df is not None else 0
    health_score = round((clean_count / total_received) * 100, 2) if total_received > 0 else 0.0

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Records Ingested", total_received, help="Total raw row count received.")
    k2.metric("Clean Records Persisted", clean_count, help="Validated non-duplicate records in active processing pipeline.")
    k3.metric("Anomalies Isolated", flagged_count, delta=f"{flagged_count} Rejections", delta_color="inverse", help="Records rejected due to missing fields or out-of-bounds values.")
    k4.metric("Data Health Score", f"{health_score}%", delta="NAAC Ready" if health_score >= 90 else "Action Required", delta_color="normal" if health_score >= 90 else "inverse", help="Percentage of clean records. NAAC/NBA target >= 90%.")
    
    if audit_df is not None and not audit_df.empty:
        with st.expander("View Isolated Anomaly Audit Trail Log", expanded=False):
            st.dataframe(audit_df, use_container_width=True)

# ---------------------------------------------------------
# 6. GOOGLE/ZOHO WORKSPACE NAVIGATION TABS
# ---------------------------------------------------------
st.markdown("<div class='main-section-lbl'>2. Academic Decision Intelligence Hub</div>", unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Executive Control & Sensitivity",
    "Course Outcomes & OBE Attainment",
    "Student 360 Directory & Scorecards",
    "2D Early Warning Risk Matrix",
    "Embedded AI Academic Assistant"
])

# ---------------------------------------------------------
# TAB 1: EXECUTIVE CONTROL & SENSITIVITY
# ---------------------------------------------------------
with tab1:
    if clean_df is not None and not clean_df.empty:
        batch_avg_mark = clean_df['normalized_mark_pct'].mean()
        batch_avg_att = clean_df['attendance_percentage'].mean()
        batch_ahi = student_matrix['Academic Health Index (AHI)'].mean()
        pass_rate = ((student_matrix['overall_mean_pct'] >= 50.0).sum() / len(student_matrix)) * 100.0
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Cohort Mean Score Attainment", f"{batch_avg_mark:.2f}%")
        m2.metric("Aggregate Attendance Baseline", f"{batch_avg_att:.1f}%")
        m3.metric("Academic Health Index (AHI)", f"{batch_ahi:.1f} / 100")
        m4.metric("Outcome Attainment Benchmark (≥ 50%)", f"{pass_rate:.1f}%")

        col_viz, col_stats = st.columns([2.2, 1])
        
        x_raw = clean_df['attendance_percentage'].to_numpy(dtype=float)
        y_raw = clean_df['normalized_mark_pct'].to_numpy(dtype=float)
        mask = np.isfinite(x_raw) & np.isfinite(y_raw)
        x_clean, y_clean = x_raw[mask], y_raw[mask]

        if len(x_clean) >= 2 and np.std(x_clean) > 0 and np.std(y_clean) > 0:
            slope, intercept, r_value, p_value, std_err = stats.linregress(x_clean, y_clean)
            r_squared = r_value ** 2
            r_str = f"{r_value:+.4f}"
            slope_str = f"{slope:+.4f}"
            r2_str = f"{r_squared:.4f}"
            p_str = f"{p_value:.2e}"
            yield_10 = f"{slope * 10:+.1f}"
            r2_pct = f"{r_squared * 100:.1f}%"
        else:
            slope, intercept, r_value, p_value = 0.0, 0.0, 0.0, 1.0
            r_squared = 0.0
            r_str = "0.0000"
            slope_str = "0.0000"
            r2_str = "0.0000"
            p_str = "1.00e+00"
            yield_10 = "0.0"
            r2_pct = "0.0%"

        with col_viz:
            fig_scatter = px.scatter(
                clean_df, x="attendance_percentage", y="normalized_mark_pct", color="subject_id",
                title=f"Attendance vs Performance Bivariate Scatter Plot (r = {r_str}, p = {p_str})",
                labels={"attendance_percentage": "Attendance (%)", "normalized_mark_pct": "Score (%)"},
                height=380
            )
            if len(x_clean) >= 2 and np.std(x_clean) > 0:
                x_range = np.linspace(x_clean.min(), x_clean.max(), 100)
                fig_scatter.add_trace(go.Scatter(
                    x=x_range, y=slope * x_range + intercept,
                    mode='lines', name=f'OLS Trendline (R²={r2_str})',
                    line=dict(color='#E11D48', dash='dash', width=2)
                ))
            fig_scatter.update_layout(**PLOTLY_CONFIG)
            st.plotly_chart(fig_scatter, use_container_width=True, key="exec_scatter_plot")

        with col_stats:
            st.markdown("##### Statistical Parameters")
            st.metric("Pearson Correlation (r)", r_str)
            st.metric("Marginal Performance Yield (m)", f"{slope_str} marks / % att")
            st.metric("Attendance Determinacy (R²)", r2_str)

            with st.popover("Methodology & Business Context"):
                st.markdown("""
                **Institutional Context (NAAC Criterion 2.6):**
                * **Pearson Correlation (r):** Quantifies whether classroom presence directly translates to academic performance.
                * **Slope (m):** Estimates score change per attendance policy adjustment.
                * **Explanatory Power (R²):** Percentage of mark variance driven by attendance discipline.
                """)

        st.markdown(f"""
        <div class="insight-banner">
            <strong>Executive Decision Sensitivity Insight:</strong><br>
            • <strong>Pearson Performance Sensitivity (r = {r_str}, p = {p_str}):</strong> {"High positive relationship — lecture attendance directly impacts student exam performance." if r_value > 0.6 else "Moderate relationship — marks are partially independent of classroom presence." if r_value > 0.3 else "Low correlation — attendance has minimal linear impact on marks."}<br>
            • <strong>Marginal Yield Per 10% Attendance Shift (Slope m = {slope_str}):</strong> Every 10% increase in lecture attendance yields an expected <strong>{yield_10} mark increase</strong> in final evaluation.<br>
            • <strong>Attendance Determinacy Coefficient (R² = {r2_str}):</strong> Exactly {r2_pct} of overall evaluation score variance is driven by attendance discipline alone.
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(EMPTY_BANNER_HTML, unsafe_allow_html=True)

# ---------------------------------------------------------
# TAB 2: COURSE OUTCOMES & OBE ATTAINMENT
# ---------------------------------------------------------
with tab2:
    if clean_df is not None and not clean_df.empty:
        st.markdown("##### Subject Difficulty Index (SDI) & NBA/NAAC Course Outcome (CO) Attainment")
        
        st.dataframe(
            subject_summary[['subject_id', 'student_count', 'subject_mean', 'subject_median', 'subject_std', 'Subject Difficulty Index (SDI)', 'Pass Rate (%)', 'OBE Target Attainment']].style.format({
                "subject_mean": "{:.2f}%", "subject_median": "{:.2f}%", "subject_std": "{:.2f}",
                "Subject Difficulty Index (SDI)": "{:.2f}", "Pass Rate (%)": "{:.1f}%"
            }),
            use_container_width=True
        )
        
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            fig_box = px.box(
                clean_df, x="subject_id", y="z_score", color="subject_id", points="all",
                title="Subject Z-Score Standard Deviation Distribution",
                labels={"subject_id": "Subject Code", "z_score": "Standard Deviations (σ)"},
                height=380
            )
            fig_box.add_hline(y=0, line_dash="dash", line_color="gray", annotation_text="Mean Baseline (Z = 0)")
            fig_box.update_layout(**PLOTLY_CONFIG)
            st.plotly_chart(fig_box, use_container_width=True, key="obe_box_plot")
            
        with col_s2:
            fig_sdi = px.bar(
                subject_summary, x="subject_id", y="Subject Difficulty Index (SDI)", color="OBE Target Attainment",
                title="Subject Difficulty Index (SDI = 100 - Mean)",
                color_discrete_map={"Level 3 (High)": "#059669", "Level 2 (Moderate)": "#0284C7", "Level 1 (Low)": "#D97706", "Level 0 (Unattained)": "#E11D48"},
                height=380
            )
            fig_sdi.update_layout(**PLOTLY_CONFIG)
            st.plotly_chart(fig_sdi, use_container_width=True, key="obe_sdi_bar")

        hardest = subject_summary.sort_values('Subject Difficulty Index (SDI)', ascending=False).iloc[0]
        st.markdown(f"""
        <div class="insight-banner">
            <strong>Accreditation Compliance & Course Difficulty Insights:</strong><br>
            • <strong>Highest Difficulty Course:</strong> <code>{hardest['subject_id']}</code> (SDI = {hardest['Subject Difficulty Index (SDI)']:.1f}, Mean = {hardest['subject_mean']:.1f}%).<br>
            • <strong>Accreditation Intervention Trigger:</strong> Allocate additional Teaching Assistants (TAs) or remedial tutorial slots to <code>{hardest['subject_id']}</code> to protect NBA/NAAC attainment target metrics.<br>
            • <strong>Z-Score Standardization:</strong> Converts raw evaluation scores into Z-scores ($Z = \\frac{{X - \\mu}}{{\\sigma}}$) so students taking strict-grading courses are evaluated fairly against peer variance.
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(EMPTY_BANNER_HTML, unsafe_allow_html=True)

# ---------------------------------------------------------
# TAB 3: STUDENT 360 DIRECTORY & SCORECARDS
# ---------------------------------------------------------
with tab3:
    if clean_df is not None and not clean_df.empty:
        total_students = len(student_matrix)
        q1_students = (student_matrix['Risk Quadrant'] == "CRITICAL RISK (Q1)").sum()
        q4_students = (student_matrix['Risk Quadrant'] == "HIGH PERFORMER (Q4)").sum()
        avg_sgpa = student_matrix['est_sgpa'].mean()

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Enrolled Students", total_students)
        m2.metric("Critical Risk (Q1) Count", q1_students, delta=f"{q1_students} At-Risk", delta_color="inverse")
        m3.metric("High Performers (Q4)", q4_students, delta=f"{q4_students} Honor Candidates")
        m4.metric("Cohort Estimated SGPA", f"{avg_sgpa:.2f} / 10.0")

        st.markdown("---")
        search_col, filter_col = st.columns([2, 1])
        with search_col:
            search_query = st.text_input("Search Student Name or ID:", "", key="student_search_input").lower()
        with filter_col:
            selected_quadrant = st.selectbox("Filter Risk Category:", ["ALL", "CRITICAL RISK (Q1)", "ATTENDANCE RISK (Q2)", "ACADEMIC RISK (Q3)", "HIGH PERFORMER (Q4)"], key="student_risk_filter")

        filtered_students = student_matrix.copy()
        if search_query:
            filtered_students = filtered_students[
                filtered_students['student_name'].str.lower().str.contains(search_query) |
                filtered_students['student_id'].str.lower().str.contains(search_query)
            ]
        if selected_quadrant != "ALL":
            filtered_students = filtered_students[filtered_students['Risk Quadrant'] == selected_quadrant]

        st.markdown(f"Displaying **{len(filtered_students)} of {total_students} Student Profiles** (Refreshed Live with Sidebar Cutoffs):")
        
        card_cols = st.columns(2)
        for idx, (_, stu) in enumerate(filtered_students.iterrows()):
            col_target = card_cols[idx % 2]
            with col_target:
                badge_class = "badge-critical" if "Q1" in stu['Risk Quadrant'] else "badge-warning" if "Q2" in stu['Risk Quadrant'] else "badge-academic" if "Q3" in stu['Risk Quadrant'] else "badge-success"
                
                with st.expander(f"ID: {stu['student_id']} | {stu['student_name']} — Score: {stu['overall_mean_pct']:.1f}% | SGPA: {stu['est_sgpa']:.1f}"):
                    st.markdown(f"""
                    **Department:** `{stu['department']}` | **Risk Status:** <span class="status-badge {badge_class}">{stu['Risk Quadrant']}</span>  
                    **Academic Health Index (AHI):** `{stu['Academic Health Index (AHI)']} / 100`  
                    **Average Relative Z-Score:** `{stu['avg_z_score']:+.2f}σ`
                    """, unsafe_allow_html=True)
                    
                    st_records = clean_df[clean_df['student_id'] == stu['student_id']]
                    
                    if not st_records.empty:
                        r_student = st_records['normalized_mark_pct'].tolist()
                        r_student.append(r_student[0])
                        r_class = st_records['subject_mean'].tolist()
                        r_class.append(r_class[0])
                        theta_subjects = st_records['subject_id'].tolist()
                        theta_subjects.append(theta_subjects[0])

                        fig_radar = go.Figure()
                        fig_radar.add_trace(go.Scatterpolar(
                            r=r_student, theta=theta_subjects,
                            fill='toself', name='Student Score', line_color='#1A73E8'
                        ))
                        fig_radar.add_trace(go.Scatterpolar(
                            r=r_class, theta=theta_subjects,
                            fill='toself', name='Subject Class Avg', line_color='#94A3B8', opacity=0.5
                        ))
                        fig_radar.update_layout(
                            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                            height=250, margin=dict(l=20, r=20, t=20, b=20)
                        )
                        st.plotly_chart(
                            fig_radar,
                            use_container_width=True,
                            key=f"radar_chart_{stu['student_id']}_{idx}"
                        )

    else:
        st.markdown(EMPTY_BANNER_HTML, unsafe_allow_html=True)

# ---------------------------------------------------------
# TAB 4: 2D EARLY WARNING RISK MATRIX (REAL-TIME CUTOFFS)
# ---------------------------------------------------------
with tab4:
    if clean_df is not None and not clean_df.empty:
        def get_action(quadrant):
            if quadrant == "CRITICAL RISK (Q1)": return "Schedule Mandatory Faculty Counseling & Notify Parents"
            elif quadrant == "ATTENDANCE RISK (Q2)": return "Issue Official Low Attendance Warning Letter"
            elif quadrant == "ACADEMIC RISK (Q3)": return "Assign Remedial Peer Tutor & Subject Workshops"
            return "Regular Monitoring & Honor Roll Recognition"

        student_matrix['Recommended Action'] = student_matrix['Risk Quadrant'].apply(get_action)

        fig_quad = px.scatter(
            student_matrix, x="mean_attendance", y="avg_z_score", color="Risk Quadrant",
            hover_data=["student_id", "student_name", "overall_mean_pct", "Academic Health Index (AHI)"],
            title=f"2D Cartesian Early Warning Risk Matrix (Attendance Cutoff = {att_threshold}%, Z-Score Cutoff = {z_risk_threshold:.2f}σ)",
            labels={"mean_attendance": "Mean Attendance (%)", "avg_z_score": "Average Z-Score (σ)"},
            color_discrete_map={"CRITICAL RISK (Q1)": "#C5221F", "ATTENDANCE RISK (Q2)": "#B06000", "ACADEMIC RISK (Q3)": "#1A73E8", "HIGH PERFORMER (Q4)": "#137333"},
            height=400
        )
        fig_quad.add_vline(x=att_threshold, line_dash="dash", line_color="gray", annotation_text=f"Attendance Cutoff ({att_threshold}%)")
        fig_quad.add_hline(y=z_risk_threshold, line_dash="dash", line_color="gray", annotation_text=f"Z-Score Cutoff ({z_risk_threshold}σ)")
        fig_quad.update_layout(**PLOTLY_CONFIG)
        st.plotly_chart(fig_quad, use_container_width=True, key="risk_matrix_scatter")
        
        q1_count = (student_matrix['Risk Quadrant'] == "CRITICAL RISK (Q1)").sum()
        revenue_at_risk = q1_count * est_tuition_fee

        st.markdown("##### Institutional Resource Allocation & Tuition Loss Counter")
        r1, r2, r3, r4 = st.columns(4)
        r1.metric("Mandatory Counseling Slots", f"{q1_count} Sessions")
        r2.metric("Formal Intimation Notices", f"{(student_matrix['Risk Quadrant']=='ATTENDANCE RISK (Q2)').sum()} Notices")
        r3.metric("Remedial Mentorship Assignments", f"{(student_matrix['Risk Quadrant']=='ACADEMIC RISK (Q3)').sum()} Allocations")
        r4.metric("Tuition Revenue Exposure", f"₹{revenue_at_risk:,.0f}", delta=f"{q1_count} Attrition Risk", delta_color="inverse")

        st.dataframe(
            student_matrix[['student_id', 'student_name', 'department', 'mean_attendance', 'overall_mean_pct', 'est_sgpa', 'avg_z_score', 'Academic Health Index (AHI)', 'Risk Quadrant', 'Recommended Action']].style.format({
                "mean_attendance": "{:.1f}%", "overall_mean_pct": "{:.2f}%", "est_sgpa": "{:.2f}",
                "avg_z_score": "{:+.2f} σ", "Academic Health Index (AHI)": "{:.1f}"
            }),
            use_container_width=True
        )
        
        action_csv = student_matrix.to_csv(index=False).encode('utf-8')
        st.download_button(
            "Export Institutional Action Strategy Matrix (.csv)",
            data=action_csv,
            file_name=f"at_risk_action_matrix_{datetime.now().strftime('%Y%m%d')}.csv",
            key="dl_action_matrix_csv",
            use_container_width=True
        )

    else:
        st.markdown(EMPTY_BANNER_HTML, unsafe_allow_html=True)

# ---------------------------------------------------------
# TAB 5: LOCAL AI ACADEMIC ASSISTANT
# ---------------------------------------------------------
with tab5:
    if clean_df is not None and not clean_df.empty:
        st.markdown("##### AI Academic Query Assistant")
        st.caption("Ask questions about student attendance, risk levels, subject difficulty, or top/bottom performers in plain English.")
        
        if "messages" not in st.session_state:
            st.session_state.messages = [
                {"role": "assistant", "content": f"Hello! I am your Academic Assistant. The dataset contains **{len(student_matrix)} unique students** across **{clean_df['subject_id'].nunique()} subjects**. How can I help you analyze this batch?"}
            ]
            
        for msg in st.session_state.messages:
            st.chat_message(msg["role"]).write(msg["content"])
            
        if prompt := st.chat_input("e.g. Who are the critical risk students? What is the hardest subject?", key="ai_chat_input_prompt"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            st.chat_message("user").write(prompt)
            
            q_lower = prompt.lower()
            response = ""

            is_dropout_or_poor = any(w in q_lower for w in [
                "drop", "dropout", "dropped", "poor", "poorest", "worst", "fail", "failing", 
                "bottom", "low mark", "struggle", "struggling", "critical", "q1", "risk", "at-risk", "at risk"
            ])

            is_top_or_best = any(w in q_lower for w in ["top", "best", "highest", "topper", "rank", "merit", "excel"]) and not is_dropout_or_poor

            is_attendance_query = any(w in q_lower for w in ["attendance", "detain", "detained", "shortage", "absent", "q2"]) and not is_top_or_best and not is_dropout_or_poor

            is_subject_query = any(w in q_lower for w in ["hardest", "difficult", "sdi", "subject", "course", "tough"])

            if is_dropout_or_poor:
                crit_df = student_matrix[student_matrix['Risk Quadrant'] == "CRITICAL RISK (Q1)"]
                
                if not crit_df.empty and ("q1" in q_lower or "critical" in q_lower or "counseling" in q_lower):
                    names = ", ".join([f"**{row['student_name']}** ({row['student_id']})" for _, row in crit_df.iterrows()])
                    response = f"There are **{len(crit_df)} students** in **Critical Risk (Q1)** requiring immediate intervention:\n\n{names}\n\n*Recommended Action:* Scheduled for mandatory faculty counseling & parent intimation."
                else:
                    bottom_df = student_matrix.sort_values('Academic Health Index (AHI)', ascending=True).head(5)
                    bottom_list = "\n".join([
                        f"{idx+1}. **{row['student_name']}** ({row['student_id']}) — Score: **{row['overall_mean_pct']:.1f}%**, Att: **{row['mean_attendance']:.1f}%**, AHI: **{row['Academic Health Index (AHI)']} / 100** [{row['Risk Quadrant']}]"
                        for idx, (_, row) in enumerate(bottom_df.iterrows())
                    ])
                    response = f"Here are the **5 lowest performing students** (ranked by Academic Health Index):\n\n{bottom_list}\n\n*Recommended Action:* High dropout risk — issue formal academic intimation letters immediately."

            elif is_top_or_best:
                top_df = student_matrix.sort_values('overall_mean_pct', ascending=False).head(5)
                top_list = "\n".join([
                    f"{idx+1}. **{row['student_name']}** ({row['student_id']}) — Score: **{row['overall_mean_pct']:.1f}%**, SGPA: **{row['est_sgpa']:.1f}**"
                    for idx, (_, row) in enumerate(top_df.iterrows())
                ])
                response = f"Here are the **top 5 high-performing students** by overall academic score:\n\n{top_list}"

            elif is_subject_query:
                hardest = subject_summary.sort_values('Subject Difficulty Index (SDI)', ascending=False).iloc[0]
                response = f"The hardest course is **{hardest['subject_id']}** with a Subject Difficulty Index (SDI) of **{hardest['Subject Difficulty Index (SDI)']:.1f}** and an average class mark of **{hardest['subject_mean']:.1f}%**."

            elif is_attendance_query:
                low_att = student_matrix[student_matrix['mean_attendance'] < att_threshold]
                response = f"There are **{len(low_att)} students** below the mandatory attendance threshold of **{att_threshold}%**."

            else:
                batch_avg = clean_df['normalized_mark_pct'].mean()
                batch_att = clean_df['attendance_percentage'].mean()
                response = f"Cohort Summary: Overall Average Score is **{batch_avg:.1f}%** and Average Attendance is **{batch_att:.1f}%**. Ask me to list 'critical risk students', 'poorest performers', 'top performers', or 'hardest subject'."

            st.session_state.messages.append({"role": "assistant", "content": response})
            st.chat_message("assistant").write(response)

    else:
        st.markdown(EMPTY_BANNER_HTML, unsafe_allow_html=True)
