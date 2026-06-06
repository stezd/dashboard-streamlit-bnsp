import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Dampak AI pada Mahasiswa", layout="wide")

# ── Load Data ──────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("ai_student_impact_dataset_CLEAN.csv")
    df["AI_Usage_Segment"] = pd.cut(
        df["Weekly_GenAI_Hours"],
        bins=[0, 5, 15, float("inf")],
        labels=["Ringan (0-5)", "Sedang (5-15)", "Berat (>15)"],
        right=False,
    )
    df["Dependency_Level"] = pd.cut(
        df["Perceived_AI_Dependency"],
        bins=[0, 3, 7, 11],
        labels=["Rendah (1-3)", "Sedang (4-7)", "Tinggi (8-10)"],
        right=False,
    )
    return df

df = load_data()

# ── Sidebar Filter ─────────────────────────────────────────
st.sidebar.title("Filter")
majors = st.sidebar.multiselect("Bidang Studi", df["Major_Category"].unique(), default=df["Major_Category"].unique())
years = st.sidebar.multiselect("Jenjang Studi", sorted(df["Year_of_Study"].unique()), default=sorted(df["Year_of_Study"].unique()))
policies = st.sidebar.multiselect("Kebijakan Institusi", df["Institutional_Policy"].unique(), default=df["Institutional_Policy"].unique())

st.sidebar.markdown("---")
st.sidebar.caption("Aldi Pramudya | G6401231003")

mask = df["Major_Category"].isin(majors) & df["Year_of_Study"].isin(years) & df["Institutional_Policy"].isin(policies)
df_f = df[mask]

# ── Tab 1: Ringkasan ───────────────────────────────────────
st.title("Dashboard Dampak AI pada Mahasiswa")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["\U0001f4ca Overview", "\U0001f4c8 Dampak AI", "\U0001f9e0 Kesehatan Mental", "\U0001f4da Retensi Pengetahuan", "\u26a0\ufe0f Profil Risiko"])

with tab1:
    st.header("Overview: Distribusi & KPI")

    c1, c2, c3 = st.columns(3)
    c1.metric("Rata-rata GPA Akhir", f"{df_f['Post_Semester_GPA'].mean():.3f}")
    c2.metric("Rata-rata Retensi Keahlian", f"{df_f['Skill_Retention_Score'].mean():.1f}")
    c3.metric("% Risiko Burnout Tinggi", f"{(df_f['Burnout_Risk_Level'] == 'High').mean() * 100:.1f}%")

    st.markdown("---")
    st.subheader("Temuan Utama")
    col_a, col_b = st.columns(2)
    with col_a:
        st.success("Intensitas AI tidak memengaruhi GPA. Yang penting adalah bagaimana AI digunakan dan berapa lama belajar tradisional.")
        st.warning("Kebijakan Strict_Ban memiliki tingkat kecemasan mahasiswa 19% lebih tinggi, tanpa peningkatan GPA yang berarti.")
    with col_b:
        st.error("Penggunaan AI tinggi (Heavy User) berkorelasi kuat dengan burnout. Mahasiswa dengan ketergantungan AI tinggi juga memiliki retensi pengetahuan lebih rendah.")

    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        fig = px.pie(df_f, names="Major_Category", title="Distribusi Bidang Studi")
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig = px.histogram(df_f, x="Year_of_Study", title="Distribusi Jenjang Studi", category_orders={"Year_of_Study": ["Freshman","Sophomore","Junior","Senior","Graduate"]})
        st.plotly_chart(fig, use_container_width=True)
    with col3:
        fig = px.histogram(df_f, x="Institutional_Policy", title="Distribusi Kebijakan Institusi")
        st.plotly_chart(fig, use_container_width=True)

