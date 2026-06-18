import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ==============================================================================
# 1. CẤU HÌNH TRANG & GIAO DIỆN CHUNG (UI/UX TỐI ƯU)
# ==============================================================================
st.set_page_config(
    page_title="CS AI Agent Analysis Dashboard", 
    layout="wide", 
    initial_sidebar_state="expanded",
    page_icon="🤖"
)

# Tùy chỉnh CSS tạo điểm nhấn chuyên nghiệp cho thẻ Metric
st.markdown("""
    <style>
    .main .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
    h1 { color: #1E3A8A; font-weight: 700; margin-bottom: 0px; }
    h2 { color: #0F172A; border-left: 5px solid #2563EB; padding-left: 12px; margin-top: 20px; }
    div[data-testid="metric-container"] {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        transition: transform 0.2s;
    }
    div[data-testid="metric-container"]:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 15px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

# TỪ ĐIỂN DỊCH CHUẨN HÓA (Dùng chung cho toàn hệ thống)
freq_map = {
    'Daily': 'Hằng ngày',
    'Weekly': 'Hằng tuần',
    'Monthly': 'Hằng tháng',
    'Yearly': 'Hằng năm',
    'Never': 'Không dùng'
}
freq_order = ['Không dùng', 'Hằng năm', 'Hằng tháng', 'Hằng tuần', 'Hằng ngày']

# ==============================================================================
# 2. HÀM ĐỌC VÀ LÀM SẠCH DỮ LIỆU TỪ 4 FILE
# ==============================================================================
@st.cache_data
def load_data():
    try:
        df_meta = pd.read_csv("domain_worker_metadata.csv")
        df_desire = pd.read_csv("domain_worker_desires.csv")
        df_expert = pd.read_csv("expert_rated_technological_capability.csv")
        df_task = pd.read_csv("task_statement_with_metadata.csv")
        
        # Làm sạch khoảng trắng trong tên cột
        for df in [df_meta, df_desire, df_expert, df_task]:
            df.columns = df.columns.str.strip()
        
        # Từ khóa lọc nhóm ngành CNTT / Khoa học máy tính
        keywords = 'Computer|Software|Developer|Programmer|Database|Network|Security|Data Analyst|Information Systems'
        
        cs_meta = df_meta[df_meta['Occupation (O*NET-SOC Title)'].str.contains(keywords, case=False, na=False)]
        cs_desire = df_desire[df_desire['Occupation (O*NET-SOC Title)'].str.contains(keywords, case=False, na=False)]
        cs_expert = df_expert[df_expert['Occupation (O*NET-SOC Title)'].str.contains(keywords, case=False, na=False)]
        cs_task = df_task[df_task['Occupation (O*NET-SOC Title)'].str.contains(keywords, case=False, na=False)]
        
        return cs_meta, cs_desire, cs_expert, cs_task, None
    except Exception as e:
        return None, None, None, None, str(e)

cs_meta, cs_desire, cs_expert, cs_task, error_msg = load_data()

# ==============================================================================
# 3. THIẾT KẾ SIDEBAR (THANH ĐIỀU HƯỚNG & BỘ LỌC ĐỘNG)
# ==============================================================================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2103/2103284.png", width=70)
    st.title("Menu Hệ Thống")
    st.markdown("---")
    
    page = st.radio(
        "ĐIỀU HƯỚNG BÁO CÁO:",
        [
            "📊 1. Thực trạng Sử dụng AI", 
            "💡 2. Nhu cầu Tự động hóa", 
            "🧠 3. Đánh giá từ Chuyên gia",
            "🧩 4. Cấu trúc Tác vụ (Đặc tả)"
        ],
        index=0
    )
    st.markdown("---")
    
    if not error_msg:
        st.subheader("⚙️ Bộ lọc Vị trí (Chuyên sâu)")
        all_occupations = sorted(list(set(cs_meta['Occupation (O*NET-SOC Title)'].dropna().unique())))
        selected_jobs = st.multiselect(
            "Phân tích theo chức danh:",
            options=all_occupations,
            default=[],
            placeholder="Để trống = Hiện tất cả"
        )
        
        # Lọc dữ liệu theo tùy chọn
        jobs_to_filter = selected_jobs if selected_jobs else all_occupations
        filtered_meta = cs_meta[cs_meta['Occupation (O*NET-SOC Title)'].isin(jobs_to_filter)]
        filtered_desire = cs_desire[cs_desire['Occupation (O*NET-SOC Title)'].isin(jobs_to_filter)]
        filtered_expert = cs_expert[cs_expert['Occupation (O*NET-SOC Title)'].isin(jobs_to_filter)]
        filtered_task = cs_task[cs_task['Occupation (O*NET-SOC Title)'].isin(jobs_to_filter)]
    
    st.markdown("---")
    st.caption("Dữ liệu: WorkBank & O*NET Database.")

# ==============================================================================
# 4. NỘI DUNG CHÍNH CỦA BÁO CÁO
# ==============================================================================
if error_msg:
    st.error(f"❌ Lỗi đọc file: {error_msg}. Đảm bảo 4 file CSV đang ở cùng thư mục với app.py.")
    st.stop()

st.title("💻 Báo cáo Ứng dụng AI Agent (Khoa học Máy tính)")
if len(jobs_to_filter) == len(all_occupations):
    st.markdown("*Phạm vi dữ liệu: Toàn bộ nhóm ngành Khoa học máy tính & CNTT*")
else:
    st.markdown(f"*Phạm vi dữ liệu: **{len(jobs_to_filter)}** vị trí chuyên môn đã chọn*")
st.markdown("---")

# --------------------------------------------------------------------------
# TRANG 1: THỰC TRẠNG SỬ DỤNG AI
# --------------------------------------------------------------------------
if page == "📊 1. Thực trạng Sử dụng AI":
        st.header("Tần suất nhân sự IT sử dụng LLM/AI vào công việc")
        
        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("Tổng lượng nhân sự khảo sát", f"{len(filtered_meta)} người")
        col_m2.metric("Số lượng chức danh IT", filtered_meta['Occupation (O*NET-SOC Title)'].nunique())
        
        # Tính tỷ lệ người dùng AI thường xuyên (Daily/Weekly)
        if 'LLM Use in Work' in filtered_meta.columns:
            ai_users = len(filtered_meta[filtered_meta['LLM Use in Work'].str.contains('Weekly|Daily', case=False, na=False)])
            ai_rate = (ai_users / len(filtered_meta)) * 100 if len(filtered_meta) > 0 else 0
            col_m3.metric("Tỷ lệ sử dụng AI mức cao", f"{ai_rate:.1f}%", "Sử dụng hàng tuần/hàng ngày")
            
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        
        def plot_llm_usage(df, column_name, title_text, color_scale):
            if column_name in df.columns and not df.empty:
                counts = df[column_name].value_counts().reset_index()
                counts.columns = ['Mức độ', 'Số lượng']
                fig = px.bar(counts, x='Số lượng', y='Mức độ', orientation='h',
                             color='Số lượng', color_continuous_scale=color_scale, text_auto=True)
                fig.update_layout(title=title_text, showlegend=False, coloraxis_showscale=False, 
                                  height=300, yaxis={'categoryorder':'total ascending'})
                return fig
            return None

        with col1:
            fig1 = plot_llm_usage(filtered_meta, 'LLM Usage by Type - Coding', "Coding", 'Blues')
            if fig1: st.plotly_chart(fig1, use_container_width=True)
        with col2:
            fig2 = plot_llm_usage(filtered_meta, 'LLM Usage by Type - System Design', "System Design", 'Tealgrn')
            if fig2: st.plotly_chart(fig2, use_container_width=True)
        with col3:
            fig3 = plot_llm_usage(filtered_meta, 'LLM Usage by Type - Data Processing', "Data Processing", 'Purples')
            if fig3: st.plotly_chart(fig3, use_container_width=True)
# --------------------------------------------------------------------------
# TRANG 2: NHU CẦU TỰ ĐỘNG HÓA
# --------------------------------------------------------------------------
elif page == "💡 2. Nhu cầu Tự động hóa":
    st.header("Tâm lý & Khao khát Tự động hóa của Kỹ sư")
    
    if not filtered_desire.empty:
        st.subheader("📊 Mật độ Phân bố Điểm Khao khát Tự động hóa")
        st.markdown("*Biểu đồ cho thấy phần lớn các tác vụ của kỹ sư đang tập trung ở mức độ muốn giao cho AI là bao nhiêu điểm.*")
        fig_hist = px.histogram(filtered_desire, x='Automation Desire Rating', 
                                nbins=20, marginal='box', color_discrete_sequence=['#EF4444'])
        fig_hist.update_layout(height=350, yaxis_title="Số lượng Tác vụ", xaxis_title="Điểm Khao khát (1 - 5)")
        st.plotly_chart(fig_hist, use_container_width=True)

        st.markdown("---")
        task_stats = filtered_desire.groupby('Task')[['Automation Desire Rating', 'Enjoyment Rating']].mean().reset_index()
        top_tasks = task_stats.sort_values(by='Automation Desire Rating', ascending=False).head(10)
        
        col_a, col_b = st.columns([1, 1.2])
        with col_a:
            st.subheader("🔥 Top 10 Tác vụ muốn 'đẩy' cho AI")
            fig_bar = px.bar(top_tasks, x='Automation Desire Rating', y='Task', orientation='h',
                             color='Automation Desire Rating', color_continuous_scale='Reds')
            fig_bar.update_layout(yaxis={'categoryorder':'total ascending'}, height=450, coloraxis_showscale=False, xaxis_title="Điểm Khao khát")
            st.plotly_chart(fig_bar, use_container_width=True)
        
        with col_b:
            st.subheader("📉 Tương quan: Khao khát vs Sự thích thú")
            st.markdown("*Quy luật: Tác vụ làm càng chán (Đường gạch ngang thấp) -> Nhu cầu ném cho AI càng cao (Đường đỏ cao).*")
            fig_line = go.Figure()
            fig_line.add_trace(go.Scatter(x=top_tasks['Task'], y=top_tasks['Automation Desire Rating'],
                                          mode='lines+markers', name='Mong muốn Tự động hóa', line=dict(color='#DC2626', width=3)))
            fig_line.add_trace(go.Scatter(x=top_tasks['Task'], y=top_tasks['Enjoyment Rating'],
                                          mode='lines+markers', name='Sự thích thú khi làm', line=dict(color='#10B981', width=3, dash='dash')))
            fig_line.update_layout(xaxis_tickangle=-25, height=450, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
            st.plotly_chart(fig_line, use_container_width=True)

# --------------------------------------------------------------------------
# TRANG 3: ĐÁNH GIÁ CHUYÊN GIA
# --------------------------------------------------------------------------
elif page == "🧠 3. Đánh giá từ Chuyên gia":
    st.header("Đánh giá Năng lực Kỹ thuật Thực tế của AI Agent")
    
    if not filtered_expert.empty:
        expert_stats = filtered_expert.groupby('Task')[['Automation Capacity Rating', 'Human Agency Scale Rating']].mean().reset_index()
        
        st.subheader("📍 Ma trận Phân Vị (Scatter Plot): Năng lực AI vs Sự kiểm soát")
        st.markdown("*Lưu ý: Góc dưới bên phải (Điểm Năng lực > 3.0 & Mức Can thiệp < 2.5) là điểm 'ngọt' nhất để tạo Agent tự trị 100%.*")
        
        fig_scatter = px.scatter(expert_stats, x='Automation Capacity Rating', y='Human Agency Scale Rating',
                                 hover_name='Task', color='Automation Capacity Rating', 
                                 color_continuous_scale='Viridis', size_max=12,
                                 labels={'Automation Capacity Rating': 'Năng lực AI (Capacity)',
                                         'Human Agency Scale Rating': 'Mức độ Can thiệp (Human Agency)'})
        # Thêm 2 đường line chéo chia vùng chiến lược
        fig_scatter.add_shape(type="line", x0=3.0, y0=0, x1=3.0, y1=5, line=dict(color="#EF4444", dash="dash"))
        fig_scatter.add_shape(type="line", x0=0, y0=2.5, x1=5, y1=2.5, line=dict(color="#EF4444", dash="dash"))
        fig_scatter.update_layout(height=450)
        st.plotly_chart(fig_scatter, use_container_width=True)
        
        st.markdown("---")
        st.subheader("📊 Khả năng AI vs Yêu cầu Giám sát (Top 10 Tác vụ mạnh nhất của AI)")
        top_capacity = expert_stats.sort_values(by='Automation Capacity Rating', ascending=False).head(10)
        
        fig_grouped = go.Figure()
        fig_grouped.add_trace(go.Bar(x=top_capacity['Task'], y=top_capacity['Automation Capacity Rating'],
                                     name='Năng lực giải quyết của AI', marker_color='#8B5CF6'))
        fig_grouped.add_trace(go.Bar(x=top_capacity['Task'], y=top_capacity['Human Agency Scale Rating'],
                                     name='Yêu cầu con người giám sát', marker_color='#F59E0B'))
        
        fig_grouped.update_layout(barmode='group', xaxis_tickangle=-30, height=450, 
                                  legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        st.plotly_chart(fig_grouped, use_container_width=True)

# --------------------------------------------------------------------------
# TRANG 4: CẤU TRÚC TÁC VỤ
# --------------------------------------------------------------------------
elif page == "🧩 4. Cấu trúc Tác vụ (Đặc tả)":
    st.header("Bản đồ Đặc tả Tác vụ Ngành Khoa học Máy tính")
    st.markdown("Khai phá dữ liệu cấu trúc ngành để xác định trọng tâm số lượng đầu việc của các Kỹ sư.")
    
    if not filtered_task.empty:
        st.subheader("🌳 Treemap: Khối lượng Tác vụ theo Chức danh")
        st.markdown("*Mỗi khối hình đại diện cho quy mô khối lượng công việc đặc thù phải xử lý của từng chức danh.*")
        
        task_counts = filtered_task['Occupation (O*NET-SOC Title)'].value_counts().reset_index()
        task_counts.columns = ['Chức danh', 'Số lượng Tác vụ']
        
        fig_tree = px.treemap(task_counts, path=['Chức danh'], values='Số lượng Tác vụ',
                              color='Số lượng Tác vụ', color_continuous_scale='Blues')
        fig_tree.update_layout(height=500, margin=dict(t=20, l=0, r=0, b=0))
        st.plotly_chart(fig_tree, use_container_width=True)
        
        st.markdown("---")
        st.subheader("📋 Bảng Tra cứu Tác vụ Chi tiết")
        st.dataframe(filtered_task[['Occupation (O*NET-SOC Title)', 'Task']].drop_duplicates().reset_index(drop=True), use_container_width=True)
    else:
        st.warning("Không có dữ liệu đặc tả tác vụ cho lựa chọn này.")
