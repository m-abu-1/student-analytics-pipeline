import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import io
from datetime import datetime

# ---------------------------------------------------------
# PAGE CONFIGURATION & ENTERPRISE DESIGN SYSTEM
# ---------------------------------------------------------
st.set_page_config(
    page_title="Academic Decision Intelligence",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Advanced CSS Injection for Scroll Optimization & SaaS UI
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        -webkit-font-smoothing: antialiased;
    }
    
    /* Zero-wasted-space container padding */
    .block-container {
        padding: 1.25rem 2rem 2rem 2rem !important;
        max-width: 100% !important;
    }
    
    /* Global Element Spacing */
    [data-testid="stVerticalBlock"] > [style*="flex-direction: column;"] > [data-testid="stVerticalBlock"] {
        gap: 0.85rem !important;
    }

    /* Enterprise Navigation Header */
    .enterprise-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: #0F172A;
        padding: 14px 24px;
        border-radius: 8px;
        margin-bottom: 16px;
        border-left: 4px solid #4F46E5;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .brand-title { color: #F8FAFC; font-size: 17px; font-weight: 800; letter-spacing: -0.02em; }
    .brand-sub { color: #94A3B8; font-size: 13px; font-weight: 400; margin-left: 8px; }
    .status-badge {
        background: #064E3B; border: 1px solid #047857; color: #34D399;
        padding: 4px 12px; border-radius: 9999px; font-size: 11px; font-weight: 700; letter-spacing: 0.05em;
    }

    /* Interactive KPI Tiles */
    .kpi-tile {
        background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px;
        padding: 16px; transition: transform 0.2s ease, box-shadow 0.2s ease;
        box-shadow: 0 1px 2px rgba(0,0,0,0.04);
    }
    .kpi-tile:hover { transform: translateY(-2px); box-shadow: 0 10px 15px -3px rgba(0,0,0,0.08); border-color: #CBD5E1; }
    .kpi-title { font-size: 12px; font-weight: 700; color: #64748B; text-transform: uppercase; letter-spacing: 0.04em; }
    .kpi-value { font-size: 26px; font-weight: 800; color: #0F172A; margin: 4px 0; line-height: 1.1; }
    .kpi-meta { font-size: 12px; font-weight: 600; }
    
    /* Tab Styling Optimization */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px !important; border-bottom: 2px solid #E2E8F0 !important;
        background: #F8FAFC; padding: 8px 12px 0 12px; border-radius: 8px 8px 0 0;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 20px !important; border-radius: 6px 6px 0 0 !important;
        font-size: 14px !important; font-weight: 600 !important; color: #64748B !important;
        transition: all 0.2s ease; border: 1px solid transparent !important; border-bottom: none !important;
    }
    .stTabs [aria-selected="true"] {
        background: #FFFFFF !important; color: #4F46E5 !important;
        border-color: #E2E8F0 !important; border-top: 3px solid #4F46E5 !important;
        box-shadow: 0 -2px 5px rgba(0,0,0,0.02);
    }

    /* Banners & Empty States */
    .insight-banner {
        background: linear-gradient(90deg, #F8FAFC 0%, #FFFFFF 100%);
        border: 1px solid #E2E8F0; border-left: 4px solid #4F46E5;
        padding: 16px 20px; border-radius: 6px; font-size: 13.5px; color: #334155;
        line-height: 1.6; margin: 12px 0; box-shadow: 0 1px 2px rgba(0,0,0,0.02);
    }
    .empty-state {
        background: #F8FAFC; border: 2px dashed #CBD5E1; border-radius: 12px;
        padding: 60px 20px; text-align: center; margin: 24px 0;
    }
    .empty-state h3 { color: #334155; font-size: 18px; font-weight: 700; margin-bottom: 8px; }
    .empty-state p { color: #64748B; font-size: 14px; max-width: 500px; margin: 0 auto; }
    
    .section-lbl { font-size: 14px; font-weight: 800; color: #0F172A; text-transform: uppercase; letter-spacing: 0.05em; margin: 16px 0 8px 0; display: block; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# CONSTANTS & CONFIGURATION
# ---------------------------------------------------------
PLOTLY_CONFIG = dict(
    font=dict(family="Inter", color="#334155", size=12),
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#FFFFFF",
    margin=dict(l=40, r=20, t=50, b=40),
    xaxis=dict(showgrid=True, gridcolor="#F1F5F9", linecolor="#CBD5E1", zerolinecolor="#E2E8F0"),
    yaxis=dict(showgrid=True, gridcolor="#F1F5F9", linecolor="#CBD5E1", zerolinecolor="#E2E8F0")
)

ALIAS_MAP = {
    'student_id': ['student_id', 'roll_no', 'usn', 'id', 'student_code'],
    'student_name': ['student_name', 'name', 'full_name'],
    'subject_id': ['subject_id', 'subject_code', 'course_id'],
    'attendance_percentage': ['attendance_percentage', 'attendance', 'att_%', 'att'],
    'marks_obtained': ['marks_obtained', 'marks', 'score', 'total_marks'],
    'maximum_marks': ['maximum_marks', 'max_marks', 'max'],
    'academic_semester': ['academic_semester', 'semester', 'sem']
}

# ---------------------------------------------------------
# CACHED DATA PROCESSING PIPELINE (Optimizes UI Speed)
# ---------------------------------------------------------
@st.cache_data(show_spinner=False)
def process_ingestion(df_raw, att_thresh, z_thresh):
    renamed = {}
    cols_lower = {str(col).strip().lower(): col for col in df_raw.columns}
    for target, aliases in ALIAS_MAP.items():
        for alias in aliases:
            if alias in cols_lower:
                renamed[cols_lower[alias]] = target
                break
    df_raw = df_raw.rename(columns=renamed)
    
    req_keys = {'student_id', 'subject_id', 'attendance_percentage', 'marks_obtained'}
    if req_keys - set(df_raw.columns):
        return None, None, None, None, list(req_keys - set(df_raw.columns))

    if 'maximum_marks' not in df_raw.columns: df_raw['maximum_marks'] = 100.0
    if 'student_name' not in df_raw.columns: df_raw['student_name'] = df_raw['student_id']
    if 'academic_semester' not in df_raw.columns: df_raw['academic_semester'] = "CURRENT"

    clean_rows, audit_entries = [], []
    
    for idx, row in df_raw.iterrows():
        s_id = str(row.get('student_id', '')).strip()
        sub_id = str(row.get('subject_id', '')).strip()
        s_name = str(row.get('student_name', s_id)).strip()
        
        reasons = []
        if not s_id or s_id == 'nan': reasons.append("Missing Student ID")
        if not sub_id or sub_id == 'nan': reasons.append("Missing Subject ID")
            
        try:
            att = float(row.get('attendance_percentage', -1))
            marks = float(row.get('marks_obtained', -1))
            max_m = float(row.get('maximum_marks', 100.0))
            
            if not (0.0 <= att <= 100.0): reasons.append(f"Invalid Attendance: {att}%")
            if marks < 0.0 or marks > max_m: reasons.append(f"Invalid Marks: {marks}/{max_m}")
                
            if not reasons:
                clean_rows.append({
                    "student_id": s_id, "student_name": s_name, "subject_id": sub_id,
                    "academic_semester": str(row.get('academic_semester', '')).strip(),
                    "attendance_percentage": att, "marks_obtained": marks,
                    "maximum_marks": max_m, "normalized_mark_pct": (marks / max_m) * 100.0
                })
        except ValueError:
            reasons.append("Type Error: Expected Numeric")
            
        if reasons:
            audit_entries.append({
                "Row": idx + 2, "Student ID": s_id, "Subject ID": sub_id,
                "Error": " | ".join(reasons), "Payload": str(row.to_dict())
            })

    clean_df = pd.DataFrame(clean_rows).drop_duplicates(subset=['student_id', 'subject_id'], keep='first')
    audit_df = pd.DataFrame(audit_entries)
    
    if clean_df.empty: return clean_df, audit_df, None, None, None

    # Subject Analytics & OBE
    sub_summary = clean_df.groupby('subject_id').agg(
        subject_mean=('normalized_mark_pct', 'mean'),
        subject_std=('normalized_mark_pct', 'std'),
        student_count=('student_id', 'nunique'),
        pass_count=('normalized_mark_pct', lambda x: (x >= 50.0).sum())
    ).reset_index()
    sub_summary['subject_std'] = sub_summary['subject_std'].fillna(0.0)
    sub_summary['SDI'] = (100.0 - sub_summary['subject_mean']).round(2)
    sub_summary['Pass Rate (%)'] = ((sub_summary['pass_count'] / sub_summary['student_count']) * 100.0).round(1)
    
    def obe_level(pr):
        if pr >= 70: return "Level 3 (High)"
        if pr >= 60: return "Level 2 (Moderate)"
        if pr >= 50: return "Level 1 (Low)"
        return "Level 0 (Unattained)"
    sub_summary['OBE'] = sub_summary['Pass Rate (%)'].apply(obe_level)
    
    # Z-Score computation
    clean_df = clean_df.merge(sub_summary[['subject_id', 'subject_mean', 'subject_std']], on='subject_id', how='left')
    clean_df['z_score'] = np.where(clean_df['subject_std'] > 0, (clean_df['normalized_mark_pct'] - clean_df['subject_mean']) / clean_df['subject_std'], 0.0)

    # Student Matrix
    stu_mat = clean_df.groupby(['student_id', 'student_name']).agg(
        mean_attendance=('attendance_percentage', 'mean'),
        overall_mean_pct=('normalized_mark_pct', 'mean'),
        avg_z_score=('z_score', 'mean')
    ).reset_index()
    stu_mat['AHI'] = ((stu_mat['overall_mean_pct'] * 0.6) + (stu_mat['mean_attendance'] * 0.4)).round(2)

    def risk_quad(row):
        a_risk = row['mean_attendance'] < att_thresh
        z_risk = row['avg_z_score'] < z_thresh
        if a_risk and z_risk: return "Q1: CRITICAL RISK"
        if a_risk: return "Q2: ATTENDANCE RISK"
        if z_risk: return "Q3: ACADEMIC RISK"
        return "Q4: HIGH PERFORMER"
    
    stu_mat['Risk Quadrant'] = stu_mat.apply(risk_quad, axis=1)
    
    return clean_df, audit_df, sub_summary, stu_mat, None

# ---------------------------------------------------------
# SIDEBAR: GOVERNANCE & PARAMS
# ---------------------------------------------------------
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/artificial-intelligence.png", width=60)
    st.markdown("<span class='section-lbl'>Platform Governance</span>", unsafe_allow_html=True)
    st.markdown("---")
    att_threshold = st.slider("Attendance Minimum Policy (%)", 50.0, 90.0, 75.0, 1.0)
    z_risk_threshold = st.slider("Z-Score Risk Threshold (\u03c3)", -2.0, 0.0, -0.5, 0.1)
    est_tuition = st.number_input("Annual Tuition / Student (\u20b9)", value=125000, step=10000)
    st.markdown("---")
    st.caption("Engine: Streamlit + Pandas + Plotly\n\nVersion: 4.2.0 (Production)")

# ---------------------------------------------------------
# MAIN LAYOUT: HEADER & INGESTION
# ---------------------------------------------------------
st.markdown("""
<div class="enterprise-header">
    <div>
        <span class="brand-title">ACADEMIC DECISION INTELLIGENCE PLATFORM</span>
        <span class="brand-sub">Institutional OBE Analytics & Early Warning System</span>
    </div>
    <div class="status-badge">PIPELINE SECURE</div>
</div>
""", unsafe_allow_html=True)

st.markdown("<span class='section-lbl'>1. Contract Ingestion & Sanitation Engine</span>", unsafe_allow_html=True)

col_ingest, col_tpl = st.columns([3, 1])
with col_ingest:
    uploaded_file = st.file_uploader("Mount Academic Batch Dataset (.csv or .xlsx)", type=["csv", "xlsx"], label_visibility="collapsed")
with col_tpl:
    tpl_df = pd.DataFrame({"student_id": ["S101"], "student_name": ["John Doe"], "subject_id": ["CS101"], "attendance_percentage": [85], "marks_obtained": [75], "maximum_marks": [100], "academic_semester": ["SEM_1"]})
    buf = io.BytesIO()
    tpl_df.to_excel(buf, index=False, engine='openpyxl')
    st.download_button("Download Schema Contract (.xlsx)", data=buf.getvalue(), file_name="schema_contract.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)

# ---------------------------------------------------------
# EXECUTE PIPELINE
# ---------------------------------------------------------
clean_df, audit_df, sub_summary, stu_mat = None, None, None, None

if uploaded_file:
    raw_df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
    clean_df, audit_df, sub_summary, stu_mat, missing_cols = process_ingestion(raw_df, att_threshold, z_risk_threshold)
    
    if missing_cols:
        st.error(f"Data Contract Violation. Missing mandatory fields: {missing_cols}")
        st.stop()
        
    total_raw = len(raw_df)
    total_clean = len(clean_df) if clean_df is not None else 0
    total_anomalies = len(audit_df)
    health = round((total_clean / total_raw) * 100, 1) if total_raw > 0 else 0

    k1, k2, k3, k4 = st.columns(4)
    k1.markdown(f"""<div class="kpi-tile"><div class="kpi-title">Raw Payload</div><div class="kpi-value">{total_raw}</div><div class="kpi-meta" style="color:#0284C7;">Records Received</div></div>""", unsafe_allow_html=True)
    k2.markdown(f"""<div class="kpi-tile"><div class="kpi-title">Sanitized</div><div class="kpi-value">{total_clean}</div><div class="kpi-meta" style="color:#059669;">Persisted to Engine</div></div>""", unsafe_allow_html=True)
    k3.markdown(f"""<div class="kpi-tile"><div class="kpi-title">Anomalies</div><div class="kpi-value">{total_anomalies}</div><div class="kpi-meta" style="color:#E11D48;">Isolated & Logged</div></div>""", unsafe_allow_html=True)
    k4.markdown(f"""<div class="kpi-tile"><div class="kpi-title">Health Score</div><div class="kpi-value">{health}%</div><div class="kpi-meta" style="color:{'#059669' if health > 90 else '#D97706'};">{"NBA/NAAC Ready" if health > 90 else "Review Required"}</div></div>""", unsafe_allow_html=True)

    if not audit_df.empty:
        with st.expander(f"⚠️ View {total_anomalies} Isolated Anomalies (Data Quality Audit)", expanded=False):
            st.dataframe(audit_df, use_container_width=True, hide_index=True)

# ---------------------------------------------------------
# MAIN ANALYTICS HUB
# ---------------------------------------------------------
st.markdown("<span class='section-lbl' style='margin-top:24px;'>2. Multi-Dimensional Intelligence Hub</span>", unsafe_allow_html=True)

tab_class, tab_subj, tab_stu, tab_risk = st.tabs([
    "Aggregate Class Performance", 
    "Subject Difficulty & OBE", 
    "Individual Merit Profile", 
    "2D Risk Matrix & Financials"
])

# Reusable Empty State HTML
empty_html = """
<div class="empty-state">
    <h3>Awaiting Ingestion Stream</h3>
    <p>Upload a valid academic dataset in Section 1 to unlock interactive models, spatial charts, and automated decision intelligence here.</p>
</div>
"""

with tab_class:
    if clean_df is not None:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Cohort Average Score", f"{clean_df['normalized_mark_pct'].mean():.2f}%")
        c2.metric("Cohort Average Attendance", f"{clean_df['attendance_percentage'].mean():.1f}%")
        c3.metric("Cohort Health Index (AHI)", f"{stu_mat['AHI'].mean():.1f}")
        pass_rate = (stu_mat['overall_mean_pct'] >= 50.0).mean() * 100
        c4.metric("Cohort Pass Rate (\u2265 50%)", f"{pass_rate:.1f}%")

        col_scatter, col_pie = st.columns([6, 3])
        
        with col_scatter:
            x, y = clean_df['attendance_percentage'], clean_df['normalized_mark_pct']
            r_val = x.corr(y)
            slope, intercept = np.polyfit(x, y, 1) if len(x) > 1 and np.std(x) > 0 else (0,0)
            
            fig_scatter = px.scatter(
                clean_df, x="attendance_percentage", y="normalized_mark_pct", color="subject_id",
                hover_data=["student_name"], title=f"Attendance vs. Score (r = {r_val:.3f})",
                labels={"attendance_percentage": "Attendance (%)", "normalized_mark_pct": "Score (%)"},
                height=450, color_discrete_sequence=px.colors.qualitative.Prism
            )
            fig_scatter.add_trace(go.Scatter(
                x=[x.min(), x.max()], y=[slope*x.min()+intercept, slope*x.max()+intercept],
                mode='lines', name=f'OLS Trend (m={slope:.2f})', line=dict(color='#0F172A', dash='dash', width=2)
            ))
            fig_scatter.update_layout(**PLOTLY_CONFIG)
            st.plotly_chart(fig_scatter, use_container_width=True)
            
        with col_pie:
            risk_counts = stu_mat['Risk Quadrant'].value_counts().reset_index()
            fig_pie = px.pie(
                risk_counts, values='count', names='Risk Quadrant', title="Cohort Risk Segmentation",
                color='Risk Quadrant', hole=0.4,
                color_discrete_map={
                    "Q1: CRITICAL RISK": "#E11D48", "Q2: ATTENDANCE RISK": "#D97706",
                    "Q3: ACADEMIC RISK": "#0284C7", "Q4: HIGH PERFORMER": "#059669"
                }, height=450
            )
            fig_pie.update_layout(**PLOTLY_CONFIG, legend=dict(orientation="h", y=-0.2))
            st.plotly_chart(fig_pie, use_container_width=True)
            
        st.markdown(f"""
        <div class="insight-banner">
            <strong>Algorithmic Insight:</strong> The Pearson correlation between attendance and performance is <strong>{r_val:+.3f}</strong>. 
            Based on the OLS regression slope, a 10% increase in attendance yields an estimated <strong>+{slope*10:.2f} mark</strong> improvement across the cohort.
        </div>
        """, unsafe_allow_html=True)
    else: st.markdown(empty_html, unsafe_allow_html=True)

with tab_subj:
    if clean_df is not None:
        st.dataframe(
            sub_summary.style.format({"subject_mean": "{:.2f}%", "subject_std": "{:.2f}", "SDI": "{:.2f}", "Pass Rate (%)": "{:.1f}%"}),
            use_container_width=True, hide_index=True
        )
        
        col_box, col_bar = st.columns(2)
        with col_box:
            fig_box = px.box(
                clean_df, x="subject_id", y="normalized_mark_pct", color="subject_id",
                title="Grade Distribution & Volatility (Z-Score Basis)",
                labels={"subject_id": "Subject", "normalized_mark_pct": "Score (%)"}, height=420
            )
            fig_box.update_layout(**PLOTLY_CONFIG, showlegend=False)
            st.plotly_chart(fig_box, use_container_width=True)
            
        with col_bar:
            fig_bar = px.bar(
                sub_summary, x="subject_id", y="SDI", color="OBE",
                title="Subject Difficulty Index (SDI) vs Attainment",
                labels={"subject_id": "Subject", "SDI": "Difficulty (100 - Mean)"},
                color_discrete_map={"Level 3 (High)": "#059669", "Level 2 (Moderate)": "#0284C7", "Level 1 (Low)": "#D97706", "Level 0 (Unattained)": "#E11D48"},
                height=420
            )
            fig_bar.update_layout(**PLOTLY_CONFIG)
            st.plotly_chart(fig_bar, use_container_width=True)
    else: st.markdown(empty_html, unsafe_allow_html=True)

with tab_stu:
    if clean_df is not None:
        stu_list = stu_mat['student_id'].astype(str) + " — " + stu_mat['student_name']
        selected = st.selectbox("Search Identity Registry:", options=stu_list, label_visibility="collapsed")
        sel_id = selected.split(" — ")[0]
        
        stu_data = stu_mat[stu_mat['student_id'] == sel_id].iloc[0]
        stu_recs = clean_df[clean_df['student_id'] == sel_id]
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Student Name", stu_data['student_name'])
        m2.metric("Current Quadrant", stu_data['Risk Quadrant'].split(":")[0])
        m3.metric("Avg Z-Score (Peer Rel)", f"{stu_data['avg_z_score']:+.2f} \u03c3")
        m4.metric("Health Index (AHI)", f"{stu_data['AHI']:.1f}")
        
        col_table, col_radar = st.columns([5, 4])
        with col_table:
            st.markdown("<span style='font-size:13px; font-weight:700;'>Transcribed Subject Records</span>", unsafe_allow_html=True)
            st.dataframe(
                stu_recs[['subject_id', 'attendance_percentage', 'normalized_mark_pct', 'subject_mean', 'z_score']],
                column_config={
                    "subject_id": "Subject",
                    "attendance_percentage": st.column_config.ProgressColumn("Attendance", min_value=0, max_value=100, format="%f%%"),
                    "normalized_mark_pct": st.column_config.NumberColumn("Score", format="%.1f%%"),
                    "subject_mean": st.column_config.NumberColumn("Class Avg", format="%.1f%%"),
                    "z_score": st.column_config.NumberColumn("Z-Score", format="%+.2f σ")
                },
                hide_index=True, use_container_width=True, height=360
            )
            
        with col_radar:
            fig_radar = go.Figure()
            fig_radar.add_trace(go.Scatterpolar(
                r=stu_recs['normalized_mark_pct'].tolist() + [stu_recs['normalized_mark_pct'].iloc[0]],
                theta=stu_recs['subject_id'].tolist() + [stu_recs['subject_id'].iloc[0]],
                fill='toself', name='Student', line_color='#4F46E5'
            ))
            fig_radar.add_trace(go.Scatterpolar(
                r=stu_recs['subject_mean'].tolist() + [stu_recs['subject_mean'].iloc[0]],
                theta=stu_recs['subject_id'].tolist() + [stu_recs['subject_id'].iloc[0]],
                fill='toself', name='Class Avg', line_color='#94A3B8', opacity=0.5
            ))
            fig_radar.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                showlegend=True, margin=dict(l=40, r=40, t=30, b=30), height=380,
                paper_bgcolor="rgba(0,0,0,0)"
            )
            st.plotly_chart(fig_radar, use_container_width=True)
    else: st.markdown(empty_html, unsafe_allow_html=True)

with tab_risk:
    if clean_df is not None:
        q1_mask = stu_mat['Risk Quadrant'] == "Q1: CRITICAL RISK"
        q1_count = q1_mask.sum()
        rev_risk = q1_count * est_tuition
        
        f1, f2, f3, f4 = st.columns(4)
        f1.metric("Tuition Revenue At Risk", f"\u20b9{rev_risk:,.0f}", delta=f"{q1_count} Students", delta_color="inverse")
        f2.metric("Counseling Interventions", q1_count, delta="Mandatory", delta_color="inverse")
        f3.metric("Warning Letters", (stu_mat['Risk Quadrant'] == "Q2: ATTENDANCE RISK").sum())
        f4.metric("Remedial Tutors", (stu_mat['Risk Quadrant'] == "Q3: ACADEMIC RISK").sum())
        
        fig_quad = px.scatter(
            stu_mat, x="mean_attendance", y="avg_z_score", color="Risk Quadrant",
            hover_data=["student_id", "student_name", "overall_mean_pct", "AHI"],
            title="2D Cartesian Early Warning Risk Matrix",
            labels={"mean_attendance": "Attendance (%)", "avg_z_score": "Mean Z-Score (\u03c3)"},
            color_discrete_map={
                "Q1: CRITICAL RISK": "#E11D48", "Q2: ATTENDANCE RISK": "#D97706",
                "Q3: ACADEMIC RISK": "#0284C7", "Q4: HIGH PERFORMER": "#059669"
            }, height=480
        )
        fig_quad.add_vline(x=att_threshold, line_dash="dash", line_color="#0F172A", annotation_text="Att Cutoff")
        fig_quad.add_hline(y=z_risk_threshold, line_dash="dash", line_color="#0F172A", annotation_text="Z Cutoff")
        fig_quad.update_layout(**PLOTLY_CONFIG)
        st.plotly_chart(fig_quad, use_container_width=True)

        stu_mat['Intervention Plan'] = stu_mat['Risk Quadrant'].map({
            "Q1: CRITICAL RISK": "Mandatory faculty review + Parent intimation",
            "Q2: ATTENDANCE RISK": "Issue formal low-attendance warning letter",
            "Q3: ACADEMIC RISK": "Assign remedial subject workshops & peer tutor",
            "Q4: HIGH PERFORMER": "Honor roll recognition & advanced opportunities"
        })
        
        csv_action = stu_mat.to_csv(index=False).encode('utf-8')
        st.download_button("Export Institutional Action Strategy (.csv)", data=csv_action, file_name=f"action_matrix_{datetime.now().strftime('%Y%m%d')}.csv", mime="text/csv", type="primary", use_container_width=True)
    else: st.markdown(empty_html, unsafe_allow_html=True)