# ── Tab 2: Dampak AI ───────────────────────────────────────
with tab2:
    st.header("Dampak AI terhadap Performa Akademik")

    with st.expander("Apa artinya?", expanded=False):
        st.info("Intensitas jam AI tidak memengaruhi GPA. Yang membedakan adalah **cara** penggunaan AI: mahasiswa yang pakai AI untuk debugging nilainya lebih tinggi dibanding yang minta jawaban langsung. Langganan premium vs gratis: tidak ada bedanya. Jam belajar tradisional tetap berkorelasi positif dengan GPA di semua tipe penggunaan AI.")
        with st.expander("Detail Statistik"):
            st.markdown("""
            **Q1: Weekly_GenAI_Hours vs Post_Semester_GPA**  
            Pearson r = -0.0186, p = 0.00003, r2 = 0.0003  
            Signifikan (Bonferroni), effect size diabaikan. Tidak ada hubungan linier.

            **Q5: Primary_Use_Case vs Post_Semester_GPA**  
            One-way ANOVA: F = 49.56, p = 0.000, eta2 = 0.004 (kecil)  
            Tukey HSD: Debugging/Troubleshooting (M = 3.396) > semua; Direct_Answer (M = 3.294) < semua.

            **Q6: Traditional_Study_Hours vs Post_GPA per Use Case**  
            Semua signifikan: Direct_Answer r = 0.185, Summarizing r = 0.151, Debugging r = 0.132, Ideation r = 0.126, Copywriting r = 0.122.

            **Q7: Paid_Subscription vs Post_Semester_GPA**  
            Welch t = -1.24, p = 0.216, Cohen d = -0.011. Tidak signifikan.
            """)

    c1, c2 = st.columns(2)
    with c1:
        df_q1 = df_f.melt(id_vars=["AI_Usage_Segment"],
                          value_vars=["Pre_Semester_GPA", "Post_Semester_GPA"],
                          var_name="GPA_Type", value_name="GPA")
        df_q1["GPA_Type"] = df_q1["GPA_Type"].str.replace("_Semester_", " ").str.replace("_", " ")
        fig = px.box(df_q1, x="AI_Usage_Segment", y="GPA",
                     color="GPA_Type",
                     title="Q1: GPA Pre vs Post per Segmen Penggunaan AI",
                     category_orders={"AI_Usage_Segment": ["Ringan (0-5)", "Sedang (5-15)", "Berat (>15)"]})
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        df_q5 = df_f.melt(id_vars=["Primary_Use_Case"],
                          value_vars=["Pre_Semester_GPA", "Post_Semester_GPA"],
                          var_name="GPA_Type", value_name="GPA")
        df_q5["GPA_Type"] = df_q5["GPA_Type"].str.replace("_Semester_", " ").str.replace("_", " ")
        med_order = df_f.groupby("Primary_Use_Case")["Post_Semester_GPA"].median().sort_values().index.tolist()
        fig = px.box(df_q5, x="Primary_Use_Case", y="GPA",
                     color="GPA_Type", category_orders={"Primary_Use_Case": med_order},
                     title="Q5: GPA Pre vs Post per Tipe Penggunaan AI")
        fig.update_xaxes(tickangle=20)
        st.plotly_chart(fig, use_container_width=True)

    c3, _ = st.columns([1, 2])
    with c3:
        df_q7 = df_f.melt(id_vars=["Paid_Subscription"],
                          value_vars=["Pre_Semester_GPA", "Post_Semester_GPA"],
                          var_name="GPA_Type", value_name="GPA")
        df_q7["GPA_Type"] = df_q7["GPA_Type"].str.replace("_Semester_", " ").str.replace("_", " ")
        fig = px.box(df_q7, x="Paid_Subscription", y="GPA",
                     color="GPA_Type",
                     title="Q7: GPA Pre vs Post: Gratis vs Premium")
        st.plotly_chart(fig, use_container_width=True)

    # ── Delta (Post - Pre) ──
    st.markdown("---")
    st.subheader("Δ GPA (Post − Pre) per Kelompok")

    def make_delta_df(group_col):
        pivot = df_f.groupby(group_col).agg(
            Pre=("Pre_Semester_GPA", "mean"),
            Post=("Post_Semester_GPA", "mean"),
        ).round(3)
        pivot["Δ (Post−Pre)"] = (pivot["Post"] - pivot["Pre"]).round(3)
        return pivot.reset_index()

    d1, d2 = st.columns(2)
    with d1:
        delta_q1 = make_delta_df("AI_Usage_Segment")
        fig = px.bar(delta_q1, x="AI_Usage_Segment", y="Δ (Post−Pre)",
                     text_auto="+.3f", color="AI_Usage_Segment",
                     title="Δ GPA per Segmen Penggunaan AI",
                     category_orders={"AI_Usage_Segment": ["Ringan (0-5)", "Sedang (5-15)", "Berat (>15)"]})
        fig.update_traces(textposition="outside")
        st.plotly_chart(fig, use_container_width=True)
    with d2:
        delta_q5 = make_delta_df("Primary_Use_Case")
        delta_q5 = delta_q5.sort_values("Δ (Post−Pre)", ascending=False)
        fig = px.bar(delta_q5, x="Primary_Use_Case", y="Δ (Post−Pre)",
                     text_auto="+.3f", color="Primary_Use_Case",
                     title="Δ GPA per Tipe Penggunaan AI")
        fig.update_traces(textposition="outside")
        fig.update_xaxes(tickangle=20)
        st.plotly_chart(fig, use_container_width=True)

    d3, _ = st.columns([1, 2])
    with d3:
        delta_q7 = make_delta_df("Paid_Subscription")
        fig = px.bar(delta_q7, x="Paid_Subscription", y="Δ (Post−Pre)",
                     text_auto="+.3f", color="Paid_Subscription",
                     title="Δ GPA: Gratis vs Premium")
        fig.update_traces(textposition="outside")
        st.plotly_chart(fig, use_container_width=True)

    # ── Q6: Traditional Study Hours per Use Case ──
    st.markdown("---")
    st.subheader("Q6: Jam Belajar Tradisional vs GPA per Tipe Penggunaan AI")
    use_cases = sorted(df_f["Primary_Use_Case"].unique())
    cols = st.columns(min(len(use_cases), 5))
    for i, uc in enumerate(use_cases):
        sub = df_f[df_f["Primary_Use_Case"] == uc]
        r = sub["Traditional_Study_Hours"].corr(sub["Post_Semester_GPA"])
        with cols[i % 5]:
            fig = px.scatter(
                sub, x="Traditional_Study_Hours", y="Post_Semester_GPA",
                opacity=0.4, trendline="ols",
                trendline_color_override="#e74c3c",
                title=f"{uc}<br>r = {r:.3f}",
                height=400,
            )
            fig.update_traces(marker=dict(size=4, color="#2c3e50"), selector=dict(mode="markers"))
            fig.update_layout(title_font_size=12, margin=dict(l=10, r=10, t=40, b=10))
            st.plotly_chart(fig, use_container_width=True)

