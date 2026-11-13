// Chuyển giữa trang chủ và trang chi tiết sách
function ChuyenTrang(TenTrang){
    const DanhSachTrang = document.querySelectorAll(".trang");

    DanhSachTrang.forEach((Trang) => {
        Trang.style.display = "none";
    });

    document.getElementById(TenTrang).style.display = "block";
    window.scrollTo(0, 0);
}

// Đọc địa chỉ trên thanh URL để biết cần hiển thị trang nào
// #book/ISBN: trang chi tiết sách
// #search/tu-khoa: trang kết quả tìm kiếm
// Các trường hợp còn lại: trang chủ
function DinhTuyen(){
    const DuongDan = location.hash.replace("#", "");

    if(DuongDan.startsWith("book/")){
        HienThiChiTiet(decodeURIComponent(DuongDan.slice(5)));
    }
    else if(DuongDan.startsWith("search/")){
        HienThiTimKiem(decodeURIComponent(DuongDan.slice(7)));
    }
    else{
        HienThiTrangChu();
    }
}

// Hiện thông báo nếu đang bật chế độ dữ liệu mẫu
if(DUNG_DU_LIEU_MAU){
    document.getElementById("thong_bao_mau").style.display = "block";
}

// Tạo ô tìm kiếm và bắt đầu hiển thị trang phù hợp
HienThiSearchBar();
window.addEventListener("hashchange", DinhTuyen);
DinhTuyen();
