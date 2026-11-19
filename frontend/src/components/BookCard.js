const MauBia = [
    "rgb(43, 75, 160)", "rgb(26, 102, 110)", "rgb(115, 60, 100)",
    "rgb(84, 94, 40)", "rgb(70, 60, 120)", "rgb(130, 40, 60)"
];function LamSach(Chuoi){
    return String(Chuoi)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#39;");
}function ChonMauBia(BookID){
    let Tong = 0;
    for(let i = 0; i < BookID.length; i++){
        Tong += BookID.charCodeAt(i);
    }
    return MauBia[Tong % MauBia.length];
}function LaIsbnHopLe(BookID){
    return /^[0-9Xx]{9,13}$/.test(String(BookID || "").trim());
}function ThuAnhDuPhong(Anh){
    const BookID = Anh.dataset.bookId || "";
    if(Anh.dataset.daThuOpenLibrary != "1" && LaIsbnHopLe(BookID)){
        Anh.dataset.daThuOpenLibrary = "1";
        Anh.src = "https://covers.openlibrary.org/b/isbn/" + encodeURIComponent(BookID) + "-M.jpg?default=false";
        return;
    }
    Anh.style.display = "none";
}function KiemTraAnh(Anh){
    if(Anh.naturalWidth <= 1){
        ThuAnhDuPhong(Anh);
    }
}function TaoBiaSach(Sach){
    let Src = Sach.image_url || "";
    if((!Src || /images\.amazon\.com/i.test(Src)) && LaIsbnHopLe(Sach.book_id)){
        Src = "https://covers.openlibrary.org/b/isbn/" + encodeURIComponent(Sach.book_id) + "-M.jpg?default=false";
    }
    let Anh = "";
    if(Src){
        const DaThu = /covers\.openlibrary\.org/i.test(Src) ? "1" : "0";
        Anh = `<img src="${LamSach(Src)}" data-book-id="${LamSach(Sach.book_id || "")}" data-da-thu-open-library="${DaThu}" alt="Bìa sách ${LamSach(Sach.title)}" onload="KiemTraAnh(this)" onerror="ThuAnhDuPhong(this)">`;
    }
    return `
        <div class="bia_sach">
            <div class="bia_mac_dinh" style="background-color: ${ChonMauBia(Sach.book_id)}" aria-hidden="true">
                ${LamSach(Sach.title)}
            </div>
            ${Anh}
        </div>
    `;
}function TaoBookCard(Sach, Loai){
    let Nhan = "";

    if(Sach.score != null){
        if(Loai == "tuong_tu"){
            Nhan = "Giống " + Math.round(Sach.score * 100) + "%";
        }
        else if(Loai == "du_doan"){
            Nhan = "Dự đoán " + Sach.score.toFixed(1);
        }
        else{
            Nhan = "Điểm " + Sach.score.toFixed(1);
        }
    }
    let HtmlTacGia = "";
    if(Sach.author != ""){
        HtmlTacGia = `<p class="tac_gia">${LamSach(Sach.author)}</p>`;
    }
    let HtmlDiem = "";
    if(Nhan != ""){
        HtmlDiem = `<span class="diem_so">${Nhan}</span>`;
    }
    return `
        <a class="book_card" href="#book/${encodeURIComponent(Sach.book_id)}">
            ${TaoBiaSach(Sach)}
            <h3 class="ten_sach">${LamSach(Sach.title)}</h3>
            ${HtmlTacGia}
            ${HtmlDiem}
        </a>
    `;
}function TaoDanhSachCard(DanhSach, Loai){
    let Html = "";
    DanhSach.forEach((Sach) => {
        Html += TaoBookCard(Sach, Loai);
    });
    return Html;
}
function TaoLoi(NoiDung){
    return '<p class="thong_bao_loi" role="alert">' + LamSach(NoiDung) + "</p>";
}