# ── Tab 3: Kesehatan Mental ────────────────────────────────
with tab3:
    st.header("Kesehatan Mental: Burnout & Kecemasan per Kebijakan")

    with st.expander("Apa artinya?", expanded=False):
        st.warning("Kebijakan Strict_Ban tidak menaikkan GPA, tapi membuat mahasiswa 19% lebih cemas saat ujian. Burnout paling dipengaruhi oleh jam AI yang tinggi dan rasa ketergantungan pada AI, bukan oleh bidang studi atau jenjang.")
        with st.expander("Detail Statistik"):
            st.markdown("""
            **Q3a: Institutional_Policy vs Post_Semester_GPA**  
            One-way ANOVA: F(2, 49997) = 6.83, p = 0.001, eta2 = 0.0003 (diabaikan)  
            Tukey HSD: Strict_Ban berbeda signifikan dari dua lainnya (selisih 0.02 poin).  
            Actively_Encouraged (M = 3.353) = Allowed_With_Citation (M = 3.353), Strict_Ban (M = 3.333)

            **Q3b: Institutional_Policy vs Anxiety**  
            One-way ANOVA: F(2, 49997) = 511.79, p = 0.000, eta2 = 0.020 (kecil)  
            Tukey HSD: Strict_Ban (M = 4.89) 0.77 poin lebih tinggi dari dua lainnya (M = 4.12)

            **Q4: Profil Burnout**  
            Chi-square Burnout vs Major: chi2(8) = 376.3, p = 0.000, Cramer V = 0.06 (lemah)  
            Chi-square Burnout vs Year: chi2(8) = 1424.2, p = 0.000, Cramer V = 0.12 (sedang)  
            ANOVA GenAI Hours vs Burnout: F(2, 49997) = 8067.4, p = 0.000, eta2 = 0.24 (BESAR)  
            Tukey HSD: semua grup berbeda signifikan  
            High M = 17.5, Medium M = 9.6, Low M = 6.9 jam per minggu  
            ANOVA Dependency vs Burnout: F(2, 49997) = 4279.9, p = 0.000, eta2 = 0.15 (BESAR)  
            Tukey HSD: semua grup berbeda signifikan  
            High M = 5.0, Medium M = 3.7, Low M = 3.2
            """)

    c1, c2 = st.columns(2)
    with c1:
        df_q3a = df_f.melt(id_vars=["Institutional_Policy"],
                           value_vars=["Pre_Semester_GPA", "Post_Semester_GPA"],
                           var_name="GPA_Type", value_name="GPA")
        df_q3a["GPA_Type"] = df_q3a["GPA_Type"].str.replace("_Semester_", " ").str.replace("_", " ")
        fig = px.box(df_q3a, x="Institutional_Policy", y="GPA",
                     color="GPA_Type",
                     title="Q3a: GPA Pre vs Post per Kebijakan Institusi")
        st.plotly_chart(fig, use_container_width=True)

        # Delta Q3a
        delta_q3a = df_f.groupby("Institutional_Policy").agg(
            Pre=("Pre_Semester_GPA", "mean"),
            Post=("Post_Semester_GPA", "mean"),
        ).round(3)
        delta_q3a["Δ (Post−Pre)"] = (delta_q3a["Post"] - delta_q3a["Pre"]).round(3)
        delta_q3a = delta_q3a.reset_index()
        fig = px.bar(delta_q3a, x="Institutional_Policy", y="Δ (Post−Pre)",
                     text_auto="+.3f", color="Institutional_Policy",
                     title="Δ GPA per Kebijakan Institusi")
        fig.update_traces(textposition="outside")
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig = px.box(df_f, x="Institutional_Policy", y="Anxiety_Level_During_Exams",
                     color="Institutional_Policy",
                     title="Q3b: Tingkat Kecemasan per Kebijakan Institusi")
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Q4: Profil Risiko Burnout")
    c1, c2, c3 = st.columns(3)
    with c1:
        ct = pd.crosstab(df_f["Major_Category"], df_f["Burnout_Risk_Level"], normalize="index") * 100
        fig = px.bar(ct.reset_index(), x="Major_Category", y=["Low", "Medium", "High"],
                     title="Burnout per Bidang Studi", barmode="stack")
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        ct2 = pd.crosstab(df_f["Year_of_Study"], df_f["Burnout_Risk_Level"], normalize="index") * 100
        fig = px.bar(ct2.reset_index(), x="Year_of_Study", y=["Low", "Medium", "High"],
                     title="Burnout per Jenjang Studi", barmode="stack",
                     category_orders={"Year_of_Study": ["Freshman","Sophomore","Junior","Senior","Graduate"]})
        st.plotly_chart(fig, use_container_width=True)
    with c3:
        ct3 = pd.crosstab(df_f["Institutional_Policy"], df_f["Burnout_Risk_Level"], normalize="index") * 100
        fig = px.bar(ct3.reset_index(), x="Institutional_Policy", y=["Low", "Medium", "High"],
                     title="Burnout per Kebijakan", barmode="stack")
        st.plotly_chart(fig, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        fig = px.box(df_f, x="Burnout_Risk_Level", y="Weekly_GenAI_Hours",
                     color="Burnout_Risk_Level",
                     title="Q4: Jam AI per Tingkat Burnout",
                     category_orders={"Burnout_Risk_Level": ["Low", "Medium", "High"]})
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig = px.box(df_f, x="Burnout_Risk_Level", y="Perceived_AI_Dependency",
                     color="Burnout_Risk_Level",
                     title="Q4: Ketergantungan AI per Tingkat Burnout",
                     category_orders={"Burnout_Risk_Level": ["Low", "Medium", "High"]})
        st.plotly_chart(fig, use_container_width=True)

# ── Tab 4: Retensi Pengetahuan ─────────────────────────────
with tab4:
    st.header("Retensi Pengetahuan: Korelasi dengan Ketergantungan AI")

    with st.expander("Apa artinya?", expanded=False):
        st.warning("Semakin tinggi ketergantungan mahasiswa pada AI, semakin rendah skor retensi pengetahuannya. Efeknya kecil tapi konsisten. Mahasiswa dengan ketergantungan tinggi perlu intervensi pengembangan kemandirian belajar.")
        with st.expander("Detail Statistik"):
            st.markdown("""
            **Q2: Perceived_AI_Dependency vs Skill_Retention_Score**  
            Spearman ρ = -0.0843, p = 0.000, ρ² = 0.007 (kecil)  
            Signifikan dengan Bonferroni correction (alpha = 0.05/7).  
            Hanya 0.7% varians Skill_Retention dijelaskan oleh Perceived_AI_Dependency.  
            Boxplot: Low dependency (M = 77.8), Medium (M = 75.0), High (M = 72.9).  
            *(Menggunakan Spearman karena Perceived_AI_Dependency adalah integer/ordinal.)*
            """)

    c1, c2 = st.columns(2)
    with c1:
        df_q2 = df_f.copy()
        df_q2["Perceived_AI_Dependency"] = df_q2["Perceived_AI_Dependency"].astype(str)
        fig = px.box(df_q2, x="Perceived_AI_Dependency", y="Skill_Retention_Score",
                     color="Perceived_AI_Dependency",
                     color_discrete_sequence=px.colors.sequential.RdBu_r,
                     title="Q2: Ketergantungan AI vs Skor Retensi Keahlian")
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig = px.box(df_f, x="Dependency_Level", y="Skill_Retention_Score",
                     color="Dependency_Level",
                     title="Q2: Retensi per Tingkat Ketergantungan",
                     category_orders={"Dependency_Level": ["Rendah (1-3)", "Sedang (4-7)", "Tinggi (8-10)"]})
        st.plotly_chart(fig, use_container_width=True)

# ── Tab 5: Profil Risiko ────────────────────────────────────
with tab5:
    st.header("Profil Risiko: Segmentasi AI Dependency × Burnout")

    with st.expander("Apa artinya?", expanded=False):
        st.error("Mahasiswa dengan penggunaan AI berat (>15 jam/minggu) jauh lebih rentan terkena burnout: 64,8% di antaranya masuk kategori Burnout High, dibanding hanya 10,5% pada pengguna ringan. Sebaliknya, segmen Sedang (5-15 jam/minggu) justru menunjukkan profil paling optimal dengan GPA dan retensi keahlian tertinggi di antara ketiga segmen. Semakin tinggi intensitas AI, semakin besar risiko burnout tanpa peningkatan GPA yang berarti.")

    # ── Stacked bar: AI_Usage_Segment × Burnout ──
    st.subheader("Burnout per Segmen Penggunaan AI")
    burnout_order = ["Low", "Medium", "High"]
    ct_seg = pd.crosstab(df_f["AI_Usage_Segment"], df_f["Burnout_Risk_Level"], normalize="index") * 100
    ct_seg = ct_seg.reindex(["Ringan (0-5)", "Sedang (5-15)", "Berat (>15)"], columns=burnout_order)
    fig = px.bar(ct_seg.reset_index(), x="AI_Usage_Segment", y=burnout_order,
                 title="Proporsi Burnout per Segmen AI", barmode="stack",
                 color_discrete_sequence=["#2ecc71", "#f1c40f", "#e74c3c"])
    fig.update_layout(legend_title="Burnout Risk", yaxis_title="Persentase (%)")
    st.plotly_chart(fig, use_container_width=True)

    # ── GPA & Retensi per Segmen ──
    st.subheader("Metrik Outcome per Segmen Penggunaan AI")
    c1, c2 = st.columns(2)
    with c1:
        seg_order = ["Ringan (0-5)", "Sedang (5-15)", "Berat (>15)"]
        seg_gpa = df_f.groupby("AI_Usage_Segment").agg(
            Pre=("Pre_Semester_GPA", "mean"),
            Post=("Post_Semester_GPA", "mean"),
        ).reindex(seg_order).round(3).reset_index()
        seg_gpa_melt = seg_gpa.melt(id_vars=["AI_Usage_Segment"],
                                     value_vars=["Pre", "Post"],
                                     var_name="GPA_Type", value_name="GPA")
        fig = px.bar(seg_gpa_melt, x="AI_Usage_Segment", y="GPA",
                     color="GPA_Type", barmode="group", text_auto=".3f",
                     title="Rata-rata GPA Pre vs Post per Segmen AI",
                     category_orders={"AI_Usage_Segment": seg_order})
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        seg_skill = df_f.groupby("AI_Usage_Segment")["Skill_Retention_Score"].mean().reindex(seg_order).round(1)
        fig = px.bar(seg_skill.reset_index(), x="AI_Usage_Segment", y="Skill_Retention_Score",
                     color="AI_Usage_Segment", text_auto=".1f",
                     title="Rata-rata Retensi Keahlian per Segmen AI",
                     category_orders={"AI_Usage_Segment": seg_order})
        st.plotly_chart(fig, use_container_width=True)

st.caption(f"Baris setelah filter: {len(df_f):,} / {len(df):,}")
