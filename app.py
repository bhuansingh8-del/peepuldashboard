import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ---------------------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------------------
st.set_page_config(
    page_title="MEL Dashboard: Alirajpur District Performance",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for a professional look
st.markdown("""
    <style>
    .main { background-color: #F8F9FA; }
    h1, h2, h3 { color: #2C3E50; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    .stMetric { background-color: #FFFFFF; padding: 15px; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------------------
# Data Loading
# ---------------------------------------------------------------------
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("Cleaned_Alirajpur_Analysis.csv")
        return df
    except FileNotFoundError:
        st.error("Data file 'Cleaned_Alirajpur_Analysis.csv' not found. Please ensure it is in the same directory.")
        return pd.DataFrame()

df = load_data()

if df.empty:
    st.stop()

# ---------------------------------------------------------------------
# Sidebar Filters
# ---------------------------------------------------------------------
st.sidebar.title("Dashboard Controls")
st.sidebar.markdown("Filter data to update the visualizations dynamically.")

# Class Filter
all_classes = sorted(df['Class'].unique().tolist())
selected_classes = st.sidebar.multiselect(
    "Select Class(es)", 
    options=all_classes, 
    default=all_classes
)

# Subject Filter
all_subjects = sorted(df['Subject'].unique().tolist())
selected_subjects = st.sidebar.multiselect(
    "Select Subject(s)", 
    options=all_subjects, 
    default=all_subjects
)

# Filter the dataframe based on selection
filtered_df = df[
    (df['Class'].isin(selected_classes)) & 
    (df['Subject'].isin(selected_subjects))
]

if filtered_df.empty:
    st.warning("No data available for the selected filters.")
    st.stop()

# ---------------------------------------------------------------------
# Header & Key Performance Indicators (KPIs)
# ---------------------------------------------------------------------
st.title("Monitoring & Evaluation: Learning Outcomes Analysis")
st.markdown("### District Performance: Alirajpur vs. Benchmarks")
st.markdown("---")

# Calculate KPIs
district_avg = filtered_df['District (Alirajpur)'].mean()
state_avg = filtered_df['State Average'].mean()
national_avg = filtered_df['National Average'].mean()
avg_gap_state = district_avg - state_avg

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label="District Average Score", value=f"{district_avg:.1f}%", delta=f"{avg_gap_state:.1f}% vs State", delta_color="normal")
with col2:
    st.metric(label="State Average Score", value=f"{state_avg:.1f}%")
with col3:
    st.metric(label="National Average Score", value=f"{national_avg:.1f}%")
with col4:
    total_los = len(filtered_df)
    critical_los = len(filtered_df[filtered_df['District (Alirajpur)'] < 40])
    st.metric(label="Critical Learning Outcomes (<40%)", value=f"{critical_los} / {total_los}", delta="- Needs Intervention", delta_color="inverse")

st.markdown("<br>", unsafe_allow_html=True)

# ---------------------------------------------------------------------
# Visualizations
# ---------------------------------------------------------------------
col_chart1, col_chart2 = st.columns(2)

# 1. Subject-Wise Performance Comparison
with col_chart1:
    st.subheader("Performance by Subject")
    subject_agg = filtered_df.groupby('Subject')[['District (Alirajpur)', 'State Average', 'National Average']].mean().reset_index()
    
    fig_subject = go.Figure()
    fig_subject.add_trace(go.Bar(x=subject_agg['Subject'], y=subject_agg['District (Alirajpur)'], name='District', marker_color='#2E86C1'))
    fig_subject.add_trace(go.Bar(x=subject_agg['Subject'], y=subject_agg['State Average'], name='State Avg', marker_color='#95A5A6'))
    fig_subject.add_trace(go.Bar(x=subject_agg['Subject'], y=subject_agg['National Average'], name='National Avg', marker_color='#34495E'))
    
    fig_subject.update_layout(barmode='group', plot_bgcolor='rgba(0,0,0,0)', yaxis_title='Average Score (%)', margin=dict(t=20, b=20, l=0, r=0))
    st.plotly_chart(fig_subject, use_container_width=True)

# 2. Class-Wise Learning Slide (Trend)
with col_chart2:
    st.subheader("Class-Wise Progression (Learning Slide)")
    class_agg = filtered_df.groupby('Class')[['District (Alirajpur)', 'State Average']].mean().reset_index()
    
    fig_trend = px.line(class_agg, x='Class', y=['District (Alirajpur)', 'State Average'], 
                        markers=True, 
                        labels={'value': 'Average Score (%)', 'variable': 'Metric'},
                        color_discrete_map={'District (Alirajpur)': '#E74C3C', 'State Average': '#7F8C8D'})
    
    fig_trend.update_layout(plot_bgcolor='rgba(0,0,0,0)', xaxis=dict(type='category'), margin=dict(t=20, b=20, l=0, r=0))
    st.plotly_chart(fig_trend, use_container_width=True)

st.markdown("---")

# 3. Gap Analysis (Diverging Bar Chart)
st.subheader("Achievement Gap Analysis (District vs. State)")
st.markdown("Negative values indicate the district is performing below the state average.")

# Sort to show biggest gaps
gap_df = filtered_df.sort_values(by='Gap_from_State').head(15) # Show top 15 worst gaps for clarity

fig_gap = px.bar(gap_df, x='Gap_from_State', y='LO Code', orientation='h', 
                 color='Gap_from_State', color_continuous_scale='Reds_r',
                 hover_data=['Class', 'Subject', 'District (Alirajpur)', 'State Average'],
                 labels={'Gap_from_State': 'Gap from State (%)', 'LO Code': 'Learning Outcome (LO)'})

fig_gap.update_layout(plot_bgcolor='rgba(0,0,0,0)', margin=dict(t=20, b=20, l=0, r=0))
fig_gap.add_vline(x=0, line_width=2, line_color="black")
st.plotly_chart(fig_gap, use_container_width=True)

# ---------------------------------------------------------------------
# Detailed Data View (Hard Spots)
# ---------------------------------------------------------------------
st.markdown("---")
st.subheader("Critical Intervention Areas ('Hard Spots')")
st.markdown("Learning outcomes where the district score is lowest. Use the table below to prioritize pedagogical interventions.")

# Filter for Hard Spots
hard_spots_df = filtered_df.sort_values(by='District (Alirajpur)', ascending=True)

# Display as an interactive dataframe
st.dataframe(
    hard_spots_df[['Class', 'Subject', 'LO Code', 'District (Alirajpur)', 'State Average', 'Gap_from_State']].head(10).style.background_gradient(cmap='Reds', subset=['District (Alirajpur)']),
    use_container_width=True,
    hide_index=True
)