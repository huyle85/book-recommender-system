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
}function KiemTraAnh(Anh){
    if(Anh.naturalWidth <= 1){
        Anh.style.display = "none";
    }
}function TaoBiaSach(Sach){
    let Anh = "";
    if(Sach.image_url){
        Anh = `<img src="${LamSach(Sach.image_url)}" alt="Bìa sách ${LamSach(Sach.title)}" loading="lazy" onload="KiemTraAnh(this)" onerror="this.style.display='none'">`;
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
function TaoTheSachViet(Sach){
    const ThongTinSach = {
        book_id: Sach.ma,
        title: Sach.ten,
        image_url: Sach.image_url || ""
    };
    let HtmlTacGia = "";
    if(Sach.tac_gia){
        HtmlTacGia = `<p class="tac_gia">${LamSach(Sach.tac_gia)}</p>`;
    }
    return `
        <a class="sach_viet_card" href="${LamSach(Sach.link)}" target="_blank" rel="noopener noreferrer">
            ${TaoBiaSach(ThongTinSach)}
            <h3 class="ten_sach">${LamSach(Sach.ten)}</h3>
            ${HtmlTacGia}
            <p class="nguon_sach">Kho Sách Online</p>
            <span class="nut_doc_sach">Đọc sách ↗</span>
        </a>
    `;
}
