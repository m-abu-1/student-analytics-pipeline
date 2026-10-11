import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import io
from datetime import datetime

# ---------------------------------------------------------
# 1. ENTERPRISE CONFIGURATION & CSS INJECTION
# ---------------------------------------------------------
st.set_page_config(
    page_title="ADI | Academic Decision Intelligence",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Advanced viewport optimization: Eliminates all wasted whitespace and standardizes typography
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; -webkit-font-smoothing: antialiased; }
    
    /* Zero-wasted-space container padding */
    .block-container { padding: 1.5rem 2rem 2rem 2rem !important; max-width: 100% !important; }
    
    /* Enterprise Header */
    .enterprise-header {
        display: flex; justify-content: space-between; align-items: center;
        background: #0F172A; padding: 16px 24px; border-radius: 8px; margin-bottom: 24px;
        border-left: 4px solid #4F46E5; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .brand-title { color: #F8FAFC; font-size: 18px; font-weight: 800; letter-spacing: -0.02em; }
    .brand-sub { color: #94A3B8; font-size: 13px; font-weight: 500; margin-left: 12px; }
    .status-badge {
        background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.2); 
        color: #34D399; padding: 4px 12px; border-radius: 999px; font-size: 11px; font-weight: 700; letter-spacing: 0.05em;
    }

    /* KPI Tiles */
    .kpi-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 24px; }
    .kpi-tile {
        background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px; padding: 16px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.02); transition: all 0.2s ease;
    }
    .kpi-tile:hover { transform: translateY(-2px); box-shadow: 0 10px 15px -3px rgba(0,0,0,0.05); border-color: #CBD5E1; }
    .kpi-title { font-size: 12px; font-weight: 700; color: #64748B; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 4px; }
    .kpi-value { font-size: 28px; font-weight: 800; color: #0F172A; line-height: 1.2; }
    
    /* Tab Overrides */
    .stTabs [data-baseweb="tab-list"] { gap: 8px !important; border-bottom: 2px solid #E2E8F0 !important; background: transparent; }
    .stTabs [data-baseweb="tab"] { padding: 12px 20px !important; font-size: 14px !important; font-weight: 600 !important; color: #64748B !important; border: none !important; }
    .stTabs [aria-selected="true"] { color: #4F46E5 !important; border-bottom: 3px solid #4F46E5 !important; background: #F8FAFC !important; border-radius: 6px 6px 0 0; }
</style>
""", unsafe_allow_html=True)

PLOTLY_CONFIG = dict(font=dict(family="Inter", color="#334155"), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#FFFFFF", margin=dict(l=20, r=20, t=40, b=20))

# ---------------------------------------------------------
# 2. CORE COMPUTATION ENGINE (CACHED)
# ---------------------------------------------------------
@st.cache_data(show_spinner=False)
def process_data(df, att_thresh, z_thresh):
    """Vectorized data processing pipeline for optimal execution speed."""
    # Enforce schema constraints safely
    req_cols = {'student_id', 'subject_id', 'attendance_percentage', 'marks_obtained'}
    missing = req_cols - set(df.columns)
    if missing: return None, None, None, list(missing)

    df['maximum_marks'] = df.get('maximum_marks', 100.0)
    df['student_name'] = df.get('student_name', df['student_id'])
    
    # Isolate valid records vs anomalies
    valid_mask = (df['attendance_percentage'].between(0, 100)) & (df['marks_obtained'].between(0, df['maximum_marks']))
    df_clean = df[valid_mask].copy()
    df_audit = df[~valid_mask].copy()
    
    if df_clean.empty: return df_clean, df_audit, None, None

    # Normalization
    df_clean['pct_score'] = (df_clean['marks_obtained'] / df_clean['maximum_marks']) * 100.0

    # Subject Aggregation (OBE & SDI)
    sub_stats = df_clean.groupby('subject_id').agg(
        mean_score=('pct_score', 'mean'), std_score=('pct_score', 'std'),
        student_count=('student_id', 'nunique'), pass_count=('pct_score', lambda x: (x >= 50).sum())
    ).reset_index()
    
    sub_stats['std_score'] = sub_stats['std_score'].fillna(0.0)
    sub_stats['SDI'] = 100.0 - sub_stats['mean_score']
    sub_stats['Pass_Rate'] = (sub_stats['pass_count'] / sub_stats['student_count']) * 100.0
    sub_stats['OBE_Level'] = pd.cut(sub_stats['Pass_Rate'], bins=[-1, 49.9, 59.9, 69.9, 100], labels=["L0: Unattained", "L1: Low", "L2: Moderate", "L3: High"])

    # Z-Score Vectorization
    df_clean = df_clean.merge(sub_stats[['subject_id', 'mean_score', 'std_score']], on='subject_id')
    df_clean['z_score'] = np.where(df_clean['std_score'] > 0, (df_clean['pct_score'] - df_clean['mean_score']) / df_clean['std_score'], 0.0)

    # Student Matrix Aggregation
    stu_mat = df_clean.groupby(['student_id', 'student_name']).agg(
        att_mean=('attendance_percentage', 'mean'), score_mean=('pct_score', 'mean'), z_mean=('z_score', 'mean')
    ).reset_index()
    
    # 2D Risk Quadrant Logic
    conditions = [
        (stu_mat['att_mean'] < att_thresh) & (stu_mat['z_mean'] < z_thresh),
        (stu_mat['att_mean'] < att_thresh),
        (stu_mat['z_mean'] < z_thresh)
    ]
    choices = ["Q1: CRITICAL RISK", "Q2: ATTENDANCE RISK", "Q3: ACADEMIC RISK"]
    stu_mat['Risk_Quadrant'] = np.select(conditions, choices, default="Q4: HIGH PERFORMER")
    stu_mat['AHI'] = (stu_mat['score_mean'] * 0.6) + (stu_mat['att_mean'] * 0.4)

    return df_clean, df_audit, sub_stats, stu_mat

# ---------------------------------------------------------
# 3. SIDEBAR CONTROLS
# ---------------------------------------------------------
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/artificial-intelligence.png", width=50)
    st.markdown("### Institutional Policies")
    att_threshold = st.slider("Min. Attendance (%)", 50.0, 90.0, 75.0, 1.0, help="University mandated minimum attendance.")
    z_risk_threshold = st.slider("Academic Risk (\u03c3)", -2.0, 0.0, -0.5, 0.1, help="Standard deviations below class average to trigger warning.")
    tuition = st.number_input("Annual Tuition (\u20b9)", value=125000, step=10000)
    st.markdown("---")
    st.caption("Engine: Streamlit + Pandas + Plotly\n\nBuild: 4.2.0-Prod")

# ---------------------------------------------------------
# 4. APPLICATION UI ROUTING
# ---------------------------------------------------------
st.markdown("""
<div class="enterprise-header">
    <div>
        <span class="brand-title">ACADEMIC DECISION INTELLIGENCE PLATFORM</span>
        <span class="brand-sub">Real-time NBA/NAAC Outcomes & Early Warning System</span>
    </div>
    <div class="status-badge">SYSTEM OPTIMIZED</div>
</div>
""", unsafe_allow_html=True)

# File Ingestion
col1, col2 = st.columns([3, 1])
uploaded_file = col1.file_uploader("Mount Academic Batch Dataset (.csv)", type=["csv"], label_visibility="collapsed")

if not uploaded_file:
    st.info("Awaiting Data Pipeline Connection. Please upload a CSV containing: `student_id`, `student_name`, `subject_id`, `attendance_percentage`, `marks_obtained`.")
    st.stop()

# Execution
df_raw = pd.read_csv(uploaded_file)
df_clean, df_audit, sub_stats, stu_mat = process_data(df_raw, att_threshold, z_risk_threshold)

if type(df_clean) == list: # Checks if returns missing cols
    st.error(f"Schema Violation. Missing mandatory columns: {df_clean}")
    st.stop()

# Global KPI Ribbon
health_score = (len(df_clean) / len(df_raw)) * 100
st.markdown(f"""
<div class="kpi-grid">
    <div class="kpi-tile"><div class="kpi-title">Records Analyzed</div><div class="kpi-value">{len(df_clean)}</div></div>
    <div class="kpi-tile"><div class="kpi-title">Data Anomalies</div><div class="kpi-value" style="color:#E11D48;">{len(df_audit)}</div></div>
    <div class="kpi-tile"><div class="kpi-title">Cohort Health Index</div><div class="kpi-value">{stu_mat['AHI'].mean():.1f}</div></div>
    <div class="kpi-tile"><div class="kpi-title">System Health</div><div class="kpi-value" style="color:{'#059669' if health_score > 90 else '#D97706'};">{health_score:.1f}%</div></div>
</div>
""", unsafe_allow_html=True)

# Analytics Modules
t1, t2, t3, t4 = st.tabs(["Aggregate Intelligence", "Subject & OBE Analytics", "Student Micro-Profiler", "Financial Risk Matrix"])

with t1:
    c1, c2 = st.columns([2, 1])
    with c1:
        # Vectorized OLS calculation
        x, y = df_clean['attendance_percentage'], df_clean['pct_score']
        m, b = np.polyfit(x, y, 1) if len(x) > 1 else (0,0)
        r_val = x.corr(y)
        
        fig = px.scatter(df_clean, x="attendance_percentage", y="pct_score", color="subject_id", hover_data=["student_name"], title=f"Attendance vs Performance Mapping (Pearson r: {r_val:.2f})", height=400)
        fig.add_trace(go.Scatter(x=[x.min(), x.max()], y=[m*x.min()+b, m*x.max()+b], mode='lines', name='Linear Trend', line=dict(color='black', dash='dash')))
        fig.update_layout(**PLOTLY_CONFIG)
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig_pie = px.pie(stu_mat, names='Risk_Quadrant', hole=0.5, title="Cohort Risk Distribution", color='Risk_Quadrant', 
                         color_discrete_map={"Q1: CRITICAL RISK": "#E11D48", "Q2: ATTENDANCE RISK": "#D97706", "Q3: ACADEMIC RISK": "#0284C7", "Q4: HIGH PERFORMER": "#059669"})
        fig_pie.update_layout(**PLOTLY_CONFIG, showlegend=False)
        st.plotly_chart(fig_pie, use_container_width=True)

with t2:
    st.dataframe(sub_stats, column_config={
        "subject_id": "Subject Code",
        "mean_score": st.column_config.NumberColumn("Average Score", format="%.1f%%"),
        "SDI": st.column_config.ProgressColumn("Difficulty Index (SDI)", min_value=0, max_value=100),
        "Pass_Rate": st.column_config.NumberColumn("Pass Rate", format="%.1f%%"),
        "OBE_Level": "NBA OBE Attainment"
    }, hide_index=True, use_container_width=True)

with t3:
    sel_stu = st.selectbox("Search Student Registry", options=stu_mat['student_id'] + " - " + stu_mat['student_name'])
    sid = sel_stu.split(" - ")[0]
    stu_recs = df_clean[df_clean['student_id'] == sid]
    
    rc1, rc2 = st.columns([1, 1])
    with rc1:
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(r=stu_recs['pct_score'].tolist() + [stu_recs['pct_score'].iloc[0]], theta=stu_recs['subject_id'].tolist() + [stu_recs['subject_id'].iloc[0]], fill='toself', name='Student Score'))
        fig_radar.add_trace(go.Scatterpolar(r=stu_recs['mean_score'].tolist() + [stu_recs['mean_score'].iloc[0]], theta=stu_recs['subject_id'].tolist() + [stu_recs['subject_id'].iloc[0]], fill='toself', name='Class Average'))
        fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), margin=dict(t=40, b=20), height=350, paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_radar, use_container_width=True)
    with rc2:
        st.dataframe(stu_recs[['subject_id', 'attendance_percentage', 'pct_score', 'z_score']], column_config={
            "attendance_percentage": st.column_config.ProgressColumn("Attendance", min_value=0, max_value=100, format="%.1f%%"),
            "z_score": st.column_config.NumberColumn("Z-Score", format="%+.2f σ")
        }, hide_index=True, use_container_width=True)

with t4:
    q1_count = (stu_mat['Risk_Quadrant'] == 'Q1: CRITICAL RISK').sum()
    st.error(f"🚨 **Financial & Retention Alert:** {q1_count} students in Critical Risk quadrant. Estimated \u20b9{(q1_count * tuition):,.0f} tuition revenue at risk.")
    
    fig_quad = px.scatter(stu_mat, x="att_mean", y="z_mean", color="Risk_Quadrant", hover_data=["student_name"],
                          title="2D Action Matrix (Attendance vs Z-Score)", height=400,
                          color_discrete_map={"Q1: CRITICAL RISK": "#E11D48", "Q2: ATTENDANCE RISK": "#D97706", "Q3: ACADEMIC RISK": "#0284C7", "Q4: HIGH PERFORMER": "#059669"})
    fig_quad.add_vline(x=att_threshold, line_dash="dash", line_color="#0F172A", annotation_text="Att Cutoff")
    fig_quad.add_hline(y=z_risk_threshold, line_dash="dash", line_color="#0F172A", annotation_text="Z Cutoff")
    fig_quad.update_layout(**PLOTLY_CONFIG)
    st.plotly_chart(fig_quad, use_container_width=True)
