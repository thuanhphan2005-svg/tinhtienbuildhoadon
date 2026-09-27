import os
from datetime import datetime
import pandas as pd
import streamlit as st
st.set_page_config(page_title="Order Nhà Hàng", layout="wide")

# Đường dẫn file dữ liệu dùng chung trên máy chủ
CSV_FILE = "history.csv"

# Thực đơn cố định của nhà hàng Mr. Bình
menu = {
    "Đồ ăn": {
        "Pizza Hải Sản": 150000,"Pizza cá": 500000,
        "Mì Ý Bò Bằm": 95000,"GÀ CHIÊN MẮM TỎI":29000,
        "Burger Gà": 35000,
        "Bít tết Bò Mỹ": 250000,
        "Sườn nướng BBQ": 150000,
        "Cánh gà chiên mắm": 75000,
        "Lẩu cá diêu hồng": 200000,
        "Lẩu Thái hải sản": 300000,
    },
    "Thức uống": {
        "Coca Cola": 20000,
        "Trà sữa SV": 70000,
        "Trà Đào Cam Sả": 35000,
        "Cà Phê Sữa": 25000,
        "Nước Suối": 10000,
        "Sinh tố Bơ": 45000,
        "Nước ép cam": 40000,
        "Mojito chanh dây": 55000,
        "Bia Heineken": 30000,
    },
}

if "order_dict" not in st.session_state:
    st.session_state.order_dict = {}

# Tự động tải dữ liệu lịch sử cũ từ file CSV lên hệ thống khi khởi động ứng dụng
if "history" not in st.session_state:
    if os.path.exists(CSV_FILE):
        try:
            # Đọc file CSV lưu trữ chung
            df_loaded = pd.read_csv(CSV_FILE)
            # Chuyển đổi ngược lại thành danh sách dict để duy trì tính nhất quán của code
            st.session_state.history = df_loaded.to_dict(orient="records")
        except Exception:
            st.session_state.history = []
    else:
        st.session_state.history = []

if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False

# Thanh điều hướng dạng RADIO hiển thị trực diện ngay trên Sidebar
page = st.sidebar.radio("📋 Chọn trang hệ thống", ["🍽️ Order", "🔑 Admin"])

if page == "🍽️ Order":
    st.title("🍽️ Hệ thống Order Nhà Hàng_Dr Thuận")
    st.caption("Ghi nhận order nhanh chóng và chính xác theo thời gian thực")

    col1, col2 = st.columns([1, 1.3])

    with col1:
        st.subheader("Chọn Món")
        table_number = st.selectbox(
            "🪑 Chọn số bàn", [f"Bàn {i}" for i in range(1, 21)]
        )
        category = st.selectbox("Chọn loại:", list(menu.keys()))
        item = st.selectbox("Chọn món:", list(menu[category].keys()))
        quantity = st.number_input("Số lượng:", min_value=1, step=1, value=1)

        if st.button("Thêm vào giỏ"):
            price = menu[category][item]

            if item in st.session_state.order_dict:
                st.session_state.order_dict[item]["Số lượng"] += quantity
                st.session_state.order_dict[item]["Thành tiền"] = (
                    st.session_state.order_dict[item]["Số lượng"] * price
                )
                st.session_state.order_dict[item]["Bàn"] = table_number
            else:
                st.session_state.order_dict[item] = {
"Bàn": table_number,
                    "Tên món": item,
                    "Đơn giá": price,
                    "Số lượng": quantity,
                    "Thành tiền": price * quantity,
                }
            st.success(f"Đã thêm {item} vào giỏ!")
            st.rerun()

    with col2:
        st.subheader("Giỏ hàng hiện tại")

        if st.session_state.order_dict:
            df = pd.DataFrame.from_dict(
                st.session_state.order_dict, orient="index"
            )
            st.table(
                df[["Bàn", "Tên món", "Đơn giá", "Số lượng", "Thành tiền"]]
            )

            tam_tinh = df["Thành tiền"].sum()
            # Giảm giá 5% cho hóa đơn trên 1 triệu đồng
            giam_gia = tam_tinh * 0.05 if tam_tinh > 1000000 else 0
            tong_thanh_toan = tam_tinh - giam_gia

            st.write(f"**Tạm tính:** {tam_tinh:,.0f} VNĐ")
            if giam_gia > 0:
                st.write(f"**Giảm giá (5% > 1M):** -{giam_gia:,.0f} VNĐ")
            st.metric("Tổng thanh toán thực tế", f"{tong_thanh_toan:,.0f} VNĐ")

            col_btn1, col_btn2 = st.columns(2)

            with col_btn1:
                if st.button("💳 Thanh toán"):
                    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                    # Ghi nhận các món vào danh sách lịch sử
                    for row in st.session_state.order_dict.values():
                        st.session_state.history.append(
                            {
                                "Thời gian": now_str,
                                "Bàn": row["Bàn"],
                                "Tên món": row["Tên món"],
                                "Số lượng": row["Số lượng"],
                                "Thành tiền": row["Thành tiền"],
                            }
                        )

                    # ĐỒNG BỘ: Lưu dữ liệu mới xuống tệp tin CSV dùng chung
                    try:
                        df_history = pd.DataFrame(st.session_state.history)
                        df_history.to_csv(
                            CSV_FILE, index=False, encoding="utf-8-sig"
                 
