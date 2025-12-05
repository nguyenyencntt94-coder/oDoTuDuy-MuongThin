import streamlit as st
import graphviz
import google.generativeai as genai

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(
    page_title="Sơ Đồ Tư Duy - THCS Mường Thín",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. CSS GIAO DIỆN (ĐÃ TỐI ƯU) ---
st.markdown("""
<style>
    /* Header trường học */
    .school-header {
        font-family: 'Arial', sans-serif;
        color: #1565C0;
        text-align: center;
        font-size: 36px;
        font-weight: bold;
        padding: 20px 0 5px 0;
        text-transform: uppercase;
        text-shadow: 1px 1px 2px #cccccc;
    }
    
    /* Dòng chữ tạo sơ đồ AI */
    .ai-header {
        text-align: center;
        color: #FF4B4B;
        font-weight: bold;
        font-size: 20px;
        margin-bottom: 10px;
        text-transform: uppercase;
        animation: blink 2s infinite;
    }

    /* Nút bấm chính */
    .stButton button {
        background-image: linear-gradient(to right, #1E88E5, #42A5F5);
        color: white;
        font-weight: bold;
        border-radius: 8px;
        height: 50px;
        width: 100%;
        border: none;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .stButton button:hover {
        transform: scale(1.02);
    }

    /* Footer */
    .footer {
        position: fixed; left: 0; bottom: 0; width: 100%;
        background-color: #f8f9fa; color: #666;
        text-align: center; padding: 10px; font-size: 13px;
        border-top: 1px solid #ddd;
        z-index: 100;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. HIỂN THỊ HEADER ---
st.markdown('<div class="school-header">TRƯỜNG THCS MƯỜNG THÍN</div>', unsafe_allow_html=True)
st.markdown('<p style="text-align:center; color:#555; font-style:italic;">Ứng dụng hỗ trợ dạy và học tích hợp Trí tuệ nhân tạo (AI)</p>', unsafe_allow_html=True)

# --- 4. SIDEBAR THÔNG MINH ---
with st.sidebar:
    st.header("⚙️ Bảng Điều Khiển")
    api_key = st.text_input("🔑 Nhập Google API Key:", type="password")
    
    # Tự động quét Model
    available_models = []
    if api_key:
        try:
            genai.configure(api_key=api_key)
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    available_models.append(m.name)
        except: pass
            
    if available_models:
        model_choice = st.selectbox("🤖 Chọn Model AI:", available_models, index=0)
        st.success(f"✅ Đã kết nối: {len(available_models)} model")
    else:
        model_choice = "models/gemini-1.5-flash" # Mặc định dự phòng
        if not api_key:
            st.info("👉 Vui lòng nhập Key để bắt đầu.")

    st.divider()
    style_option = st.selectbox("🎨 Phong cách vẽ:", ["Học sinh (Màu sắc)", "Đơn giản (Trắng đen)", "Chuyên nghiệp (Xanh)"])

# --- 5. HÀM XỬ LÝ AI ---
def get_mindmap_code(text, style, model_name):
    style_config = ""
    if style == "Học sinh (Màu sắc)":
        style_config = 'node [style="filled", fillcolor="yellow:cyan:orange", gradientangle=270, fontname="Arial", penwidth=0]; edge [color="#666"];'
    elif style == "Chuyên nghiệp (Xanh)":
        style_config = 'node [style="filled", fillcolor="#E1F5FE", color="#0277BD", fontcolor="#01579B", shape="box", fontname="Arial"]; edge [color="#0277BD"];'
    else:
        style_config = 'node [shape=ellipse, fontname="Arial"];'

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name) 
    
    prompt = f"""
    Tạo code Graphviz DOT từ văn bản: "{text}".
    YÊU CẦU: Chỉ trả về code thuần. KHÔNG Markdown.
    Cấu trúc: digraph G {{ rankdir=LR; fontname="Arial"; {style_config} ... }}
    Nội dung node thật ngắn gọn.
    """
    response = model.generate_content(prompt)
    return response.text.replace("```dot", "").replace("```", "").strip()

# --- 6. GIAO DIỆN CHÍNH ---
col1, col2 = st.columns([1, 1.5], gap="large")

with col1:
    st.markdown("### 📝 Nhập nội dung bài học")
    input_text = st.text_area("", height=350, placeholder="Dán văn bản vào đây...\nVí dụ: Các loại câu trong Tiếng Việt...")
    
    # Dòng chữ bạn yêu cầu
    st.markdown('<div class="ai-header">✨ TẠO SƠ ĐỒ TƯ DUY AI ✨</div>', unsafe_allow_html=True)
    
    btn = st.button("BẤM VÀO ĐÂY ĐỂ VẼ")

with col2:
    st.markdown("### 🖼️ Kết quả Sơ đồ")
    
    if btn:
        if not api_key:
            st.error("⚠️ Chưa nhập API Key!")
        elif not input_text:
            st.warning("⚠️ Chưa nhập nội dung!")
        else:
            with st.spinner(f"AI đang vẽ..."):
                try:
                    # 1. Lấy code từ AI
                    dot_code = get_mindmap_code(input_text, style_option, model_choice)
                    
                    # 2. Vẽ hình lên web
                    st.graphviz_chart(dot_code, use_container_width=True)
                    st.balloons()
                    
                    # 3. Tạo nút tải về (Ẩn code đi, chỉ hiện nút này)
                    try:
                        source = graphviz.Source(dot_code)
                        png_data = source.pipe(format='png')
                        
                        st.download_button(
                            label="⬇️ TẢI SƠ ĐỒ VỀ MÁY (PNG)",
                            data=png_data,
                            file_name="sodo_muongthin.png",
                            mime="image/png"
                        )
                    except Exception as e:
                        st.warning("Đã vẽ xong! (Chức năng tải về cần cài đặt Graphviz trên máy chủ).")
                    
                except Exception as e:
                    st.error(f"Lỗi: {e}")

# Footer
st.markdown('<div class="footer">© 2024 Trường THCS Mường Thín - Công nghệ 4.0</div>', unsafe_allow_html=True)