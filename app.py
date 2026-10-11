import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import io
from datetime import datetime

# ---------------------------------------------------------
# 1. PAGE & HIGH-DENSITY ENTERPRISE STYLING
# ---------------------------------------------------------
st.set_page_config(
    page_title="Academic Intelligence & Assistant Platform",
    page_icon="https://img.icons8.com/ios-filled/50/4f46e5/analytics.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] { font-family: 'Inter', -apple-system, sans-serif; }
    
    .block-container {
        padding-top: 1.25rem !important;
        padding-bottom: 1.5rem !important;
        padding-left: 1.5rem !important;
        padding-right: 1.5rem !important;
        max-width: 100% !important;
    }
    
    [data-testid="stVerticalBlock"] { gap: 0.75rem !important; }

    /* Top Enterprise Control Bar */
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
    .top-navbar .brand-title { font-size: 16px; font-weight: 800; color: #F8FAFC; }
    .top-navbar .brand-sub { font-size: 12px; color: #94A3B8; }
    .top-navbar .status-tag {
        background: #1E293B; border: 1px solid #334155; color: #38BDF8;
        padding: 4px 10px; border-radius: 4px; font-size: 11px; font-weight: 700;
    }

    /* KPI Cards */
    .kpi-tile {
        background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 6px;
        padding: 12px 16px; box-shadow: 0 1px 2px rgba(0,0,0,0.02);
    }
    .kpi-title { font-size: 11px; font-weight: 700; color: #64748B; text-transform: uppercase; letter-spacing: 0.05em; }
    .kpi-value { font-size: 22px; font-weight: 800; color: #0F172A; margin-top: 2px; }
    .kpi-meta { font-size: 11px; font-weight: 600; margin-top: 4px; }
    .sub-good { color: #059669; } .sub-bad { color: #E11D48; } .sub-info { color: #0284C7; }

    /* Student Profile Cards */
    .student-card {
        background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px;
        padding: 14px; margin-bottom: 10px; box-shadow: 0 1px 2px rgba(0,0,0,0.02);
    }
    .student-card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
    .student-name { font-size: 14px; font-weight: 700; color: #0F172A; }
    .student-id { font-size: 11px; color: #64748B; font-weight: 600; }
    
    .badge { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 10px; font-weight: 700; text-transform: uppercase; }
    .badge-critical { background: #FFE4E6; color: #E11D48; }
    .badge-warning { background: #FEF3C7; color: #D97706; }
    .badge-academic { background: #E0F2FE; color: #0369A1; }
    .badge-success { background: #D1FAE5; color: #059669; }

    .insight-banner {
        background-color: #F8FAFC; border: 1px solid #E2E8F0; border-left: 4px solid #4F46E5;
        padding: 12px 16px; border-radius: 6px; font-size: 12.5px; color: #334155; line-height: 1.6;
    }

    .section-label { font-size: 13px; font-weight: 700; color: #0F172A; text-transform: uppercase; letter-spacing: 0.04em; margin: 8px 0; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="top-navbar">
    <div>
        <span class="brand-title">ACADEMIC INTELLIGENCE PLATFORM</span>
        <span class="brand-sub"> &nbsp;|&nbsp; AI Query Assistant, Student Directory & Institutional Analytics</span>
    </div>
    <div class="status-tag">SYSTEM ACTIVE</div>
</div>
""", unsafe_allow_html=True)

PLOTLY_CONFIG = dict(
    font=dict(family="Inter, sans-serif", color="#334155", size=12),
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#FFFFFF",
    margin=dict(l=40, r=20, t=40, b=40),
    xaxis=dict(showgrid=True, gridcolor="#F1F5F9", linecolor="#CBD5E1"),
    yaxis=dict(showgrid=True, gridcolor="#F1F5F9", linecolor="#CBD5E1")
)

# ---------------------------------------------------------
# 2. SCHEMA NORMALIZATION
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
# 3. NAVIGATION & POLICY CONTROLS
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("<div class='section-label'>Navigation & Policy</div>", unsafe_allow_html=True)
    view_mode = st.radio(
        "Select Active View Mode:",
        ["1. Executive Control & AI Assistant", "2. Student Profile Directory", "3. Institutional Risk Governance"]
    )
    st.markdown("---")
    st.markdown("<div class='section-label'>Policy Cutoffs</div>", unsafe_allow_html=True)
    att_threshold = st.slider("Attendance Cutoff (%)", 50.0, 90.0, 75.0, 1.0)
    z_risk_threshold = st.slider("Critical Z-Score Cutoff (\u03c3)", -2.0, 0.0, -0.5, 0.1)
    est_tuition_fee = st.number_input("Annual Tuition Fee (\u20b9)", value=125000, step=5000)

# ---------------------------------------------------------
# 4. DATA PROCESSING PIPELINE (CACHED)
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
            if marks < 0.0 or marks > max_m: reasons.append(f"Invalid Marks [{marks}/{max_m}]")
                
            if not reasons:
                clean_rows.append({
                    "student_id": s_id, "student_name": s_name, "subject_id": sub_id,
                    "academic_semester": sem, "attendance_percentage": att,
                    "marks_obtained": marks, "maximum_marks": max_m,
                    "normalized_mark_pct": (marks / max_m) * 100.0
                })
        except ValueError:
            reasons.append("Non-numeric Data Type")
            
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
# 5. INGESTION TOP SECTION
# ---------------------------------------------------------
col_ingest, col_template = st.columns([3, 1])
with col_ingest:
    uploaded_file = st.file_uploader("Upload Academic Data Dataset (.csv or .xlsx)", type=["csv", "xlsx"])

with col_template:
    template_data = pd.DataFrame({
        "student_id": ["STU_101"], "student_name": ["Alice Smith"],
        "subject_id": ["CS101"], "attendance_percentage": [85.0],
        "marks_obtained": [78.0], "maximum_marks": [100.0], "academic_semester": ["SEM_05"]
    })
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine='openpyxl') as writer:
        template_data.to_excel(writer, index=False, sheet_name='Data_Contract')
    st.download_button("Download Schema Contract (.xlsx)", data=buf.getvalue(), file_name="academic_schema_contract.xlsx", use_container_width=True)

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
    k2.markdown(f"""<div class="kpi-tile"><div class="kpi-title">Clean Records</div><div class="kpi-value">{clean_count}</div><div class="kpi-meta sub-good">Persisted to Engine</div></div>""", unsafe_allow_html=True)
    k3.markdown(f"""<div class="kpi-tile"><div class="kpi-title">Anomalies Isolated</div><div class="kpi-value">{flagged_count}</div><div class="kpi-meta sub-bad">Audit Logged</div></div>""", unsafe_allow_html=True)
    k4.markdown(f"""<div class="kpi-tile"><div class="kpi-title">Data Health Score</div><div class="kpi-value">{health_score}%</div><div class="kpi-meta {"sub-good" if health_score>=90 else "sub-bad"}">{"NAAC/NBA Compliant" if health_score>=90 else "Action Required"}</div></div>""", unsafe_allow_html=True)
    
    if not audit_df.empty:
        with st.expander("View Isolated Anomaly Audit Log", expanded=False):
            st.dataframe(audit_df, use_container_width=True)

# ---------------------------------------------------------
# VIEW MODE 1: EXECUTIVE CONTROL & AI ASSISTANT CHATBOT
# ---------------------------------------------------------
if view_mode == "1. Executive Control & AI Assistant":
    st.markdown("<div class='section-label'>Executive Overview & Automated AI Assistant</div>", unsafe_allow_html=True)
    
    if clean_df is not None and not clean_df.empty:
        col_chat, col_viz = st.columns([1, 1])
        
        # LOCAL AI QUERY ASSISTANT CHATBOT ENGINE
        with col_chat:
            st.markdown("##### 💬 AI Academic Query Assistant")
            st.caption("Ask questions about student attendance, risk levels, subject difficulty, or top performers in plain English.")
            
            if "messages" not in st.session_state:
                st.session_state.messages = [
                    {"role": "assistant", "content": f"Hello! I am your Academic Intelligence Assistant. The current batch contains **{len(student_matrix)} unique students** across **{clean_df['subject_id'].nunique()} subjects**. What would you like to query?"}
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
                        response = f"There are **{len(crit_df)} students** in Critical Risk (Q1):\n\n{names}\n\n*Action:* Scheduled for mandatory faculty counseling."
                    else:
                        response = "Great news! There are currently zero students flagged in Critical Risk (Q1)."
                        
                elif "top" in query_lower or "best" in query_lower or "performer" in query_lower or "high" in query_lower:
                    top_df = student_matrix.sort_values('overall_mean_pct', ascending=False).head(5)
                    top_list = "\n".join([f"1. **{row['student_name']}** ({row['student_id']}) — Score: {row['overall_mean_pct']:.1f}%, Att: {row['mean_attendance']:.1f}%" for _, row in top_df.iterrows()])
                    response = f"Here are the top 5 students by overall score:\n\n{top_list}"
                    
                elif "hardest" in query_lower or "difficult" in query_lower or "subject" in query_lower:
                    hardest = subject_summary.sort_values('Subject Difficulty Index (SDI)', ascending=False).iloc[0]
                    response = f"The hardest subject is **{hardest['subject_id']}** with a Subject Difficulty Index (SDI) of **{hardest['Subject Difficulty Index (SDI)']:.1f}** and an average score of **{hardest['subject_mean']:.1f}%**."
                    
                elif "attendance" in query_lower or "low attendance" in query_lower:
                    low_att = student_matrix[student_matrix['mean_attendance'] < att_threshold]
                    response = f"There are **{len(low_att)} students** below the mandatory attendance cutoff of {att_threshold}%."
                    
                else:
                    batch_avg = clean_df['normalized_mark_pct'].mean()
                    batch_att = clean_df['attendance_percentage'].mean()
                    response = f"Batch Analysis Summary: Overall Average Score is **{batch_avg:.1f}%** and Average Attendance is **{batch_att:.1f}%**. You can ask me to list at-risk students, top performers, or subject metrics!"
                    
                st.session_state.messages.append({"role": "assistant", "content": response})
                st.chat_message("assistant").write(response)

        with col_viz:
            st.markdown("##### 📊 Cohort Performance Overview")
            x = clean_df['attendance_percentage'].values
            y = clean_df['normalized_mark_pct'].values
            r_val = clean_df['attendance_percentage'].corr(clean_df['normalized_mark_pct'], method='pearson')
            
            if len(clean_df) > 1 and np.std(x) > 0:
                slope, intercept = np.polyfit(x, y, 1)
            else: slope, intercept = 0.0, 0.0

            fig_scatter = px.scatter(
                clean_df, x="attendance_percentage", y="normalized_mark_pct", color="subject_id",
                title=f"Attendance vs Score (Pearson r = {r_val:+.2f})",
                labels={"attendance_percentage": "Attendance (%)", "normalized_mark_pct": "Score (%)"},
                height=350
            )
            if len(clean_df) > 1 and np.std(x) > 0:
                x_range = np.linspace(x.min(), x.max(), 100)
                fig_scatter.add_trace(go.Scatter(x=x_range, y=slope * x_range + intercept, mode='lines', name='OLS Baseline', line=dict(color='#E11D48', dash='dash')))
            fig_scatter.update_layout(**PLOTLY_CONFIG)
            st.plotly_chart(fig_scatter, use_container_width=True)

    else:
        st.info("Upload an academic dataset above to trigger the AI Assistant and Analytics Control Engine.")

# ---------------------------------------------------------
# VIEW MODE 2: TOTAL STUDENT COUNT PROFILES & DIRECTORY
# ---------------------------------------------------------
elif view_mode == "2. Student Profile Directory":
    st.markdown("<div class='section-label'>Total Student Profile Roster & Identity Directory</div>", unsafe_allow_html=True)
    
    if clean_df is not None and not clean_df.empty:
        total_students = len(student_matrix)
        q1_students = (student_matrix['Risk Quadrant'] == "CRITICAL RISK (Q1)").sum()
        q4_students = (student_matrix['Risk Quadrant'] == "HIGH PERFORMER (Q4)").sum()
        avg_ahi = student_matrix['Academic Health Index (AHI)'].mean()

        st.markdown("##### Cohort Demographics & Count Summary")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Student Enrolled", total_students)
        m2.metric("Critical Risk (Q1) Count", q1_students, delta=f"{q1_students} At-Risk", delta_color="inverse")
        m3.metric("High Performers (Q4)", q4_students, delta=f"{q4_students} Honor Candidates")
        m4.metric("Cohort Health Index (AHI)", f"{avg_ahi:.1f} / 100")

        st.markdown("---")
        st.markdown("##### Filter & Search Student Profiles")
        
        search_col, filter_col = st.columns([2, 1])
        with search_col:
            search_query = st.text_input("Search by Student Name or ID:", "").lower()
        with filter_col:
            selected_quadrant = st.selectbox("Filter by Risk Category:", ["ALL", "CRITICAL RISK (Q1)", "ATTENDANCE RISK (Q2)", "ACADEMIC RISK (Q3)", "HIGH PERFORMER (Q4)"])

        filtered_students = student_matrix.copy()
        if search_query:
            filtered_students = filtered_students[
                filtered_students['student_name'].str.lower().str.contains(search_query) |
                filtered_students['student_id'].str.lower().str.contains(search_query)
            ]
        if selected_quadrant != "ALL":
            filtered_students = filtered_students[filtered_students['Risk Quadrant'] == selected_quadrant]

        st.markdown(f"Displaying **{len(filtered_students)} of {total_students} Student Profiles**:")
        
        # STUDENT PROFILE CARDS GRID
        card_cols = st.columns(2)
        for idx, (_, stu) in enumerate(filtered_students.iterrows()):
            col_target = card_cols[idx % 2]
            with col_target:
                badge_class = "badge-critical" if "Q1" in stu['Risk Quadrant'] else "badge-warning" if "Q2" in stu['Risk Quadrant'] else "badge-academic" if "Q3" in stu['Risk Quadrant'] else "badge-success"
                
                with st.expander(f"👤 {stu['student_name']} ({stu['student_id']}) — Score: {stu['overall_mean_pct']:.1f}% | Att: {stu['mean_attendance']:.1f}%"):
                    st.markdown(f"""
                    **Risk Status:** <span class="badge {badge_class}">{stu['Risk Quadrant']}</span>  
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
        st.info("Upload an academic dataset above to view student count profile cards.")

# ---------------------------------------------------------
# VIEW MODE 3: INSTITUTIONAL RISK & GOVERNANCE
# ---------------------------------------------------------
elif view_mode == "3. Institutional Risk Governance":
    st.markdown("<div class='section-label'>Institutional 2D Risk Matrix & Revenue Attrition Model</div>", unsafe_allow_html=True)
    
    if clean_df is not None and not clean_df.empty:
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

        st.markdown("##### Resource Allocation & Tuition Loss Model")
        r1, r2, r3, r4 = st.columns(4)
        r1.metric("Counseling Slots Required", f"{q1_count} Sessions")
        r2.metric("Warning Letters Required", f"{(student_matrix['Risk Quadrant']=='ATTENDANCE RISK (Q2)').sum()} Letters")
        r3.metric("Remedial Tutors Required", f"{(student_matrix['Risk Quadrant']=='ACADEMIC RISK (Q3)').sum()} Tutors")
        r4.metric("Tuition Revenue At-Risk", f"\u20b9{revenue_at_risk:,.0f}", delta=f"{q1_count} Dropout Candidates", delta_color="inverse")

    else:
        st.info("Upload an academic dataset above to view the Institutional Risk Matrix.")
