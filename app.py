import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import io
from datetime import datetime

# ---------------------------------------------------------
# 1. ENTERPRISE CONFIGURATION & HIGH-DENSITY CSS
# ---------------------------------------------------------
st.set_page_config(
    page_title="Academic Decision Intelligence Platform",
    page_icon="https://img.icons8.com/ios-filled/50/4f46e5/analytics.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .block-container {
        padding-top: 1.25rem !important;
        padding-bottom: 1.5rem !important;
        padding-left: 1.5rem !important;
        padding-right: 1.5rem !important;
        max-width: 100% !important;
    }
    
    [data-testid="stVerticalBlock"] {
        gap: 0.75rem !important;
    }

    .top-navbar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: #0F172A;
        color: #FFFFFF;
        padding: 12px 20px;
        border-radius: 8px;
        margin-bottom: 12px;
        border-left: 4px solid #4F46E5;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .top-navbar .brand-title {
        font-size: 16px;
        font-weight: 800;
        letter-spacing: -0.01em;
        color: #F8FAFC;
    }
    .top-navbar .brand-sub {
        font-size: 12px;
        color: #94A3B8;
        font-weight: 400;
    }
    .top-navbar .status-tag {
        background: #1E293B;
        border: 1px solid #334155;
        color: #38BDF8;
        padding: 4px 10px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
    }

    .kpi-tile {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 6px;
        padding: 12px 16px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.02);
    }
    .kpi-title {
        font-size: 11px;
        font-weight: 700;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .kpi-value {
        font-size: 22px;
        font-weight: 800;
        color: #0F172A;
        line-height: 1.2;
        margin-top: 2px;
    }
    .kpi-meta {
        font-size: 11px;
        font-weight: 600;
        margin-top: 4px;
    }
    .sub-good { color: #059669; }
    .sub-bad { color: #E11D48; }
    .sub-info { color: #0284C7; }

    .stTabs [data-baseweb="tab-list"] {
        gap: 6px !important;
        border-bottom: 2px solid #E2E8F0 !important;
        background: #F8FAFC;
        padding: 6px 8px 0px 8px;
        border-radius: 8px 8px 0 0;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 8px 18px !important;
        border-radius: 6px 6px 0 0 !important;
        font-size: 13px !important;
        font-weight: 600 !important;
        color: #64748B !important;
    }
    .stTabs [aria-selected="true"] {
        background: #FFFFFF !important;
        color: #4F46E5 !important;
        border-top: 3px solid #4F46E5 !important;
        box-shadow: 0 -1px 3px rgba(0,0,0,0.03);
    }

    .insight-banner {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-left: 4px solid #4F46E5;
        padding: 12px 16px;
        border-radius: 6px;
        font-size: 12.5px;
        color: #334155;
        line-height: 1.6;
        margin-top: 10px;
        margin-bottom: 10px;
    }

    .empty-state {
        background: #FFFFFF;
        border: 2px dashed #E2E8F0;
        border-radius: 8px;
        padding: 40px;
        text-align: center;
        color: #64748B;
        margin: 20px 0;
    }
    .empty-state-title {
        font-size: 16px;
        font-weight: 700;
        color: #334155;
        margin-bottom: 6px;
    }
    .empty-state-sub {
        font-size: 13px;
        color: #94A3B8;
    }

    .section-label {
        font-size: 13px;
        font-weight: 700;
        color: #0F172A;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        margin-top: 8px;
        margin-bottom: 8px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="top-navbar">
    <div>
        <span class="brand-title">ACADEMIC DECISION INTELLIGENCE PLATFORM</span>
        <span class="brand-sub"> &nbsp;|&nbsp; Enterprise Normalization, OBE Outcome Attainment & Retention Risk Model</span>
    </div>
    <div class="status-tag">SYSTEM ACTIVE</div>
</div>
""", unsafe_allow_html=True)

PLOTLY_CONFIG = dict(
    font=dict(family="Inter, sans-serif", color="#334155", size=12),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="#FFFFFF",
    margin=dict(l=40, r=20, t=40, b=40),
    xaxis=dict(showgrid=True, gridcolor="#F1F5F9", linecolor="#CBD5E1"),
    yaxis=dict(showgrid=True, gridcolor="#F1F5F9", linecolor="#CBD5E1")
)

# ---------------------------------------------------------
# 2. SCHEMA NORMALIZATION & ALIASING MAP
# ---------------------------------------------------------
ALIAS_MAP = {
    'student_id': ['student_id', 'roll_no', 'register_no', 'usn', 'id', 'student_code'],
    'student_name': ['student_name', 'name', 'full_name', 'candidate_name'],
    'subject_id': ['subject_id', 'subject_code', 'course_id', 'subject'],
    'attendance_percentage': ['attendance_percentage', 'attendance', 'attendance_pct', 'att_%', 'att'],
    'marks_obtained': ['marks_obtained', 'marks', 'score', 'obtained_marks', 'total_marks'],
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
# 3. SIDEBAR GOVERNANCE CONTROLS
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("<div class='section-label'>Institutional Controls</div>", unsafe_allow_html=True)
    st.markdown("---")
    att_threshold = st.slider("Attendance Minimum Cutoff (%)", 50.0, 90.0, 75.0, 1.0)
    z_risk_threshold = st.slider("Critical Z-Score Risk Cutoff (\u03c3)", -2.0, 0.0, -0.5, 0.1)
    est_tuition_fee = st.number_input("Annual Tuition Fee per Student (\u20b9)", value=125000, step=5000)

# ---------------------------------------------------------
# 4. DATA INGESTION & SANITATION ENGINE (CACHED)
# ---------------------------------------------------------
@st.cache_data(show_spinner=False)
def execute_pipeline(df_raw, att_thresh, z_thresh):
    df = normalize_columns(df_raw)
    
    required_keys = {'student_id', 'subject_id', 'attendance_percentage', 'marks_obtained'}
    missing = required_keys - set(df.columns)
    if missing:
        return None, None, None, None, list(missing)

    if 'maximum_marks' not in df.columns: df['maximum_marks'] = 100.0
    if 'student_name' not in df.columns: df['student_name'] = df['student_id']
    if 'academic_semester' not in df.columns: df['academic_semester'] = "CURRENT_SEM"

    clean_rows, audit_entries = [], []
    
    for idx, row in df.iterrows():
        r_num = idx + 2
        s_id = str(row.get('student_id', '')).strip()
        sub_id = str(row.get('subject_id', '')).strip()
        s_name = str(row.get('student_name', s_id)).strip()
        sem = str(row.get('academic_semester', 'CURRENT_SEM')).strip()
        
        reasons = []
        if not s_id or s_id == 'nan': reasons.append("Missing Student ID")
        if not sub_id or sub_id == 'nan': reasons.append("Missing Subject ID")
            
        try:
            att = float(row.get('attendance_percentage', -1))
            marks = float(row.get('marks_obtained', -1))
            max_m = float(row.get('maximum_marks', 100.0))
            
            if att < 0.0 or att > 100.0: reasons.append(f"Invalid Attendance [{att}%]")
            if marks < 0.0 or marks > max_m: reasons.append(f"Invalid Score [{marks}/{max_m}]")
                
            if not reasons:
                clean_rows.append({
                    "student_id": s_id, "student_name": s_name, "subject_id": sub_id,
                    "academic_semester": sem, "attendance_percentage": att,
                    "marks_obtained": marks, "maximum_marks": max_m,
                    "normalized_mark_pct": (marks / max_m) * 100.0
                })
        except ValueError:
            reasons.append("Non-numeric Data Type Error")
            
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

    # Subject Level Statistics & Normalization Basis
    subject_summary = clean_df.groupby('subject_id').agg(
        subject_mean=('normalized_mark_pct', 'mean'),
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
    
    clean_df = clean_df.merge(subject_summary[['subject_id', 'subject_mean', 'subject_std']], on='subject_id', how='left')
    clean_df['z_score'] = (clean_df['normalized_mark_pct'] - clean_df['subject_mean']) / clean_df['subject_std']

    # Student Level Matrix
    student_matrix = clean_df.groupby(['student_id', 'student_name']).agg(
        mean_attendance=('attendance_percentage', 'mean'),
        overall_mean_pct=('normalized_mark_pct', 'mean'),
        avg_z_score=('z_score', 'mean'),
        subjects_count=('subject_id', 'nunique')
    ).reset_index()

    student_matrix['Academic Health Index (AHI)'] = (
        (student_matrix['overall_mean_pct'] * 0.60) + (student_matrix['mean_attendance'] * 0.40)
    ).round(2)

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
# 5. INGESTION INTERFACE
# ---------------------------------------------------------
st.markdown("<div class='section-label'>1. Ingestion Console & Data Contract Validation</div>", unsafe_allow_html=True)

col_ingest, col_template = st.columns([3, 1])
with col_ingest:
    uploaded_file = st.file_uploader("Upload Academic Dataset (.csv or .xlsx)", type=["csv", "xlsx"])

with col_template:
    st.markdown("**Contract Schema**")
    template_data = pd.DataFrame({
        "student_id": ["STU_101"], "student_name": ["Alice Smith"],
        "subject_id": ["CS101"], "attendance_percentage": [85.0],
        "marks_obtained": [78.0], "maximum_marks": [100.0], "academic_semester": ["SEM_05"]
    })
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine='openpyxl') as writer:
        template_data.to_excel(writer, index=False, sheet_name='Data_Contract')
    st.download_button("Download Contract Schema (.xlsx)", data=buf.getvalue(), file_name="academic_schema_contract.xlsx", use_container_width=True)

clean_df, audit_df, subject_summary, student_matrix = None, None, None, None

if uploaded_file is not None:
    raw_df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
    clean_df, audit_df, subject_summary, student_matrix, missing = execute_pipeline(raw_df, att_threshold, z_risk_threshold)
    
    if missing:
        st.error(f"Data Contract Violation: Missing required fields {missing}")
        st.stop()
        
    total_received = len(raw_df)
    clean_count = len(clean_df) if clean_df is not None else 0
    flagged_count = len(audit_df)
    health_score = round((clean_count / total_received) * 100, 2) if total_received > 0 else 0.0

    k1, k2, k3, k4 = st.columns(4)
    k1.markdown(f"""<div class="kpi-tile"><div class="kpi-title">Records Ingested</div><div class="kpi-value">{total_received}</div><div class="kpi-meta sub-info">Raw Data Stream</div></div>""", unsafe_allow_html=True)
    k2.markdown(f"""<div class="kpi-tile"><div class="kpi-title">Clean Records</div><div class="kpi-value">{clean_count}</div><div class="kpi-meta sub-good">Persisted to Pipeline</div></div>""", unsafe_allow_html=True)
    k3.markdown(f"""<div class="kpi-tile"><div class="kpi-title">Anomalies Isolated</div><div class="kpi-value">{flagged_count}</div><div class="kpi-meta sub-bad">Audit Logged</div></div>""", unsafe_allow_html=True)
    k4.markdown(f"""<div class="kpi-tile"><div class="kpi-title">Data Health Score</div><div class="kpi-value">{health_score}%</div><div class="kpi-meta {"sub-good" if health_score>=90 else "sub-bad"}">{"NAAC/NBA Compliant" if health_score>=90 else "Action Required"}</div></div>""", unsafe_allow_html=True)
    
    if not audit_df.empty:
        with st.expander("View Isolated Anomaly Audit Log", expanded=False):
            st.dataframe(audit_df, use_container_width=True)

# ---------------------------------------------------------
# 6. DECISION INTELLIGENCE HUB
# ---------------------------------------------------------
st.markdown("<div class='section-label'>2. Decision Intelligence & Analytics Hub</div>", unsafe_allow_html=True)

tab_class, tab_subject, tab_student, tab_matrix = st.tabs([
    "Class Performance & Sensitivity Analysis",
    "Subject Normalization & OBE Attainment",
    "Individual Student Scorecard & Merit Profile",
    "2D Risk Matrix & Financial Retention Planner"
])

empty_state_html = """
<div class="empty-state">
    <div class="empty-state-title">Awaiting Ingestion Stream</div>
    <div class="empty-state-sub">Upload an academic dataset in Section 1 to compute statistics, standardizations, and risk models.</div>
</div>
"""

# TAB 1: CLASS PERFORMANCE & SENSITIVITY
with tab_class:
    if clean_df is not None and not clean_df.empty:
        batch_avg_mark = clean_df['normalized_mark_pct'].mean()
        batch_avg_att = clean_df['attendance_percentage'].mean()
        batch_ahi = student_matrix['Academic Health Index (AHI)'].mean()
        pass_rate = ((student_matrix['overall_mean_pct'] >= 50.0).sum() / len(student_matrix)) * 100.0
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Class Average Score", f"{batch_avg_mark:.2f}%")
        c2.metric("Class Average Attendance", f"{batch_avg_att:.1f}%")
        c3.metric("Cohort Health Index", f"{batch_ahi:.1f} / 100")
        c4.metric("Class Pass Rate (\u2265 50%)", f"{pass_rate:.1f}%")

        x = clean_df['attendance_percentage'].values
        y = clean_df['normalized_mark_pct'].values
        r_val = clean_df['attendance_percentage'].corr(clean_df['normalized_mark_pct'], method='pearson')
        
        if len(clean_df) > 1 and np.std(x) > 0:
            slope, intercept = np.polyfit(x, y, 1)
            y_pred = slope * x + intercept
            ss_tot = np.sum((y - np.mean(y))**2)
            ss_res = np.sum((y - y_pred)**2)
            r_squared = 1.0 - (ss_res / ss_tot) if ss_tot > 0 else 0.0
        else:
            slope, intercept, r_squared = 0.0, 0.0, 0.0

        col_c1, col_c2 = st.columns([2, 1])
        with col_c1:
            fig_scatter = px.scatter(
                clean_df, x="attendance_percentage", y="normalized_mark_pct", color="subject_id",
                hover_data=["student_id", "student_name"],
                title=f"Attendance vs Score Scatter Plot & OLS Baseline (y = {slope:.2f}x + {intercept:.2f})",
                labels={"attendance_percentage": "Attendance (%)", "normalized_mark_pct": "Score (%)"},
                height=400
            )
            fig_scatter.update_layout(**PLOTLY_CONFIG)
            if len(clean_df) > 1 and np.std(x) > 0:
                x_range = np.linspace(x.min(), x.max(), 100)
                fig_scatter.add_trace(go.Scatter(x=x_range, y=slope * x_range + intercept, mode='lines', name=f'OLS Line (R²={r_squared:.2f})', line=dict(color='#E11D48', dash='dash', width=2)))
            st.plotly_chart(fig_scatter, use_container_width=True)
            
        with col_c2:
            st.metric("Pearson Correlation ($r$)", f"{r_val:+.4f}")
            st.metric("Regression Slope ($m$)", f"{slope:+.4f} marks / % att")
            st.metric("Explanatory Power ($R^2$)", f"{r_squared:.4f}")
            
            fig_pie = px.pie(
                student_matrix['Risk Quadrant'].value_counts().reset_index(), 
                values='count', names='Risk Quadrant', title="Cohort Risk Segmentation",
                color='Risk Quadrant',
                color_discrete_map={"CRITICAL RISK (Q1)": "#E11D48", "ATTENDANCE RISK (Q2)": "#D97706", "ACADEMIC RISK (Q3)": "#0284C7", "HIGH PERFORMER (Q4)": "#059669"},
                height=250
            )
            fig_pie.update_layout(**PLOTLY_CONFIG)
            st.plotly_chart(fig_pie, use_container_width=True)

        st.markdown(f"""
        <div class="insight-banner">
            <strong>Institutional Decision Insight:</strong><br>
            • <strong>Attendance Sensitivity Rating (Pearson r = {r_val:+.4f}):</strong> {"High positive relationship — lecture attendance directly impacts student exam performance." if r_val > 0.6 else "Moderate relationship — marks are partially independent of classroom presence." if r_val > 0.3 else "Low correlation — attendance has minimal impact on marks; review pedagogy alignment."}<br>
            • <strong>Yield Per Lecture (Slope m = {slope:+.2f}):</strong> Every 10% increase in attendance yields an expected <strong>+{slope*10:.1f} mark increase</strong> in final performance.<br>
            • <strong>Explanatory Power (R² = {r_squared:.2f}):</strong> Exactly {r_squared*100:.1f}% of overall score variance is driven by attendance alone.
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(empty_state_html, unsafe_allow_html=True)

# TAB 2: SUBJECT NORMALIZATION & OBE
with tab_subject:
    if clean_df is not None and not clean_df.empty:
        st.dataframe(
            subject_summary[['subject_id', 'student_count', 'subject_mean', 'subject_std', 'Subject Difficulty Index (SDI)', 'Pass Rate (%)', 'OBE Target Attainment']].style.format({
                "subject_mean": "{:.2f}%", "subject_std": "{:.2f}",
                "Subject Difficulty Index (SDI)": "{:.2f}", "Pass Rate (%)": "{:.1f}%"
            }),
            use_container_width=True
        )
        
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            fig_box = px.box(
                clean_df, x="subject_id", y="z_score", color="subject_id", points="all",
                title="Subject Z-Score Variance (Normalized Score Distribution)",
                labels={"subject_id": "Subject Code", "z_score": "Standard Deviations (\u03c3)"},
                height=400
            )
            fig_box.add_hline(y=0, line_dash="dash", line_color="gray", annotation_text="Mean Baseline (Z = 0)")
            fig_box.update_layout(**PLOTLY_CONFIG)
            st.plotly_chart(fig_box, use_container_width=True)
            
        with col_s2:
            fig_sdi = px.bar(
                subject_summary, x="subject_id", y="Subject Difficulty Index (SDI)", color="OBE Target Attainment",
                title="Subject Difficulty Index (SDI = 100 - Mean)",
                color_discrete_map={"Level 3 (High)": "#059669", "Level 2 (Moderate)": "#0284C7", "Level 1 (Low)": "#D97706", "Level 0 (Unattained)": "#E11D48"},
                height=400
            )
            fig_sdi.update_layout(**PLOTLY_CONFIG)
            st.plotly_chart(fig_sdi, use_container_width=True)

        hardest = subject_summary.sort_values('Subject Difficulty Index (SDI)', ascending=False).iloc[0]
        st.markdown(f"""
        <div class="insight-banner">
            <strong>Course Difficulty & Accreditation Insights:</strong><br>
            • <strong>Highest Difficulty Course:</strong> <code>{hardest['subject_id']}</code> (SDI = {hardest['Subject Difficulty Index (SDI)']:.1f}, Mean = {hardest['subject_mean']:.1f}%).<br>
            • <strong>Accreditation Trigger:</strong> Allocate additional Teaching Assistants (TAs) or remedial tutorial slots to <code>{hardest['subject_id']}</code> to protect NBA/NAAC attainment target metrics.<br>
            • <strong>Z-Score Normalization:</strong> Standardizes raw marks into Z-scores ($Z = \\frac{{X - \\mu}}{{\\sigma}}$) so students taking strict-grading courses are evaluated fairly against peer variance.
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(empty_state_html, unsafe_allow_html=True)

# TAB 3: STUDENT SCORECARD & MERIT PROFILE
with tab_student:
    if clean_df is not None and not clean_df.empty:
        selected_student = st.selectbox(
            "Search Student ID or Name:",
            options=student_matrix['student_id'].unique(),
            format_func=lambda x: f"{x} — {student_matrix[student_matrix['student_id']==x]['student_name'].values[0]}"
        )
        
        if selected_student:
            st_info = student_matrix[student_matrix['student_id'] == selected_student].iloc[0]
            st_records = clean_df[clean_df['student_id'] == selected_student]
            
            s1, s2, s3, s4 = st.columns(4)
            s1.metric("Student Name", st_info['student_name'])
            s2.metric("Mean Attendance", f"{st_info['mean_attendance']:.1f}%")
            s3.metric("Overall Average Score", f"{st_info['overall_mean_pct']:.2f}%")
            s4.metric("Average Z-Score Deviation", f"{st_info['avg_z_score']:+.2f} \u03c3")
            
            st.markdown(f"**Current Status:** `{st_info['Risk Quadrant']}` | **Academic Health Index (AHI):** `{st_info['Academic Health Index (AHI)']} / 100`")
            
            col_tbl, col_radar = st.columns([3, 2])
            with col_tbl:
                st.dataframe(
                    st_records[['subject_id', 'attendance_percentage', 'marks_obtained', 'maximum_marks', 'normalized_mark_pct', 'subject_mean', 'z_score']].style.format({
                        "attendance_percentage": "{:.1f}%", "marks_obtained": "{:.1f}", "maximum_marks": "{:.1f}",
                        "normalized_mark_pct": "{:.2f}%", "subject_mean": "{:.2f}%", "z_score": "{:+.2f} \u03c3"
                    }),
                    use_container_width=True
                )
            with col_radar:
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
                fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), height=320, margin=dict(l=40, r=40, t=20, b=20))
                st.plotly_chart(fig_radar, use_container_width=True)
    else:
        st.markdown(empty_state_html, unsafe_allow_html=True)

# TAB 4: 2D RISK MATRIX & FINANCIAL RETENTION
with tab_matrix:
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
        q2_count = (student_matrix['Risk Quadrant'] == "ATTENDANCE RISK (Q2)").sum()
        q3_count = (student_matrix['Risk Quadrant'] == "ACADEMIC RISK (Q3)").sum()
        revenue_at_risk = q1_count * est_tuition_fee

        st.markdown("**Institutional Resource & Financial Impact Allocation**")
        r1, r2, r3, r4 = st.columns(4)
        r1.metric("Mandatory Counseling Slots Required", f"{q1_count} Sessions", delta=f"{q1_count} Students", delta_color="inverse")
        r2.metric("Attendance Warning Letters Required", f"{q2_count} Letters", delta=f"{q2_count} Students", delta_color="inverse")
        r3.metric("Remedial Peer Tutors Required", f"{q3_count} Tutors", delta=f"{q3_count} Students", delta_color="off")
        r4.metric("Tuition Revenue At-Risk (Q1 Attrition)", f"\u20b9{revenue_at_risk:,.0f}", delta=f"{q1_count} Attrition Risk", delta_color="inverse")

        st.dataframe(
            student_matrix[['student_id', 'student_name', 'mean_attendance', 'overall_mean_pct', 'avg_z_score', 'Academic Health Index (AHI)', 'Risk Quadrant', 'Recommended Action']].style.format({
                "mean_attendance": "{:.1f}%", "overall_mean_pct": "{:.2f}%",
                "avg_z_score": "{:+.2f} \u03c3", "Academic Health Index (AHI)": "{:.1f}"
            }),
            use_container_width=True
        )
        
        action_csv = student_matrix.to_csv(index=False).encode('utf-8')
        st.download_button("Export Institutional Action Strategy (.csv)", data=action_csv, file_name=f"action_matrix_{datetime.now().strftime('%Y%m%d')}.csv", use_container_width=True)
    else:
        st.markdown(empty_state_html, unsafe_allow_html=True)
