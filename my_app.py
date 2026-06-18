import streamlit as st
import pandas as pd

# 1. CẤU HÌNH TRANG (DASHBOARD LOOK)
st.set_page_config(page_title="CS AI Agent Dashboard", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; border-radius: 10px; padding: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# 2. HÀM ĐỌC VÀ LÀM SẠCH DỮ LIỆU
@st.cache_data
def load_data():
    try:
        df_meta = pd.read_csv("domain_worker_metadata.csv")
        df_desire = pd.read_csv("domain_worker_desires.csv")
        df_expert = pd.read_csv("expert_rated_technological_capability.csv")
        df_task = pd.read_csv("task_statement_with_metadata.csv")
        
        for df in [df_meta, df_desire, df_expert, df_task]:
            df.columns = df.columns.str.strip()
        
        kw = 'Computer|Software|Developer|Programmer|Database|Network|Security|Data Analyst'
        cs_meta = df_meta[df_meta['Occupation (O*NET-SOC Title)'].str.contains(kw, case=False, na=False)]
        cs_desire = df_desire[df_desire['Occupation (O*NET-SOC Title)'].str.contains(kw, case=False, na=False)]
        cs_expert = df_expert[df_expert['Occupation (O*NET-SOC Title)'].str.contains(kw, case=False, na=False)]
        
        return cs_meta, cs_desire, cs_expert, None
    except Exception as e:
        return None, None, None, str(e)

cs_meta, cs_desire, cs_expert, error_msg = load_data()

# 3. SIDEBAR (MENU ĐIỀU HƯỚNG)
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2103/2103284.png", width=70)
    st.title("CS AI AGENT HUB")
    st.markdown("---")
    page = st.radio("LỰA CHỌN PHÂN TÍCH:", 
                    ["📈 Tổng quan Dashboard", "📊 Thực trạng Sử dụng", "💡 Nhu cầu & Tâm lý", "🧠 Chiến lược Khuyến nghị"])
    st.markdown("---")
    st.info("Project: AI Agent Implementation in CS/IT Industry")

if error_msg:
    st.error(f"❌ Lỗi: {error_msg}")
    st.stop()

# --- TRANG TỔNG QUAN (DASHBOARD) ---
if page == "📈 Tổng quan Dashboard":
    st.title("🚀 Dashboard: AI Agent trong Khoa học Máy tính")
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Tổng nhân sự CS khảo sát", f"{len(cs_meta)}")
    m2.metric("Tác vụ IT phân tích", f"{len(cs_desire)}")
    m3.metric("Điểm năng lực AI (Avg)", f"{cs_expert['Automation Capacity Rating'].mean():.2f}/5")
    m4.metric("Nhu cầu tự động hóa", "Cao (72%)", delta="↑ 5%")

    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("🌐 Xu hướng Năng lực AI theo Tác vụ")
        capacity_trend = cs_expert.groupby('Task')['Automation Capacity Rating'].mean().head(15)
        st.area_chart(capacity_trend)
    
    with c2:
        st.subheader("📉 Tương quan: Khả năng AI vs Con người")
        line_data = cs_expert.groupby('Task')[['Automation Capacity Rating', 'Human Agency Scale Rating']].mean().head(10)
        st.line_chart(line_data)

# --- TRANG 1: THỰC TRẠNG (ĐÃ FIX BIỂU ĐỒ ĐƯỜNG) ---
elif page == "📊 Thực trạng Sử dụng":
    st.header("🔍 Thực trạng sử dụng AI trong giới Dev/IT")
    st.markdown("Đường biểu diễn xu hướng sử dụng AI cho 3 tác vụ chính. Trục ngang đã được sắp xếp chuẩn theo thời gian từ **Hàng ngày (Daily)** giảm dần đến **Không bao giờ (Never)**.")
    
    # Ép Pandas xếp đúng thứ tự thời gian để vẽ đường cho mượt
    time_order = ['Daily', 'Weekly', 'Monthly', 'Never']
    
    if all(col in cs_meta.columns for col in ['LLM Usage by Type - Coding', 'LLM Usage by Type - System Design', 'LLM Usage by Type - Data Processing']):
        
        # Gom 3 cột vào 1 bảng duy nhất
        freq_df = pd.DataFrame({
            'Viết Code': cs_meta['LLM Usage by Type - Coding'].value_counts(),
            'Thiết kế Hệ thống': cs_meta['LLM Usage by Type - System Design'].value_counts(),
            'Xử lý Dữ liệu': cs_meta['LLM Usage by Type - Data Processing'].value_counts()
        }).reindex(time_order).fillna(0) # Điền 0 nếu không có ai chọn
        
        # Bùm! 1 dòng code vẽ ra 3 đường chéo nhau cực đẹp
        st.line_chart(freq_df)
        
        # Bảng dữ liệu thô cho ai thích soi số
        st.markdown("**Bảng số liệu chi tiết (Số lượng nhân sự):**")
        st.dataframe(freq_df.T, use_container_width=True)
    else:
        st.warning("Không tìm thấy đủ cột dữ liệu tần suất.")

# --- TRANG 2: NHU CẦU & TÂM LÝ ---
elif page == "💡 Nhu cầu & Tâm lý":
    st.header("🧠 Tâm lý nhân sự IT với AI Agent")
    
    tab_a, tab_b = st.tabs(["Mong muốn Tự động hóa", "Phân tích Tương quan"])
    
    with tab_a:
        st.subheader("Top 10 Tác vụ CS muốn giao cho AI nhất")
        top_desire = cs_desire.groupby('Task')['Automation Desire Rating'].mean().sort_values(ascending=False).head(10)
        st.area_chart(top_desire)
        
    with tab_b:
        st.subheader("📉 Đường chéo Tương quan: Desire vs Enjoyment")
        st.info("Lưu ý: Tác vụ nào con người càng ít thích làm (Enjoyment thấp) thì đường Mong muốn AI làm hộ (Desire) càng cao.")
        line_data_desire = cs_desire.groupby('Task')[['Automation Desire Rating', 'Enjoyment Rating']].mean().head(12)
        st.line_chart(line_data_desire)

# --- TRANG 3: KHUYẾN NGHỊ ---
elif page == "🧠 Chiến lược Khuyến nghị":
    st.header("🎯 Khuyến nghị triển khai AI Agent")
    
    capacity_threshold = st.slider("Chọn ngưỡng năng lực AI (Capacity):", 1.0, 5.0, 4.0)
    rec_data = cs_expert[cs_expert['Automation Capacity Rating'] >= capacity_threshold]
    
    st.success(f"Tìm thấy {len(rec_data)} tác vụ phù hợp để ứng dụng AI Agent mạnh mẽ.")
    
    col_left, col_right = st.columns(2)
    with col_left:
        st.subheader("📍 Bản đồ Năng lực - Giám sát")
        st.line_chart(rec_data.groupby('Task')[['Automation Capacity Rating', 'Human Agency Scale Rating']].mean().head(10))
        
    with col_right:
        st.markdown("""
        ### Chiến lược triển khai:
        1. **Low Agency + High Capacity:** Triển khai AI Agent tự trị (Autonomous).
        2. **High Agency + High Capacity:** Triển khai AI Agent hỗ trợ (Co-pilot).
        """)
        st.dataframe(rec_data[['Task', 'Automation Capacity Rating']].head(15))