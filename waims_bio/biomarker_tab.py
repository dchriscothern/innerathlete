import streamlit as st
import pandas as pd
import plotly.express as px

def run_biomarker_tab():
    st.header("🩸 Biomarker Analysis")
    
    # 1. File Uploader
    uploaded_file = st.file_uploader("Upload Bloodwork CSV", type=["csv"])
    
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        
        # 2. Key Metric Highlights (KPIs)
        if 'Metric' in df.columns and 'Value' in df.columns:
            cols = st.columns(len(df))
            for i, row in df.iterrows():
                cols[i].metric(label=row['Metric'], value=row['Value'], delta=row.get('Status', ""))

        # 3. Trend Visualization
        st.subheader("Biomarker Trends")
        # Assuming CSV has 'Date', 'Metric', 'Value'
        if 'Date' in df.columns:
            fig = px.line(df, x="Date", y="Value", color="Metric", markers=True,
                         color_discrete_sequence=["#00FFA3", "#FF4B4B", "#00CCFF"])
            fig.update_layout(template="plotly_dark", plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("💡 Please upload a CSV file. Expected columns: Date, Metric, Value, Status")
        
        # Provide a download button for a template
        template_data = "Date,Metric,Value,Status\n2026-01-01,Cortisol,15,Optimal\n2026-02-01,Cortisol,22,Elevated\n2026-03-01,Cortisol,18,Stabilizing"
        st.download_button("Download CSV Template", template_data, "biomarker_template.csv")