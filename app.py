import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import io
from datetime import datetime

# ---------------------------------------------------------
# GLOBAL ENTERPRISE HIGH-DENSITY DASHBOARD STYLING
# ---------------------------------------------------------
st.set_page_config(
    page_title="BIT Academic Decision Intelligence Platform",
    page_icon="https://img.icons8.com/ios-filled/50/4f46e5/analytics.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS Override Engine (Eliminates Whitespace & Enforces SaaS Density)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    /* Remove Default Streamlit Whitespace Padding */
    .main .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
        padding-left: 1.25rem !important;
        padding-right: 1.25rem !important;
        max-width: 100% !important;
    }
    
    [data-testid="stVerticalBlock"] {
        gap: 0.5rem !important;
    }
    
    /* Global Typography */
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Global SaaS Top Control Bar */
    .top-navbar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: #0F172A;
        color: #FFFFFF;
        padding: 10px 16px;
        border-radius: 6px;
        margin-bottom: 10px;
        border-left: 4px solid #4F46E5;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .top-navbar .brand-title {
        font-size: 15px;
        font-weight: 800;
        letter-spacing: -0.01em;
        color: #F8FAFC;
    }
    .top-navbar .brand-sub {
        font-size: 11px;
        color: #94A3B8;
        font-weight: 400;
    }
    .top-navbar .status-tag {
        background: #1E293B;
        border: 1px solid #334155;
        color: #38BDF8;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 10px;
        font-weight: 700;
        text-transform: uppercase;
    }

    /* Dense KPI Tile Layout */
    .kpi-tile {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 6px;
        padding: 10px 14px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.02);
    }
    .kpi-title {
        font-size: 10px;
        font-weight: 700;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .kpi-value {
        font-size: 20px;
        font-weight: 800;
        color: #0F172A;
        line-height: 1.2;
        margin-top: 2px;
    }
    .kpi-meta {
        font-size: 10px;
        font-weight: 600;
        margin-top: 3px;
    }
    .sub-good { color: #059669; }
    .sub-bad { color: #E11D48; }
    .sub-info { color: #0284C7; }

    /* High-Density Tab Design */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px !important;
        border-bottom: 1px solid #CBD5E1 !important;
        background: #F8FAFC;
        padding: 3px 4px 0px 4px;
        border-radius: 6px 6px 0 0;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 6px 14px !important;
        border-radius: 4px 4px 0 0 !important;
        font-size: 12px !important;
        font-weight: 600 !important;
        color: #64748B !important;
    }
    .stTabs [aria-selected="true"] {
        background: #FFFFFF !important;
        color: #4F46E5 !important;
        border-top: 2px solid #4F46E5 !important;
        box-shadow: 0 -1px 2px rgba(0,0,0,0.03);
    }

    /* Compact Insight Banners */
    .insight-banner {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-left: 3px solid #4F46E5;
        padding: 8px 12px;
        border-radius: 4px;
        font-size: 11.5px;
        color: #334155;
        line-height: 1.5;
        margin-top: 6px;
        margin-bottom: 6px;
    }
    
    .section-label {
        font-size: 12px;
        font-weight: 700;
        color: #0F172A;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        margin-top: 4px;
        margin-bottom: 4px;
    }
</style>
""", unsafe_allow_html=True)

# Top Bar Header
st.markdown("""
<div class="top-navbar">
    <div>
        <span class="brand-title">ACADEMIC DECISION INTELLIGENCE PLATFORM</span>
        <span class="brand-sub"> &nbsp;|&nbsp; Bannari Amman Institute of Technology &nbsp;•&nbsp; Institutional Analytics & Outcome Attainment</span>
    </div>
    <div class="status-tag">PIPELINE ACTIVE</div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# COMPACT PLOTLY THEME
# ---------------------------------------------------------
PLOTLY_CONFIG = dict(
    font=dict(family="Inter, sans-serif", color="#334155", size=11),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="#FFFFFF",
    margin=dict(l=35, r=15, t=30, b=30),
    xaxis=dict(showgrid=True, gridcolor="#F1F5F9", linecolor="#CBD5E1"),
    yaxis=dict(showgrid=True, gridcolor="#F1F5F9", linecolor="#CBD5E1")
)

# ---------------------------------------------------------
# SIDEBAR CONTROLS & CONTRACT ENGINE
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("<div class='section-label'>Pipeline Configuration</div>", unsafe_allow_html=True)
    
    st.markdown("**1. Data Contract Schema**")
    template_data = pd.DataFrame({
        "student_id": ["STU_101", "STU_102", "STU_103", "STU_104", "STU_105"],
        "student_name": ["Alice Smith", "Bob Jones", "Charlie Brown", "Diana Prince", "Evan Wright"],
        "subject_id": ["MATH101", "CS201", "MATH101", "CS201", "PHY102"],
        "attendance_percentage": [88.5, 64.0, 92.0, 55.0, 78.0],
        "marks_obtained": [82.0, 45.0, 95.0, 38.0, 68.0],
        "maximum_marks": [100.0, 100.0, 100.0, 100.0, 100.0],
        "academic_semester": ["SEM_07", "SEM_07", "SEM_07", "SEM_07", "SEM_07"]
    })
    
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine='openpyxl') as writer:
        template_data.to_excel(writer, index=False, sheet_name='Data_Contract')
    
    st.download_button(
        label="Download Schema Contract (.xlsx)",
        data=buf.getvalue(),
        file_name="academic_ingestion_template.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )
    
    st.markdown("---")
    st.markdown("**2. Policy Controls**")
    att_threshold = st.slider("Attendance Cutoff (%)", 50.0, 90.0, 75.0, 1.0)
    z_risk_threshold = st.slider("Critical Z-Score Cutoff (\u03c3)", -2.0, 0.0, -0.5, 0.1)
    est_tuition_fee = st.number_input("Annual Tuition Fee per Student (\u20b9)", value=125000, step=5000)

# ---------------------------------------------------------
# DYNAMIC SCHEMA MAPPING
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
# STAGE 1: INGESTION & PIPELINE SANITATION
# ---------------------------------------------------------
uploaded_file = st.file_uploader("Upload Academic Data (.csv or .xlsx)", type=["csv", "xlsx"])

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv'):
            raw_df = pd.read_csv(uploaded_file)
        else:
            raw_df = pd.read_excel(uploaded_file)
    except Exception as e:
        st.error(f"Ingestion Exception: {e}")
        st.stop()
        
    raw_df = normalize_columns(raw_df)
    
    required_keys = {'student_id', 'subject_id', 'attendance_percentage', 'marks_obtained'}
    missing = required_keys - set(raw_df.columns)
    
    if missing:
        st.error(f"Data Contract Violation: Could not resolve fields {list(missing)}.")
        st.stop()
        
    if 'maximum_marks' not in raw_df.columns:
        raw_df['maximum_marks'] = 100.0
    if 'student_name' not in raw_df.columns:
        raw_df['student_name'] = raw_df['student_id']
    if 'academic_semester' not in raw_df.columns:
        raw_df['academic_semester'] = "CURRENT_SEM"

    # Cleansing Engine
    clean_rows = []
    audit_entries = []
    
    for idx, row in raw_df.iterrows():
        r_num = idx + 2
        s_id = str(row.get('student_id', '')).strip()
        sub_id = str(row.get('subject_id', '')).strip()
        s_name = str(row.get('student_name', s_id)).strip()
        sem = str(row.get('academic_semester', 'CURRENT_SEM')).strip()
        
        reasons = []
        if not s_id or s_id == 'nan':
            reasons.append("Missing Student ID")
        if not sub_id or sub_id == 'nan':
            reasons.append("Missing Subject ID")
            
        try:
            att = float(row.get('attendance_percentage', -1))
            marks = float(row.get('marks_obtained', -1))
            max_m = float(row.get('maximum_marks', 100.0))
            
            if att < 0.0 or att > 100.0:
                reasons.append(f"Attendance out of range: {att}%")
            if marks < 0.0:
                reasons.append(f"Negative mark: {marks}")
            if marks > max_m:
                reasons.append(f"Marks ({marks}) > Maximum ({max_m})")
                
            if not reasons:
                pct_mark = (marks / max_m) * 100.0
                clean_rows.append({
                    "student_id": s_id,
                    "student_name": s_name,
                    "subject_id": sub_id,
                    "academic_semester": sem,
                    "attendance_percentage": att,
                    "marks_obtained": marks,
                    "maximum_marks": max_m,
                    "normalized_mark_pct": pct_mark
                })
        except ValueError:
            reasons.append("Non-numeric data in numeric field")
            
        if reasons:
            audit_entries.append({
                "Row Number": r_num,
                "Student ID": s_id,
                "Subject ID": sub_id,
                "Rejection Reason": " | ".join(reasons),
                "Raw Record Payload": str(row.to_dict())
            })

    clean_df = pd.DataFrame(clean_rows)
    audit_df = pd.DataFrame(audit_entries)
    
    if not clean_df.empty:
        before_dedup = len(clean_df)
        clean_df = clean_df.drop_duplicates(subset=['student_id', 'subject_id', 'academic_semester'], keep='first')
        dedup_count = before_dedup - len(clean_df)
        if dedup_count > 0:
            st.warning(f"Deduplication Engine: Removed {dedup_count} duplicate records.")

    total_received = len(raw_df)
    clean_count = len(clean_df)
    flagged_count = len(audit_df)
    health_score = round((clean_count / total_received) * 100, 2) if total_received > 0 else 0.0

    # ---------------------------------------------------------
    # STAGE 2: PIPELINE QUALITY AUDIT CONSOLE
    # ---------------------------------------------------------
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(f"""<div class="kpi-tile"><div class="kpi-title">Records Ingested</div><div class="kpi-value">{total_received}</div><div class="kpi-meta sub-info">Raw Stream Input</div></div>""", unsafe_allow_html=True)
    with k2:
        st.markdown(f"""<div class="kpi-tile"><div class="kpi-title">Clean Records</div><div class="kpi-value">{clean_count}</div><div class="kpi-meta sub-good">Persisted to Engine</div></div>""", unsafe_allow_html=True)
    with k3:
        st.markdown(f"""<div class="kpi-tile"><div class="kpi-title">Anomalies Isolated</div><div class="kpi-value">{flagged_count}</div><div class="kpi-meta sub-bad">Audit Logged</div></div>""", unsafe_allow_html=True)
    with k4:
        st.markdown(f"""<div class="kpi-tile"><div class="kpi-title">Data Health Score</div><div class="kpi-value">{health_score}%</div><div class="kpi-meta {"sub-good" if health_score>=90 else "sub-bad"}">{"NAAC/NBA Ready" if health_score>=90 else "Action Required"}</div></div>""", unsafe_allow_html=True)
    
    if not audit_df.empty:
        with st.expander("Isolated Anomaly Audit Log", expanded=False):
            st.dataframe(audit_df[['Row Number', 'Student ID', 'Subject ID', 'Rejection Reason']], use_container_width=True)
            audit_csv = audit_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Export Audit Log (.csv)",
                data=audit_csv,
                file_name=f"audit_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )

    if clean_df.empty:
        st.error("No clean records survived sanitation. Check the audit log and re-upload.")
        st.stop()

    # Calculate Subject Metrics & Z-Scores
    subject_summary = clean_df.groupby('subject_id').agg(
        subject_mean=('normalized_mark_pct', 'mean'),
        subject_std=('normalized_mark_pct', 'std'),
        avg_attendance=('attendance_percentage', 'mean'),
        student_count=('student_id', 'nunique'),
        pass_count=('normalized_mark_pct', lambda x: (x >= 50.0).sum())
    ).reset_index()
    
    subject_summary['subject_std'] = subject_summary['subject_std'].fillna(0.0)
    subject_summary['Subject Difficulty Index (SDI)'] = (100.0 - subject_summary['subject_mean']).round(2)
    subject_summary['Pass Rate (%)'] = ((subject_summary['pass_count'] / subject_summary['student_count']) * 100.0).round(1)
    
    def get_obe_level(pass_rate):
        if pass_rate >= 70.0:
            return "Level 3 (High)"
        elif pass_rate >= 60.0:
            return "Level 2 (Moderate)"
        elif pass_rate >= 50.0:
            return "Level 1 (Low)"
        return "Level 0 (Unattained)"

    subject_summary['OBE Target Attainment'] = subject_summary['Pass Rate (%)'].apply(get_obe_level)
    
    clean_df = clean_df.merge(subject_summary[['subject_id', 'subject_mean', 'subject_std']], on='subject_id', how='left')
    clean_df['z_score'] = np.where(
        clean_df['subject_std'] > 0,
        (clean_df['normalized_mark_pct'] - clean_df['subject_mean']) / clean_df['subject_std'],
        0.0
    )

    # Student Summary
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
        att_low = row['mean_attendance'] < att_threshold
        z_low = row['avg_z_score'] < z_risk_threshold
        if att_low and z_low:
            return "CRITICAL RISK (Q1)"
        elif att_low and not z_low:
            return "ATTENDANCE RISK (Q2)"
        elif not att_low and z_low:
            return "ACADEMIC RISK (Q3)"
        return "HIGH PERFORMER (Q4)"

    student_matrix['Risk Quadrant'] = student_matrix.apply(classify_quadrant, axis=1)

    # ---------------------------------------------------------
    # STAGE 3: DECISION INTELLIGENCE HUB
    # ---------------------------------------------------------
    st.markdown("<div class='section-label'>Decision Analytics Hub</div>", unsafe_allow_html=True)

    tab_class, tab_subject, tab_student, tab_matrix = st.tabs([
        "Class Analytics & Sensitivity",
        "Course Variance & OBE Attainment",
        "Individual Student Scorecard",
        "At-Risk Intervention Matrix"
    ])

    # ---------------------------------------------------------
    # TAB 1: CLASS PERFORMANCE & CORRELATION
    # ---------------------------------------------------------
    with tab_class:
        batch_avg_mark = clean_df['normalized_mark_pct'].mean()
        batch_avg_att = clean_df['attendance_percentage'].mean()
        batch_ahi = student_matrix['Academic Health Index (AHI)'].mean()
        pass_count = (student_matrix['overall_mean_pct'] >= 50.0).sum()
        pass_rate = (pass_count / len(student_matrix)) * 100.0 if len(student_matrix) > 0 else 0.0
        
        c_col1, c_col2, c_col3, c_col4 = st.columns(4)
        c_col1.metric("Class Average Score", f"{batch_avg_mark:.2f}%")
        c_col2.metric("Class Average Attendance", f"{batch_avg_att:.1f}%")
        c_col3.metric("Cohort Health Index", f"{batch_ahi:.1f} / 100")
        c_col4.metric("Class Pass Rate (\u2265 50%)", f"{pass_rate:.1f}%")

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
            fig_class_scatter = px.scatter(
                clean_df,
                x="attendance_percentage",
                y="normalized_mark_pct",
                color="subject_id",
                hover_data=["student_id", "student_name"],
                title=f"Attendance vs Score Scatter Plot & Native OLS Baseline (y = {slope:.2f}x + {intercept:.2f})",
                labels={"attendance_percentage": "Attendance (%)", "normalized_mark_pct": "Score (%)"},
                color_discrete_sequence=["#4F46E5", "#0284C7", "#D97706", "#059669", "#7C3AED"],
                height=320
            )
            fig_class_scatter.update_layout(**PLOTLY_CONFIG)
            
            if len(clean_df) > 1 and np.std(x) > 0:
                x_range = np.linspace(x.min(), x.max(), 100)
                y_range = slope * x_range + intercept
                fig_class_scatter.add_trace(
                    go.Scatter(
                        x=x_range,
                        y=y_range,
                        mode='lines',
                        name=f'OLS Baseline (R²={r_squared:.2f})',
                        line=dict(color='#E11D48', dash='dash', width=2)
                    )
                )
            st.plotly_chart(fig_class_scatter, use_container_width=True)
            
        with col_c2:
            st.metric("Pearson Correlation ($r$)", f"{r_val:+.4f}")
            st.metric("Regression Slope ($m$)", f"{slope:+.4f} marks / % att")
            st.metric("Explanatory Power ($R^2$)", f"{r_squared:.4f}")
            
            risk_counts = student_matrix['Risk Quadrant'].value_counts().reset_index()
            fig_pie = px.pie(
                risk_counts, 
                values='count', 
                names='Risk Quadrant', 
                title="Cohort Risk Distribution",
                color='Risk Quadrant',
                color_discrete_map={
                    "CRITICAL RISK (Q1)": "#E11D48",
                    "ATTENDANCE RISK (Q2)": "#D97706",
                    "ACADEMIC RISK (Q3)": "#0284C7",
                    "HIGH PERFORMER (Q4)": "#059669"
                },
                height=220
            )
            fig_pie.update_layout(**PLOTLY_CONFIG)
            st.plotly_chart(fig_pie, use_container_width=True)

        st.markdown(f"""
        <div class="insight-banner">
            <strong>Institutional Decision Insight:</strong><br>
            • <strong>Attendance Sensitivity Rating (Pearson r = {r_val:+.4f}):</strong> {"High positive correlation — attendance directly drives exam performance." if r_val > 0.6 else "Moderate correlation — marks are partially independent of class presence." if r_val > 0.3 else "Low correlation — attendance has minimal linear impact on marks."}<br>
            • <strong>Grade Yield per Lecture (Slope m = {slope:+.2f}):</strong> Every 10% increase in attendance yields an expected <strong>+{slope*10:.1f} mark increase</strong> in final performance.<br>
            • <strong>Explanatory Power (R² = {r_squared:.2f}):</strong> Exactly {r_squared*100:.1f}% of overall score variance is explained by attendance alone.
        </div>
        """, unsafe_allow_html=True)

    # ---------------------------------------------------------
    # TAB 2: COURSE DIFFICULTY & OBE ATTAINMENT
    # ---------------------------------------------------------
    with tab_subject:
        st.dataframe(
            subject_summary[['subject_id', 'student_count', 'subject_mean', 'subject_std', 'Subject Difficulty Index (SDI)', 'Pass Rate (%)', 'OBE Target Attainment']].style.format({
                "subject_mean": "{:.2f}%",
                "subject_std": "{:.2f}",
                "Subject Difficulty Index (SDI)": "{:.2f}",
                "Pass Rate (%)": "{:.1f}%"
            }),
            use_container_width=True
        )
        
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            fig_subject_box = px.box(
                clean_df,
                x="subject_id",
                y="normalized_mark_pct",
                color="subject_id",
                points="all",
                title="Subject Grade Distribution (Evaluating Grading Strictness)",
                labels={"subject_id": "Subject Code", "normalized_mark_pct": "Score (%)"},
                color_discrete_sequence=["#4F46E5", "#0284C7", "#D97706", "#059669", "#7C3AED"],
                height=300
            )
            fig_subject_box.update_layout(**PLOTLY_CONFIG)
            st.plotly_chart(fig_subject_box, use_container_width=True)
            
        with col_s2:
            fig_sdi_bar = px.bar(
                subject_summary,
                x="subject_id",
                y="Subject Difficulty Index (SDI)",
                color="OBE Target Attainment",
                title="Subject Difficulty Index (SDI = 100 - Mean)",
                labels={"subject_id": "Subject Code", "Subject Difficulty Index (SDI)": "Difficulty Rating"},
                color_discrete_map={
                    "Level 3 (High)": "#059669",
                    "Level 2 (Moderate)": "#0284C7",
                    "Level 1 (Low)": "#D97706",
                    "Level 0 (Unattained)": "#E11D48"
                },
                height=300
            )
            fig_sdi_bar.update_layout(**PLOTLY_CONFIG)
            st.plotly_chart(fig_sdi_bar, use_container_width=True)

        hardest_sub = subject_summary.sort_values('Subject Difficulty Index (SDI)', ascending=False).iloc[0]
        st.markdown(f"""
        <div class="insight-banner">
            <strong>Course Difficulty & Accreditation Insights:</strong><br>
            • <strong>Highest Difficulty Course:</strong> <code>{hardest_sub['subject_id']}</code> (SDI = {hardest_sub['Subject Difficulty Index (SDI)']:.1f}, Mean = {hardest_sub['subject_mean']:.1f}%).<br>
            • <strong>Accreditation Trigger:</strong> Allocate additional Teaching Assistants (TAs) or remedial tutorial slots to <code>{hardest_sub['subject_id']}</code> to protect NBA/NAAC attainment target metrics.<br>
            • <strong>Z-Score Normalization:</strong> Converts raw scores into Z-scores ($Z = \\frac{{X - \\mu}}{{\\sigma}}$) to evaluate students fairly relative to peer variance, removing grading bias.
        </div>
        """, unsafe_allow_html=True)

    # ---------------------------------------------------------
    # TAB 3: INDIVIDUAL STUDENT PROFILE
    # ---------------------------------------------------------
    with tab_student:
        selected_student = st.selectbox(
            "Search Student ID or Name:",
            options=student_matrix['student_id'].unique(),
            format_func=lambda x: f"{x} — {student_matrix[student_matrix['student_id']==x]['student_name'].values[0]}"
        )
        
        if selected_student:
            st_info = student_matrix[student_matrix['student_id'] == selected_student].iloc[0]
            st_records = clean_df[clean_df['student_id'] == selected_student]
            
            s_col1, s_col2, s_col3, s_col4 = st.columns(4)
            s_col1.metric("Student Name", st_info['student_name'])
            s_col2.metric("Mean Attendance", f"{st_info['mean_attendance']:.1f}%")
            s_col3.metric("Overall Average Score", f"{st_info['overall_mean_pct']:.2f}%")
            s_col4.metric("Average Z-Score", f"{st_info['avg_z_score']:+.2f} \u03c3")
            
            st.markdown(f"**Current Risk Status:** `{st_info['Risk Quadrant']}` | **Academic Health Index (AHI):** `{st_info['Academic Health Index (AHI)']} / 100`")
            
            st.dataframe(
                st_records[['subject_id', 'attendance_percentage', 'marks_obtained', 'maximum_marks', 'normalized_mark_pct', 'subject_mean', 'z_score']].style.format({
                    "attendance_percentage": "{:.1f}%",
                    "marks_obtained": "{:.1f}",
                    "maximum_marks": "{:.1f}",
                    "normalized_mark_pct": "{:.2f}%",
                    "subject_mean": "{:.2f}%",
                    "z_score": "{:+.2f} \u03c3"
                }),
                use_container_width=True
            )
            
            fig_student_bar = go.Figure()
            fig_student_bar.add_trace(go.Bar(
                x=st_records['subject_id'],
                y=st_records['normalized_mark_pct'],
                name='Student Mark %',
                marker_color='#4F46E5'
            ))
            fig_student_bar.add_trace(go.Bar(
                x=st_records['subject_id'],
                y=st_records['subject_mean'],
                name='Subject Class Average %',
                marker_color='#94A3B8'
            ))
            fig_student_bar.update_layout(
                barmode='group',
                title=f"Performance Breakdown: {st_info['student_name']} vs. Subject Class Averages",
                xaxis_title="Subject Code",
                yaxis_title="Score (%)",
                height=280,
                **PLOTLY_CONFIG
            )
            st.plotly_chart(fig_student_bar, use_container_width=True)

    # ---------------------------------------------------------
    # TAB 4: AT-RISK MATRIX & INTERVENTION
    # ---------------------------------------------------------
    with tab_matrix:
        def get_action(quadrant):
            if quadrant == "CRITICAL RISK (Q1)":
                return "Schedule Mandatory Faculty Counseling & Notify Parents"
            elif quadrant == "ATTENDANCE RISK (Q2)":
                return "Issue Official Low Attendance Warning Letter"
            elif quadrant == "ACADEMIC RISK (Q3)":
                return "Assign Remedial Peer Tutor & Subject Workshops"
            return "Regular Monitoring & Honor Roll Recognition"

        student_matrix['Recommended Action'] = student_matrix['Risk Quadrant'].apply(get_action)
        
        fig_quad = px.scatter(
            student_matrix,
            x="mean_attendance",
            y="avg_z_score",
            color="Risk Quadrant",
            hover_data=["student_id", "student_name", "overall_mean_pct", "Academic Health Index (AHI)"],
            title="2D Cartesian Early Warning Risk Matrix (Attendance vs. Z-Score Deviation)",
            labels={"mean_attendance": "Mean Attendance (%)", "avg_z_score": "Average Z-Score (\u03c3)"},
            color_discrete_map={
                "CRITICAL RISK (Q1)": "#E11D48",
                "ATTENDANCE RISK (Q2)": "#D97706",
                "ACADEMIC RISK (Q3)": "#0284C7",
                "HIGH PERFORMER (Q4)": "#059669"
            },
            height=340
        )
        fig_quad.add_vline(x=att_threshold, line_dash="dash", line_color="#64748B", annotation_text=f"Attendance Cutoff ({att_threshold}%)")
        fig_quad.add_hline(y=z_risk_threshold, line_dash="dash", line_color="#64748B", annotation_text=f"Z-Score Cutoff ({z_risk_threshold}\u03c3)")
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
                "mean_attendance": "{:.1f}%",
                "overall_mean_pct": "{:.2f}%",
                "avg_z_score": "{:+.2f} \u03c3",
                "Academic Health Index (AHI)": "{:.1f}"
            }),
            use_container_width=True
        )
        
        action_csv = student_matrix.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Export Institutional Action Matrix (.csv)",
            data=action_csv,
            file_name=f"at_risk_action_matrix_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )

else:
    st.info("Upload an academic batch data file (.csv or .xlsx) using the file uploader above to trigger the analytics pipeline.")
