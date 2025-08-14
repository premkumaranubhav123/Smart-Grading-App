# app.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO

# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(
    page_title="🎯 Smart Grading Pro",
    page_icon="🎯",
    layout="wide"
)

# -----------------------------
# Custom CSS for Dark Mode & Visibility
# -----------------------------
st.markdown("""
<style>
    /* Dark background, white text */
    .main {
        background-color: #0e1117;
        color: white;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #ffffff;
    }
    /* File uploader text */
    .stFileUploader label {
        color: white !important;
    }
    /* Markdown text */
    p, div, span {
        color: white !important;
    }
    /* Table and dataframe */
    .stTable, .stDataFrame {
        color: white;
    }
    /* Button styling */
    .stButton button {
        background-color: #007bff;
        color: white;
        border-radius: 10px;
        padding: 10px 24px;
        font-size: 18px;
        border: none;
    }
    .stButton button:hover {
        background-color: #0056b3;
        transform: scale(1.05);
    }
    /* Info box */
    .info-box {
        background-color: #1f283a;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #007bff;
        margin: 10px 0;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Header
# -----------------------------
st.markdown("<h1 style='text-align: center;'>🎯 Smart Grading Pro</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #aaa; font-size: 18px;'>"
            "Upload marks, set grade boundaries, and get instant analytics.</p>", unsafe_allow_html=True)
st.markdown("---")

# -----------------------------
# Sidebar: Grade Boundaries
# -----------------------------
st.sidebar.header("🔧 Customize Grade Boundaries")
st.sidebar.markdown("Adjust sliders to define minimum marks for each grade:")

grade_ranges = {}
grade_ranges['A'] = st.sidebar.slider("A (Excellent)", 70.0, 100.0, 85.0)
grade_ranges['B'] = st.sidebar.slider("B (Good)", 60.0, 90.0, 75.0)
grade_ranges['C'] = st.sidebar.slider("C (Average)", 50.0, 80.0, 60.0)
grade_ranges['D'] = st.sidebar.slider("D (Pass)", 40.0, 70.0, 50.0)

st.sidebar.markdown("---")
st.sidebar.info("💡 Adjust sliders to see changes in real time.")

# -----------------------------
# File Uploader
# -----------------------------
st.markdown("<div class='info-box'>"
            "📥 Upload your <strong>Marks for Grading.xlsx</strong> or any Excel file with a <code>Marks</code> column.</div>",
            unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "Upload Excel File",
    type=["xlsx"],
    label_visibility="collapsed"
)

if uploaded_file:
    with st.spinner("📊 Processing student data..."):
        try:
            # Read Excel
            df = pd.read_excel(uploaded_file)

            # Validate 'Marks' column
            if 'Marks' not in df.columns:
                st.error("❌ Your file must have a column named **'Marks'**.")
            else:
                # Preserve available columns
                available_cols = [col for col in ['SNo', 'Roll No', 'Name', 'Marks'] if col in df.columns]

                # Sort by Marks (high to low)
                df = df[available_cols].sort_values(by='Marks', ascending=False).reset_index(drop=True)

                # Assign Grades
                def assign_grade(marks):
                    if marks >= grade_ranges['A']:
                        return 'A'
                    elif marks >= grade_ranges['B']:
                        return 'B'
                    elif marks >= grade_ranges['C']:
                        return 'C'
                    elif marks >= grade_ranges['D']:
                        return 'D'
                    else:
                        return 'F'

                df['Grade'] = df['Marks'].apply(assign_grade)

                # -----------------------------
                # Display Data
                # -----------------------------
                st.subheader("📋 Student Grades (Sorted by Marks)")
                st.dataframe(df, use_container_width=True, height=400)

                # -----------------------------
                # Statistics
                # -----------------------------
                st.subheader("📈 Performance Analytics")

                col1, col2 = st.columns([1, 2])

                with col1:
                    # Grade counts and percentages
                    grade_counts = df['Grade'].value_counts().reindex(['A', 'B', 'C', 'D', 'F'], fill_value=0)
                    total = len(df)
                    grade_percent = (grade_counts / total * 100).round(1)

                    stats_df = pd.DataFrame({
                        'Students': grade_counts,
                        'Percentage (%)': grade_percent
                    })
                    st.table(stats_df)

                with col2:
                    # Histogram with color zones
                    fig, ax = plt.subplots(figsize=(10, 6))
                    bins = [0, grade_ranges['D'], grade_ranges['C'], grade_ranges['B'], grade_ranges['A'], 100]
                    colors = ['#d9534f', '#f0ad4e', '#5bc0de', '#428bca', '#5cb85c']
                    labels = ['F', 'D', 'C', 'B', 'A']

                    for i in range(len(bins) - 1):
                        data = df[(df['Marks'] >= bins[i]) & (df['Marks'] < bins[i + 1])]['Marks']
                        ax.hist(data, bins=15, range=(bins[i], bins[i + 1]),
                                color=colors[i], alpha=0.8, edgecolor='black', label=f"{labels[i]}: {len(data)}")

                    avg_mark = df['Marks'].mean()
                    ax.axvline(avg_mark, color='red', linestyle='--', linewidth=3,
                               label=f'Average: {avg_mark:.1f}')
                    ax.set_title("📊 Distribution of Marks", fontsize=16, fontweight='bold')
                    ax.set_xlabel("Marks")
                    ax.set_ylabel("Number of Students")
                    ax.legend()
                    st.pyplot(fig)

                # -----------------------------
                # Export Button
                # -----------------------------
                st.subheader("💾 Export Graded Data")

                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df.to_excel(writer, sheet_name='Graded Results', index=False)
                output.seek(0)

                st.download_button(
                    label="⬇️ Download as Excel",
                    data=output,
                    file_name="graded_output_with_grades.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

        except Exception as e:
            st.error(f"❌ Error processing file: {e}")
else:
    st.markdown("<div style='text-align: center; padding: 40px; color: #aaa;'>"
                "📁 Upload a file to get started.</div>", unsafe_allow_html=True)

# -----------------------------
# Footer
# -----------------------------
st.markdown("---")
st.markdown("<p style='text-align: center; color: #888; font-size: 14px;'>"
            "🎯 Smart Grading Pro | Built with ❤️ using Streamlit</p>",
            unsafe_allow_html=True)