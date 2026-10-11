import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from scipy import stats
import io
from datetime import datetime

# ---------------------------------------------------------
# 1. PAGE CONFIGURATION & HIGH-DENSITY SAAS DESIGN SYSTEM
# ---------------------------------------------------------
st.set_page_config(
    page_title="BIT Academic Decision Intelligence Platform",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom High-Density CSS Architecture (Datadog / Snowflake Dark Slate Theme)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] { 
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; 
        -webkit-font-smoothing: antialiased;
    }
    
    /* Zero Whitespace Viewport Optimization */
    .block-container {
        padding-top: 1.1rem !important;
        padding-bottom: 1.2rem !important;
        padding-left: 1.2rem !important;
        padding-right: 1.2rem !important;
        max-width: 100% !important;
    }
    
    [data-testid="stVerticalBlock"] { gap: 0.65rem !important; }

    /* Responsive SaaS Header Banner */
    .enterprise-navbar {
        width: 100%;
        box-sizing: border-box;
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: #0F172A;
        color: #FFFFFF;
        padding: 16px 24px;
        border-radius: 8px;
        margin-bottom: 14px;
        border-left: 6px solid #4F46E5;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .enterprise-navbar .brand-title { font-size: 18px; font-weight: 800; color: #F8FAFC; letter-spacing: -0.02em; }
    .enterprise-navbar .brand-sub { font-size: 12.5px; color: #94A3B8; font-weight: 400; margin-left: 8px; }
    .enterprise-navbar .status-tag {
        background: #1E293B; border: 1px solid #334155; color: #38BDF8;
        padding: 5px 14px; border-radius: 9999px; font-size: 11px; font-weight: 700; text-transform: uppercase;
    }

    /* KPI Grid Cards */
    .kpi-tile {
        background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px;
        padding: 14px 18px; box-shadow: 0 1px 3px rgba(0,0,0,0.03); transition: all 0.2s;
        box-sizing: border-box; width: 100%;
    }
    .kpi-tile:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.06); border-color: #CBD5E1; }
    .kpi-title { font-size: 11px; font-weight: 700; color: #64748B; text-transform: uppercase; letter-spacing: 0.05em; }
    .kpi-value { font-size: 26px; font-weight: 800; color: #0F172A; margin-top: 2px; line-height: 1.1; }
    .kpi-meta { font-size: 11px; font-weight: 600; margin-top: 4px; }
    .sub-good { color: #059669; } .sub-bad { color: #E11D48; } .sub-info { color: #0284C7; }

    /* Custom Badges & SaaS Cards */
    .badge { display: inline-block; padding: 3px 9px; border-radius: 4px; font-size: 10.5px; font-weight: 700; text-transform: uppercase; }
    .badge-critical { background: #FFE4E6; color: #E11D48; }
    .badge-warning { background: #FEF3C7; color: #D97706; }
    .badge-academic { background: #E0F2FE; color: #0369A1; }
    .badge-success { background: #D1FAE5; color: #059669; }

    .insight-banner {
        background-color: #F8FAFC; border: 1px solid #E2E8F0; border-left: 4px solid #4F46E5;
        padding: 14px 18px; border-radius: 6px; font-size: 13px; color: #334155; line-height: 1.6;
        margin-top: 8px; margin-bottom: 8px;
    }

    .empty-banner {
        background: #FFFFFF; border: 2px dashed #CBD5E1; border-radius: 8px;
        padding: 40px; text-align: center; color: #64748B; margin: 20px 0;
    }
    .empty-banner-title { font-size: 16px; font-weight: 700; color: #334155; margin-bottom: 4px; }
    .empty-banner-sub { font-size: 13px; color: #94A3B8; }

    /* Enhanced Streamlit Main Workspace Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px !important;
        border-bottom: 2px solid #E2E8F0 !important;
        background-color: #F8FAFC;
        padding: 6px 10px 0px 10px;
        border-radius: 8px 8px 0 0;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 20px !important;
        font-size: 13.5px !important;
        font-weight: 700 !important;
        color: #64748B !important;
        border-radius: 6px 6px 0 0 !important;
        transition: all 0.2s;
    }
    .stTabs [aria-selected="true"] {
        color: #4F46E5 !important;
        background-color: #FFFFFF !important;
        border-top: 3px solid #4F46E5 !important;
        box-shadow: 0 -2px 4px rgba(0,0,0,0.03);
    }

    .section-lbl { font-size: 13px; font-weight: 800; color: #0F172A; text-transform: uppercase; letter-spacing: 0.04em; margin: 10px 0 6px 0; }
</style>
""", unsafe_allow_html=True)

# Top Application Banner
st.markdown("""
<div class="enterprise-navbar">
    <div>
        <span class="brand-title">ACADEMIC DECISION INTELLIGENCE PLATFORM</span>
        <span class="brand-sub"> &nbsp;|&nbsp; Bannari Amman Institute of Technology — Outcome Governance & Retention Analytics</span>
    </div>
    <div class="status-tag">PIPELINE SECURE</div>
</div>
""", unsafe_allow_html=True)

PLOTLY_CONFIG = dict(
    font=dict(family="Inter, sans-serif", color="#334155", size=12),
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#FFFFFF",
    margin=dict(l=35, r=20, t=35, b=35),
    xaxis=dict(showgrid=True, gridcolor="#F1F5F9", linecolor="#CBD5E1"),
    yaxis=dict(showgrid=True, gridcolor="#F1F5F9", linecolor="#CBD5E1")
)

# ---------------------------------------------------------
# 2. SCHEMA NORMALIZATION & DYNAMIC ALIASING
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

# ---------------------------------------------------------
# 3. SIDEBAR INSTITUTIONAL POLICY CONTROLS
# ---------------------------------------------------------
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/analytics.png", width=54)
    st.markdown("<div class='section-lbl'>Institutional Policy Cutoffs</div>", unsafe_allow_html=True)
    
    att_threshold = st.slider(
        "Attendance Cutoff (%)", 50.0, 90.0, 75.0, 1.0,
        help="Mandatory university attendance threshold. Below this cutoff triggers an Attendance Warning or Critical At-Risk flag."
    )
    z_risk_threshold = st.slider(
        "Critical Z-Score Cutoff (\u03c3)", -2.0, 0.0, -0.5, 0.1,
        help="Standard deviation cutoff relative to subject average. Scores below this threshold signal severe relative academic underperformance."
    )
    est_tuition_fee = st.number_input(
        "Annual Tuition Fee (\u20b9)", value=125000, step=5000,
        help="Annual departmental tuition fee per student used to calculate total financial tuition revenue exposure for at-risk students."
    )

# ---------------------------------------------------------
# 4. STATISTICAL & CALCULATIVE PIPELINE (CACHED)
# ---------------------------------------------------------
@st.cache_data(show_spinner=False)
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
            
            if att < 0.0 or att > 100.0: reasons.append(f"Invalid Attendance [{att}%]")
            if marks < 0.0 or marks > max_m: reasons.append(f"Invalid Marks [{marks}/{max_m}]")
                
            if not reasons:
                pct_score = (marks / max_m) * 100.0
                clean_rows.append({
                    "student_id": s_id, "student_name": s_name, "department": dept,
                    "subject_id": sub_id, "academic_semester": sem,
                    "attendance_percentage": att, "marks_obtained": marks,
                    "maximum_marks": max_m, "normalized_mark_pct": pct_score
                })
        except ValueError:
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

    # Indian 10-Point Grade Point (GPA/SGPA Scale)
    def mark_to_gpa(pct):
        if pct >= 90: return 10.0 # O Grade
        elif pct >= 80: return 9.0  # A+ Grade
        elif pct >= 70: return 8.0  # A Grade
        elif pct >= 60: return 7.0  # B+ Grade
        elif pct >= 50: return 6.0  # B Grade
        return 0.0                  # Re-Approve (RA)

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

    # Risk Quadrant Classification
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
# 5. INGESTION CONSOLE (FULL-WIDTH TOP SECTION)
# ---------------------------------------------------------
st.markdown("<div class='section-lbl'>1. Data Ingestion & Sanitation Audit Console</div>", unsafe_allow_html=True)

col_ingest, col_template = st.columns([3, 1])
with col_ingest:
    uploaded_file = st.file_uploader(
        "Ingest Academic Data File (.csv or .xlsx)", type=["csv", "xlsx"],
        help="Upload raw academic dataset containing student marks, attendance, and subject details."
    )

with col_template:
    st.markdown("**Contract Schema**")
    template_data = pd.DataFrame({
        "student_id": ["BIT26CS001"], "student_name": ["Aarav Sharma"], "department": ["CSE"],
        "subject_id": ["MA3151_Maths"], "attendance_percentage": [88.5],
        "marks_obtained": [82.0], "maximum_marks": [100.0], "academic_semester": ["SEM_05"]
    })
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine='openpyxl') as writer:
        template_data.to_excel(writer, index=False, sheet_name='Data_Contract')
    st.download_button("Download Schema Contract (.xlsx)", data=buf.getvalue(), file_name="academic_schema_contract.xlsx", use_container_width=True)

clean_df, audit_df, subject_summary, student_matrix = None, None, None, None

if uploaded_file is not None:
    raw_df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
    clean_df, audit_df, subject_summary, student_matrix, missing = run_analytics_pipeline(raw_df, att_threshold, z_risk_threshold)
    
    if missing:
        st.error(f"Data Contract Violation: Could not resolve required fields {missing}. Download and use the standard schema template above.")
        st.stop()
        
    total_received = len(raw_df)
    clean_count = len(clean_df) if clean_df is not None else 0
    flagged_count = len(audit_df)
    health_score = round((clean_count / total_received) * 100, 2) if total_received > 0 else 0.0

    k1, k2, k3, k4 = st.columns(4)
    k1.metric(
        "Records Ingested", total_received,
        help="Total raw row count received from the uploaded dataset stream."
    )
    k2.metric(
        "Clean Records Persisted", clean_count,
        help="Validated, non-duplicate records successfully loaded into the statistical pipeline."
    )
    k3.metric(
        "Anomalies Isolated", flagged_count, delta=f"{flagged_count} Rejections", delta_color="inverse",
        help="Records rejected due to missing IDs, out-of-bounds percentages (>100% or <0%), or non-numeric types."
    )
    k4.metric(
        "Data Health Score", f"{health_score}%",
        delta="NAAC Ready" if health_score >= 90 else "Action Required",
        delta_color="normal" if health_score >= 90 else "inverse",
        help="Percentage of clean records over total received. NAAC/NBA criteria require a health score >= 90% for valid audit reporting."
    )
    
    if not audit_df.empty:
        with st.expander("View Isolated Anomaly Audit Trail Log", expanded=False):
            st.dataframe(audit_df, use_container_width=True)

# ---------------------------------------------------------
# 6. MAIN WORKSPACE TABS
# ---------------------------------------------------------
st.markdown("<div class='section-lbl'>2. Academic Decision Intelligence Hub</div>", unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Executive Control & Sensitivity Analysis",
    "🎯 OBE & Course Outcome Attainment",
    "👤 Student 360° Directory & Scorecards",
    "🛡️ Early Warning Matrix & Financial Retention",
    "💬 Local AI Academic Assistant"
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
        m1.metric("Class Average Score", f"{batch_avg_mark:.2f}%", help="Mean percentage mark obtained across all subjects and students.")
        m2.metric("Class Average Attendance", f"{batch_avg_att:.1f}%", help="Mean lecture attendance percentage across the cohort.")
        m3.metric("Cohort Health Index (AHI)", f"{batch_ahi:.1f} / 100", help="Weighted index combining 60% academic performance and 40% attendance discipline.")
        m4.metric("Class Pass Rate (\u2265 50%)", f"{pass_rate:.1f}%", help="Percentage of cohort maintaining an overall passing grade (>= 50%).")

        col_viz, col_stats = st.columns([2, 1])
        with col_viz:
            x = clean_df['attendance_percentage'].values
            y = clean_df['normalized_mark_pct'].values
            
            # Rigorous Statistical Regression using SciPy
            slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
            r_squared = r_value ** 2

            fig_scatter = px.scatter(
                clean_df, x="attendance_percentage", y="normalized_mark_pct", color="subject_id",
                title=f"Attendance vs Marks Scatter Plot ($r$ = {r_value:+.3f}, $p$ = {p_value:.2e})",
                labels={"attendance_percentage": "Attendance (%)", "normalized_mark_pct": "Score (%)"},
                height=380
            )
            if len(clean_df) > 1 and np.std(x) > 0:
                x_range = np.linspace(x.min(), x.max(), 100)
                fig_scatter.add_trace(go.Scatter(x=x_range, y=slope * x_range + intercept, mode='lines', name=f'OLS Trendline (R²={r_squared:.2f})', line=dict(color='#E11D48', dash='dash', width=2)))
            fig_scatter.update_layout(**PLOTLY_CONFIG)
            st.plotly_chart(fig_scatter, use_container_width=True)

        with col_stats:
            st.markdown("##### Statistical Parameters")
            st.metric("Pearson Correlation ($r$)", f"{r_value:+.4f}", help="Linear relationship strength between attendance and marks (-1.0 to +1.0).")
            st.metric("Regression Slope ($m$)", f"{slope:+.4f} marks / % att", help="Grade yield: expected mark increase for every 1% increase in attendance.")
            st.metric("Explanatory Power ($R^2$)", f"{r_squared:.4f}", help="Proportion of total score variance explained by attendance alone.")

            with st.popover("❓ Business Context & Methodology"):
                st.markdown("""
                **Institutional Context (NAAC Criterion 2.6):**
                * **Pearson Correlation ($r$):** Quantifies whether classroom presence directly translates to academic success.
                * **Slope ($m$):** Used by Deans to calculate grade improvement per attendance policy shift.
                * **Explanatory Power ($R^2$):** Demonstrates what percentage of academic variance is driven by attendance vs. external factors (self-study, foundational skill).
                """)

        st.markdown(f"""
        <div class="insight-banner">
            <strong>Statistical Sensitivity Insight:</strong><br>
            • <strong>Pearson Correlation (r = {r_value:+.4f}, p = {p_value:.2e}):</strong> {"High positive relationship — lecture attendance directly impacts student exam performance." if r_value > 0.6 else "Moderate relationship — marks are partially independent of classroom presence." if r_value > 0.3 else "Low correlation — attendance has minimal linear impact on marks."}<br>
            • <strong>Yield Per Lecture (Slope m = {slope:+.2f}):</strong> Every 10% increase in attendance yields an expected <strong>+{slope*10:.1f} mark increase</strong> in final performance.<br>
            • <strong>Explanatory Power (R² = {r_squared:.2f}):</strong> Exactly {r_squared*100:.1f}% of overall score variance is driven by attendance alone.
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(empty_banner_html, unsafe_allow_html=True)

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
                labels={"subject_id": "Subject Code", "z_score": "Standard Deviations (\u03c3)"},
                height=380
            )
            fig_box.add_hline(y=0, line_dash="dash", line_color="gray", annotation_text="Mean Baseline (Z = 0)")
            fig_box.update_layout(**PLOTLY_CONFIG)
            st.plotly_chart(fig_box, use_container_width=True)
            
        with col_s2:
            fig_sdi = px.bar(
                subject_summary, x="subject_id", y="Subject Difficulty Index (SDI)", color="OBE Target Attainment",
                title="Subject Difficulty Index (SDI = 100 - Mean)",
                color_discrete_map={"Level 3 (High)": "#059669", "Level 2 (Moderate)": "#0284C7", "Level 1 (Low)": "#D97706", "Level 0 (Unattained)": "#E11D48"},
                height=380
            )
            fig_sdi.update_layout(**PLOTLY_CONFIG)
            st.plotly_chart(fig_sdi, use_container_width=True)

        hardest = subject_summary.sort_values('Subject Difficulty Index (SDI)', ascending=False).iloc[0]
        st.markdown(f"""
        <div class="insight-banner">
            <strong>Accreditation Compliance & Course Difficulty Insights:</strong><br>
            • <strong>Highest Difficulty Course:</strong> <code>{hardest['subject_id']}</code> (SDI = {hardest['Subject Difficulty Index (SDI)']:.1f}, Mean = {hardest['subject_mean']:.1f}%).<br>
            • <strong>Accreditation Trigger:</strong> Allocate additional Teaching Assistants (TAs) or remedial tutorial slots to <code>{hardest['subject_id']}</code> to protect NBA/NAAC attainment target metrics.<br>
            • <strong>Z-Score Normalization:</strong> Converts raw evaluation scores into Z-scores ($Z = \\frac{{X - \\mu}}{{\\sigma}}$) so students taking strict-grading courses are evaluated fairly against peer variance.
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(empty_banner_html, unsafe_allow_html=True)

# ---------------------------------------------------------
# TAB 3: STUDENT DIRECTORY & 360° SCORECARD
# ---------------------------------------------------------
with tab3:
    if clean_df is not None and not clean_df.empty:
        total_students = len(student_matrix)
        q1_students = (student_matrix['Risk Quadrant'] == "CRITICAL RISK (Q1)").sum()
        q4_students = (student_matrix['Risk Quadrant'] == "HIGH PERFORMER (Q4)").sum()
        avg_sgpa = student_matrix['est_sgpa'].mean()

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Enrolled Students", total_students, help="Count of unique student IDs in current batch.")
        m2.metric("Critical Risk (Q1) Count", q1_students, delta=f"{q1_students} At-Risk", delta_color="inverse", help="Students failing both attendance and performance benchmarks.")
        m3.metric("High Performers (Q4)", q4_students, delta=f"{q4_students} Honor Candidates", help="Students meeting or exceeding both attendance and performance benchmarks.")
        m4.metric("Cohort Estimated SGPA", f"{avg_sgpa:.2f} / 10.0", help="Estimated Semester Grade Point Average based on Indian 10-point scale.")

        st.markdown("---")
        search_col, filter_col = st.columns([2, 1])
        with search_col:
            search_query = st.text_input("Search Student Name or ID:", "", help="Filter student profiles in real time.").lower()
        with filter_col:
            selected_quadrant = st.selectbox("Filter Risk Category:", ["ALL", "CRITICAL RISK (Q1)", "ATTENDANCE RISK (Q2)", "ACADEMIC RISK (Q3)", "HIGH PERFORMER (Q4)"])

        filtered_students = student_matrix.copy()
        if search_query:
            filtered_students = filtered_students[
                filtered_students['student_name'].str.lower().str.contains(search_query) |
                filtered_students['student_id'].str.lower().str.contains(search_query)
            ]
        if selected_quadrant != "ALL":
            filtered_students = filtered_students[filtered_students['Risk Quadrant'] == selected_quadrant]

        st.markdown(f"Displaying **{len(filtered_students)} of {total_students} Student Profiles**:")
        
        card_cols = st.columns(2)
        for idx, (_, stu) in enumerate(filtered_students.iterrows()):
            col_target = card_cols[idx % 2]
            with col_target:
                badge_class = "badge-critical" if "Q1" in stu['Risk Quadrant'] else "badge-warning" if "Q2" in stu['Risk Quadrant'] else "badge-academic" if "Q3" in stu['Risk Quadrant'] else "badge-success"
                
                with st.expander(f"👤 {stu['student_name']} ({stu['student_id']}) — Score: {stu['overall_mean_pct']:.1f}% | SGPA: {stu['est_sgpa']:.1f}"):
                    st.markdown(f"""
                    **Department:** `{stu['department']}` | **Risk Status:** <span class="badge {badge_class}">{stu['Risk Quadrant']}</span>  
                    **Academic Health Index (AHI):** `{stu['Academic Health Index (AHI)']} / 100`  
                    **Average Relative Z-Score:** `{stu['avg_z_score']:+.2f}\u03c3`
                    """, unsafe_allow_html=True)
                    
                    st_records = clean_df[clean_df['student_id'] == stu['student_id']]
                    
                    fig_radar = go.Figure()
                    fig_radar.add_trace(go.Scatterpolar(
                        r=st_records['normalized_mark_pct'].tolist() + [st_records['normalized_mark_pct'].iloc[0]],
                        theta=st_records['subject_id'].tolist() + [st_records['subject_id'].iloc[0]],
                        fill='toself', name='Student Score', line_color='#4F46E5'
                    ))
                    fig_radar.add_trace(go.Scatterpolar(
                        r=st_records['subject_mean'].tolist() + [st_records['subject_mean'].iloc[0]],
                        theta=st_records['subject_id'].tolist() + [st_records['subject_id'].iloc[0]],
                        fill='toself', name='Subject Class Avg', line_color='#94A3B8', opacity=0.5
                    ))
                    fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), height=250, margin=dict(l=20, r=20, t=20, b=20))
                    st.plotly_chart(fig_radar, use_container_width=True)

    else:
        st.markdown(empty_banner_html, unsafe_allow_html=True)

# ---------------------------------------------------------
# TAB 4: EARLY WARNING MATRIX & FINANCIAL LOSS
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
            title="2D Cartesian Early Warning Risk Matrix (Attendance vs. Z-Score Deviation)",
            labels={"mean_attendance": "Mean Attendance (%)", "avg_z_score": "Average Z-Score (\u03c3)"},
            color_discrete_map={"CRITICAL RISK (Q1)": "#E11D48", "ATTENDANCE RISK (Q2)": "#D97706", "ACADEMIC RISK (Q3)": "#0284C7", "HIGH PERFORMER (Q4)": "#059669"},
            height=400
        )
        fig_quad.add_vline(x=att_threshold, line_dash="dash", line_color="gray", annotation_text=f"Attendance Cutoff ({att_threshold}%)")
        fig_quad.add_hline(y=z_risk_threshold, line_dash="dash", line_color="gray", annotation_text=f"Z-Score Cutoff ({z_risk_threshold}\u03c3)")
        fig_quad.update_layout(**PLOTLY_CONFIG)
        st.plotly_chart(fig_quad, use_container_width=True)
        
        q1_count = (student_matrix['Risk Quadrant'] == "CRITICAL RISK (Q1)").sum()
        revenue_at_risk = q1_count * est_tuition_fee

        st.markdown("##### Resource Allocation & Financial Attrition Loss Counter")
        r1, r2, r3, r4 = st.columns(4)
        r1.metric("Counseling Slots Required", f"{q1_count} Sessions", help="Number of 1-on-1 counseling slots needed for Q1 students.")
        r2.metric("Warning Letters Required", f"{(student_matrix['Risk Quadrant']=='ATTENDANCE RISK (Q2)').sum()} Letters", help="Official attendance warning letters to issue.")
        r3.metric("Remedial Tutors Required", f"{(student_matrix['Risk Quadrant']=='ACADEMIC RISK (Q3)').sum()} Tutors", help="Peer tutoring assignments required for academic risk students.")
        r4.metric("Tuition Revenue At-Risk", f"\u20b9{revenue_at_risk:,.0f}", delta=f"{q1_count} Dropout Candidates", delta_color="inverse", help="Total annual tuition revenue exposed to dropout risk.")

        st.dataframe(
            student_matrix[['student_id', 'student_name', 'department', 'mean_attendance', 'overall_mean_pct', 'est_sgpa', 'avg_z_score', 'Academic Health Index (AHI)', 'Risk Quadrant', 'Recommended Action']].style.format({
                "mean_attendance": "{:.1f}%", "overall_mean_pct": "{:.2f}%", "est_sgpa": "{:.2f}",
                "avg_z_score": "{:+.2f} \u03c3", "Academic Health Index (AHI)": "{:.1f}"
            }),
            use_container_width=True
        )
        
        action_csv = student_matrix.to_csv(index=False).encode('utf-8')
        st.download_button("Export Institutional Action Strategy Matrix (.csv)", data=action_csv, file_name=f"at_risk_action_matrix_{datetime.now().strftime('%Y%m%d')}.csv", use_container_width=True)

    else:
        st.markdown(empty_banner_html, unsafe_allow_html=True)

# ---------------------------------------------------------
# TAB 5: LOCAL AI ACADEMIC QUERY ASSISTANT
# ---------------------------------------------------------
with tab5:
    if clean_df is not None and not clean_df.empty:
        st.markdown("##### AI Academic Query Assistant")
        st.caption("Ask questions about student attendance, risk levels, subject difficulty, or top performers in plain English.")
        
        if "messages" not in st.session_state:
            st.session_state.messages = [
                {"role": "assistant", "content": f"Hello! I am your Academic Assistant. The dataset contains **{len(student_matrix)} unique students** across **{clean_df['subject_id'].nunique()} subjects**. How can I help you analyze this batch?"}
            ]
            
        for msg in st.session_state.messages:
            st.chat_message(msg["role"]).write(msg["content"])
            
        if prompt := st.chat_input("e.g. Who are the critical risk students? What is the hardest subject?"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            st.chat_message("user").write(prompt)
            
            query_lower = prompt.lower()
            response = ""
            
            if "critical" in query_lower or "q1" in query_lower or "risk" in query_lower:
                crit_df = student_matrix[student_matrix['Risk Quadrant'] == "CRITICAL RISK (Q1)"]
                if not crit_df.empty:
                    names = ", ".join([f"**{row['student_name']}** ({row['student_id']})" for _, row in crit_df.iterrows()])
                    response = f"There are **{len(crit_df)} students** in Critical Risk (Q1):\n\n{names}\n\n*Recommended Action:* Scheduled for mandatory faculty counseling & parent intimation."
                else:
                    response = "Great news! There are currently zero students flagged in Critical Risk (Q1)."
                    
            elif "top" in query_lower or "best" in query_lower or "performer" in query_lower:
                top_df = student_matrix.sort_values('overall_mean_pct', ascending=False).head(5)
                top_list = "\n".join([f"1. **{row['student_name']}** ({row['student_id']}) — Score: {row['overall_mean_pct']:.1f}%, SGPA: {row['est_sgpa']:.1f}" for _, row in top_df.iterrows()])
                response = f"Here are the top 5 students by overall academic score:\n\n{top_list}"
                
                
            elif "hardest" in query_lower or "difficult" in query_lower or "subject" in query_lower:
                hardest = subject_summary.sort_values('Subject Difficulty Index (SDI)', ascending=False).iloc[0]
                response = f"The hardest course is **{hardest['subject_id']}** with a Subject Difficulty Index (SDI) of **{hardest['Subject Difficulty Index (SDI)']:.1f}** and an average mark of **{hardest['subject_mean']:.1f}%**."
                
            elif "attendance" in query_lower or "low attendance" in query_lower:
                low_att = student_matrix[student_matrix['mean_attendance'] < att_threshold]
                response = f"There are **{len(low_att)} students** below the mandatory attendance threshold of {att_threshold}%."
                
            else:
                batch_avg = clean_df['normalized_mark_pct'].mean()
                batch_att = clean_df['attendance_percentage'].mean()
                response = f"Cohort Summary: Overall Average Score is **{batch_avg:.1f}%** and Average Attendance is **{batch_att:.1f}%**. You can ask me to list at-risk students, top performers, or subject metrics!"
                
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.chat_message("assistant").write(response)

    else:
        st.markdown(empty_banner_html, unsafe_allow_html=True)
