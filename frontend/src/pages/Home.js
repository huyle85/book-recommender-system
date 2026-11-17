const SO_SACH_MOI_TRANG = 8;
let DanhSachPhoBien = [];
let TrangPhoBienHienTai = 1;
let TrangSachVietHienTai = 1;
function HienThiTrangChu(){
    ChuyenTrang("trang_home");
    document.getElementById("khu_trang_chu").style.display = "block";
    document.getElementById("khu_tim_kiem").style.display = "none";
    document.getElementById("o_tim_kiem").value = "";
    document.title = "Gợi ý sách";
    if(DanhSachPhoBien.length === 0){
        TaiSachPhoBien();
    }
    else{
        HienThiTrangSachPhoBien(TrangPhoBienHienTai);
    }
    HienThiSachTiengViet(TrangSachVietHienTai);
}

async function TaiSachPhoBien(){
    const Khung = document.getElementById("danh_sach_pho_bien");
    const KhungPhanTrang = document.getElementById("phan_trang_pho_bien");
    Khung.innerHTML = '<p class="thong_bao">Đang tải sách...</p>';
    KhungPhanTrang.innerHTML = "";
    try{
        DanhSachPhoBien = await LayPhoBien(100);
        TrangPhoBienHienTai = 1;
        HienThiTrangSachPhoBien(TrangPhoBienHienTai);
    }
    catch(error){
        console.log(error);
        Khung.innerHTML = TaoLoi(error.message);
    }
}function HienThiTrangSachPhoBien(Trang){
    const Khung = document.getElementById("danh_sach_pho_bien");
    const KhungPhanTrang = document.getElementById("phan_trang_pho_bien");
    const TongTrang = Math.ceil(DanhSachPhoBien.length / SO_SACH_MOI_TRANG);
    if(TongTrang == 0){
        Khung.innerHTML = '<p class="thong_bao">Chưa có sách để hiển thị.</p>';
        KhungPhanTrang.innerHTML = "";
        return;
    }
    if(Trang < 1){
        Trang = 1;
    }
    if(Trang > TongTrang){
        Trang = TongTrang;
    }
    TrangPhoBienHienTai = Trang;
    const ViTriDau = (Trang - 1) * SO_SACH_MOI_TRANG;
    const SachTrenTrang = DanhSachPhoBien.slice(ViTriDau, ViTriDau + SO_SACH_MOI_TRANG);
    Khung.innerHTML = TaoDanhSachCard(SachTrenTrang, "pho_bien");
    KhungPhanTrang.innerHTML = `
        <button class="nut_phan_trang" onclick="ChuyenTrangPhoBien(${Trang - 1})" ${Trang == 1 ? "disabled" : ""}>
            Trước
        </button>
        <span class="so_trang">Trang ${Trang} / ${TongTrang}</span>
        <button class="nut_phan_trang" onclick="ChuyenTrangPhoBien(${Trang + 1})" ${Trang == TongTrang ? "disabled" : ""}>
            Tiếp theo
        </button>
    `;
}function ChuyenTrangPhoBien(Trang){
    HienThiTrangSachPhoBien(Trang);
    document.getElementById("danh_sach_pho_bien").scrollIntoView({behavior: "smooth", block: "start"});
}
function HienThiSachTiengViet(Trang){
    const Khung = document.getElementById("danh_sach_tieng_viet");
    const KhungPhanTrang = document.getElementById("phan_trang_tieng_viet");
    const TongTrang = Math.ceil(DanhSachSachTiengViet.length / SO_SACH_MOI_TRANG);
    if(Trang < 1){
        Trang = 1;
    }
    if(Trang > TongTrang){
        Trang = TongTrang;
    }
    TrangSachVietHienTai = Trang;
    const ViTriDau = (Trang - 1) * SO_SACH_MOI_TRANG;
    const SachTrenTrang = DanhSachSachTiengViet.slice(ViTriDau, ViTriDau + SO_SACH_MOI_TRANG);
    let Html = "";
    SachTrenTrang.forEach((Sach) => {
        Html += TaoTheSachViet(Sach);
    });
    Khung.innerHTML = Html;
    KhungPhanTrang.innerHTML = `
        <button class="nut_phan_trang" onclick="HienThiSachTiengViet(${Trang - 1})" ${Trang == 1 ? "disabled" : ""}>
            Trước
        </button>
        <span class="so_trang">Trang ${Trang} / ${TongTrang}</span>
        <button class="nut_phan_trang" onclick="HienThiSachTiengViet(${Trang + 1})" ${Trang == TongTrang ? "disabled" : ""}>
            Tiếp theo
        </button>
    `;
}
async function HienThiTimKiem(TuKhoa){
    ChuyenTrang("trang_home");
    document.getElementById("khu_trang_chu").style.display = "none";
    document.getElementById("khu_tim_kiem").style.display = "block";
    document.getElementById("o_tim_kiem").value = TuKhoa;
    document.getElementById("tieu_de_tim_kiem").textContent = "Kết quả tìm kiếm cho: " + TuKhoa;
    document.title = TuKhoa + " - Gợi ý sách";
    const Khung = document.getElementById("ket_qua_tim_kiem");
    Khung.innerHTML = '<p class="thong_bao">Đang tìm sách...</p>';
    try{
        const DanhSach = await TimSach(TuKhoa);
        if(DanhSach.length == 0){
            Khung.innerHTML = '<p class="thong_bao">Không tìm thấy sách nào. Thử tên tác giả hoặc từ khóa ngắn hơn.</p>';
            return;
        }
        Khung.innerHTML = TaoDanhSachCard(DanhSach, "");
    }
    catch(error){
        console.log(error);
        Khung.innerHTML = TaoLoi(error.message);
    }
}
async function GoiYTheoUser(event){
    event.preventDefault();
    const UserID = document.getElementById("user_id").value.trim();
    const KetQua = document.getElementById("ket_qua_user");
    const Nut = document.getElementById("button_user");
    if(UserID == ""){
        KetQua.innerHTML = TaoLoi("Vui lòng nhập User-ID.");
        return;
    }
    if(!/^\d+$/.test(UserID) || !Number.isSafeInteger(Number(UserID)) || Number(UserID) < 1){
        KetQua.innerHTML = TaoLoi("User-ID phải là số nguyên dương hợp lệ, ví dụ 166596 hoặc 9999999.");
        return;
    }
    const CleanUserID = String(Number(UserID));
    KetQua.innerHTML = '<p class="thong_bao">Đang tính gợi ý cho User ' + LamSach(CleanUserID) + ', việc này có thể mất vài giây...</p>';
    Nut.disabled = true;
    try{
        const KetQuaGoiY = await LayGoiYTheoUser(CleanUserID, 10);
        const DanhSach = KetQuaGoiY.books || [];
        if(DanhSach.length === 0){
            KetQua.innerHTML = '<p class="thong_bao">Hiện chưa có sách gợi ý cho User-ID ' + LamSach(CleanUserID) + ".</p>";
            return;
        }
        if(KetQuaGoiY.is_cold_start){
            const MoTa = KetQuaGoiY.message || (
                "User-ID " + CleanUserID + " chưa có lịch sử đánh giá (Cold Start). Hệ thống tự động dùng Popularity-Based để gợi ý " +
                DanhSach.length + " sách phổ biến nhất."
            );
            KetQua.innerHTML =
                "<h3>Gợi ý Cold Start cho User " + LamSach(CleanUserID) + " — Popularity-Based (Top " + DanhSach.length + ")</h3>" +
                '<p class="thong_bao_cold_start">' + LamSach(MoTa) + "</p>" +
                '<div class="luoi_sach">' + TaoDanhSachCard(DanhSach, "pho_bien") + "</div>";
        }
        else{
            const MoTa = KetQuaGoiY.message || (
                "Gợi ý cá nhân hóa cho User-ID " + CleanUserID + " bằng Collaborative Filtering (SVD)."
            );
            KetQua.innerHTML =
                "<h3>Gợi ý cá nhân hóa cho User " + LamSach(CleanUserID) + " — Collaborative Filtering (SVD)</h3>" +
                '<p class="thong_bao_svd">' + LamSach(MoTa) + "</p>" +
                '<div class="luoi_sach">' + TaoDanhSachCard(DanhSach, "du_doan") + "</div>";
        }
    }
    catch(error){
        console.log(error);
        KetQua.innerHTML = TaoLoi(error.message);
    }
    finally{
        Nut.disabled = false;
    }
}
