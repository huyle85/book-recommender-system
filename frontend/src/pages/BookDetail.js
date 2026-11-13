function HienThiChiTiet(BookID){
    ChuyenTrang("trang_chi_tiet");
    TaiThongTinSach(BookID);
    TaiSachTuongTu(BookID);
}async function TaiThongTinSach(BookID){
    const Khung = document.getElementById("chi_tiet_sach");
    Khung.innerHTML = '<p class="thong_bao">Đang tải thông tin sách...</p>';
    try{
        const Sach = await LayChiTietSach(BookID);
        let ThongTin = "";
        if(Sach.author != ""){
            ThongTin += "<p>Tác giả: <b>" + LamSach(Sach.author) + "</b></p>";
        }
        if(Sach.year != ""){
            ThongTin += "<p>Năm xuất bản: <b>" + LamSach(Sach.year) + "</b></p>";
        }
        if(Sach.publisher != ""){
            ThongTin += "<p>Nhà xuất bản: <b>" + LamSach(Sach.publisher) + "</b></p>";
        }
        ThongTin += "<p>ISBN: <b>" + LamSach(Sach.book_id) + "</b></p>";
        if(Sach.rating_mean != undefined){
            ThongTin += "<p>Điểm trung bình: <b>" + Number(Sach.rating_mean).toFixed(1) + " / 10</b>";
            if(Sach.rating_count != undefined){
                ThongTin += " (" + Sach.rating_count + " lượt đánh giá)";
            }
            ThongTin += "</p>";
        }
        Khung.innerHTML = `
            <div class="chi_tiet">
                <div class="bia_lon">${TaoBiaSach(Sach)}</div>
                <div>
                    <h1>${LamSach(Sach.title)}</h1>
                    ${ThongTin}
                </div>
            </div>
        `;
        document.title = Sach.title + " - Gợi ý sách";
    }
    catch(error){
        console.log(error);
        if(error.status == 404){
            Khung.innerHTML = TaoLoi("Không tìm thấy cuốn sách này. Hãy quay lại trang chủ và chọn sách khác.");
        }
        else{
            Khung.innerHTML = TaoLoi(error.message);
        }
    }
}async function TaiSachTuongTu(BookID){
    const Khung = document.getElementById("sach_tuong_tu");
    Khung.innerHTML = '<p class="thong_bao">Đang tìm sách tương tự...</p>';
    try{
        const DanhSach = await LaySachTuongTu(BookID, 5);
        if(DanhSach.length == 0){
            Khung.innerHTML = '<p class="thong_bao">Chưa có sách tương tự cho cuốn này.</p>';
            return;
        }
        Khung.innerHTML = TaoDanhSachCard(DanhSach, "tuong_tu");
    }
    catch(error){
        console.log(error);
        Khung.innerHTML = TaoLoi(error.message);
    }
}
