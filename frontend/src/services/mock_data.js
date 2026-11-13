// Một số sách mẫu để chạy thử giao diện khi backend chưa hoàn thành
const SachMau = [
    {book_id: "0439425220", image_url: "https://covers.openlibrary.org/b/isbn/0439425220-M.jpg?default=false", title: "Harry Potter and the Chamber of Secrets Postcard Book", author: "J. K. Rowling", score: 9.92},
    {book_id: "0394800389", image_url: "https://covers.openlibrary.org/b/isbn/0394800389-M.jpg?default=false", title: "Fox in Socks (I Can Read It All by Myself Beginner Books)", author: "Dr. Seuss", score: 9.9},
    {book_id: "0920668372", image_url: "https://covers.openlibrary.org/b/isbn/0920668372-M.jpg?default=false", title: "Love You Forever", author: "Robert N. Munsch", score: 9.8},
    {book_id: "0399135782", image_url: "https://covers.openlibrary.org/b/isbn/0399135782-M.jpg?default=false", title: "The Kitchen God's Wife", author: "Amy Tan", year: 1991, publisher: "Putnam Pub Group", score: 8.9},
    {book_id: "0804106304", image_url: "https://covers.openlibrary.org/b/isbn/0804106304-M.jpg?default=false", title: "The Joy Luck Club", author: "Amy Tan", year: 1994, publisher: "Prentice Hall (K-12)", score: 8.8},
    {book_id: "0440234743", image_url: "https://covers.openlibrary.org/b/isbn/0440234743-M.jpg?default=false", title: "The Testament", author: "John Grisham", year: 1999, publisher: "Dell", score: 8.5},
    {book_id: "0345402871", image_url: "https://covers.openlibrary.org/b/isbn/0345402871-M.jpg?default=false", title: "Airframe", author: "Michael Crichton", year: 1997, publisher: "Ballantine Books", score: 8.4},
    {book_id: "0385504209", image_url: "https://covers.openlibrary.org/b/isbn/0385504209-M.jpg?default=false", title: "The Da Vinci Code", author: "Dan Brown", year: 2003, publisher: "Doubleday", score: 8.3},
    {book_id: "0316666343", image_url: "https://covers.openlibrary.org/b/isbn/0316666343-M.jpg?default=false", title: "The Lovely Bones: A Novel", author: "Alice Sebold", year: 2002, publisher: "Little, Brown", score: 8.2},
    {book_id: "0195153448", image_url: "https://covers.openlibrary.org/b/isbn/0195153448-M.jpg?default=false", title: "Classical Mythology", author: "Mark P. O. Morford", year: 2002, publisher: "Oxford University Press", score: 7.8}
];

// Danh sách sách tiếng Việt lấy từ Kho Sách Online.
// image_url dùng ảnh bìa từ các trang giới thiệu sách; link mở tài liệu đọc.
const DanhSachSachTiengViet = [

    {ma: "vn01", ten: "Đắc Nhân Tâm", link: "https://drive.google.com/file/d/1mlIagmYc0_B7E38xHcmyEYLSZj-qlLGM/view?usp=drive_open", tac_gia: "Dale Carnegie", image_url: "https://sachtiengviet.com/cdn/shop/files/05f733810a7a8e323bc0e8a9af473421_1024x1024.jpg?v=1720948661"},
    {ma: "vn02", ten: "Nghĩ Giàu Và Làm Giàu", link: "https://drive.google.com/file/d/1MobeoGLxrv0hVEbCRo4VuOW4gV_EYoYf/view?usp=drive_open", tac_gia: "Napoleon Hill", image_url: "https://www.netabooks.vn/Data/Sites/1/Product/36217/think-and-grow-rich-nghi-giau-va-lam-giau-phien-ban-dac-biet-bia-cung.jpg"},
    {ma: "vn03", ten: "Quẳng Gánh Lo Đi Và Vui Sống", link: "https://drive.google.com/file/d/1t0-EVWPVMI0eZFB6DVcvHgPcoxiuEYMV/view?usp=drive_open", tac_gia: "Dale Carnegie", image_url: "https://www.netabooks.vn/Data/Sites/1/Product/75158/quang-ganh-lo-di-va-vui-song-how-to-stop-worrying-and-start-living.jpg"},
    {ma: "vn04", ten: "Ai Lấy Miếng Pho Mát Của Tôi?", link: "https://drive.google.com/file/d/15-xaQxxuI5PdPwes_1gquhv4lkABuXJs/view?usp=drive_open", tac_gia: "Spencer Johnson", image_url: "https://shopeziau.sgp1.cdn.digitaloceanspaces.com/prod/92/92c40b51b015f4e65ba65b7694e9d99eb5617b05"},
    {ma: "vn05", ten: "Ngày Xưa Có Một Con Bò", link: "https://drive.google.com/file/d/1eGdd6K5-fIaFrdid4vq7lMtRIlMxMo5h/view?usp=drive_open", tac_gia: "Camilo Cruz", image_url: "https://cdn1.fahasa.com/media/catalog/product/i/m/image_195509_1_27254.jpg"},
    {ma: "vn06", ten: "Thành Công Với Thái Độ Tích Cực", link: "https://drive.google.com/file/d/1lnH7pEs0KHKVp7D8r_OsXqm8pQsCo6hr/view?usp=drive_open"},
    {ma: "vn07", ten: "Chiếc Lexus Và Cây Ô Liu", link: "https://drive.google.com/file/d/1Ga8wfeFvrJeHNYzfOeK23G10pcrFA-AS/view?usp=drive_open", tac_gia: "Thomas L. Friedman", image_url: "https://static.oreka.vn/800-800_05e29564-e4e7-46ac-95b1-f84bc91a79ec"},
    {ma: "vn08", ten: "Chiến Thắng Con Quỷ Trong Bạn", link: "https://drive.google.com/file/d/1-b8cYbhSn0sRGvb1SVCSwmqBj6H42GC9/view?usp=drive_open", tac_gia: "Napoleon Hill", image_url: "https://cdn1.fahasa.com/media/catalog/product/9/7/9786044415536.jpg"},
    {ma: "vn09", ten: "Con Đường Phía Trước", link: "https://drive.google.com/file/d/1Vd7CXwds8rsY-hSqw2JtA4IvmdxD7SML/view?usp=drive_open"},
    {ma: "vn10", ten: "Dám Nghĩ Lớn", link: "https://drive.google.com/file/d/1pftqeABPQKREvPkAm7EH4Anl8e6zG_vh/view?usp=drive_open", tac_gia: "David J. Schwartz", image_url: "https://pos.nvncdn.com/fd5775-40602/ps/20240510_ZdXKXzd2U6.png?v=1715326203"},
    {ma: "vn11", ten: "Đánh Cắp Ý Tưởng", link: "https://drive.google.com/file/d/12RHFQnrpH_tryWkBm5Sgt8mnBRRfb-vL/view?usp=drive_open"},
    {ma: "vn12", ten: "Dám Chấp Nhận", link: "https://drive.google.com/file/d/1ojk2nz0oY5iTGwLTGTMzKkGcOkkmgS3L/view?usp=drive_open"},
    {ma: "vn13", ten: "Đọc Vị Bất Kỳ Ai", link: "https://drive.google.com/file/d/1SabMlzE3C7rSG-mxhor-nuMNhXT5AGUj/view?usp=drive_open", tac_gia: "David J. Lieberman", image_url: "https://www.sachkhaitri.com/Data/Sites/2/Product/62204/doc-vi-bat-ky-ai-de-khong-bi-lua-doi-va-loi-dung.jpg"},
    {ma: "vn14", ten: "Đọc Vị Khách Hàng", link: "https://drive.google.com/file/d/18fjeyOKmilAUct_4R-MW52PPlZwrHmp6/view?usp=drive_open"},
    {ma: "vn15", ten: "Hẹn Bạn Trên Đỉnh Thành Công", link: "https://drive.google.com/file/d/1SAOi5KHoUWodrRL6tCOz-3VXmeCivKXa/view?usp=drive_open"},
    {ma: "vn16", ten: "Nghĩ Lớn Để Thành Công", link: "https://drive.google.com/file/d/1dvvrGVAV9f2dm1wcAbPEXr7ZCigOO4Jl/view?usp=drive_open", tac_gia: "Donald J. Trump", image_url: "https://www.netabooks.vn/Data/Sites/1/Product/1932/nghi-lon-de-thanh-cong-3.jpg"},
    {ma: "vn17", ten: "Khác Biệt Hay Là Chết", link: "https://drive.google.com/file/d/1-NgbXqb7ddXRM3qPOfHzdfDEXlzXSGJn/view?usp=drive_open"},
    {ma: "vn18", ten: "Tuổi Trẻ Đáng Giá Bao Nhiêu", link: "https://drive.google.com/file/d/1hDwTGnNfNfdAqa4DVeumEBcLmwKCjUXD/view?usp=drive_open", tac_gia: "Rosie Nguyễn", image_url: "https://www.netabooks.vn/Data/Sites/1/Product/2625/tuoi-tre-dang-gia-bao-nhieu-3.jpg"},
    {ma: "vn19", ten: "Đừng Bao Giờ Đi Ăn Một Mình", link: "https://drive.google.com/file/d/1kk3CzPtB7JYc7nBWMy4xcpryTeUeZqZ6/view?usp=drive_open"},
    {ma: "vn20", ten: "Bàn Về Tiếp Thị", link: "https://drive.google.com/file/d/1toHQEvabgku4nA6AXfZS0cfDGqzHcYrs/view?usp=drive_open"},
    {ma: "vn21", ten: "Làm Chủ Tư Duy Thay Đổi Vận Mệnh", link: "https://drive.google.com/file/d/1_ebP-SydCRkdjqUoRgi3C88PBR9KtSnl/view?usp=drive_open"},
    {ma: "vn22", ten: "Bí Quyết Gây Dựng Cơ Nghiệp Bạc Tỷ", link: "https://drive.google.com/file/d/1prT4RcTAoiLqP6Bf2lIVn9HMW3LLmutj/view?usp=drive_open"},
    {ma: "vn23", ten: "Sống Và Suy Ngẫm", link: "https://drive.google.com/file/d/1yeO-DqW4Mb0ipKgHiccbbX-jQWUKy_Nh/view?usp=drive_open", tac_gia: "V. N. Kakar", image_url: "https://media.metaisach.com/2025/03/song-va-suy-ngam-50cf6d54.jpeg"},
    {ma: "vn24", ten: "Thay Thái Độ Đổi Cuộc Đời", link: "https://drive.google.com/file/d/1e-o1LfV0evARGeDjPeJ9OKdWmoCluUFf/view?usp=drive_open"},
    {ma: "vn25", ten: "Trên Đường Băng", link: "https://drive.google.com/file/d/1rYwp8NJcUvSqtdYIycDM2Z5pKBMVeCHY/view?usp=drive_open"},
    {ma: "vn26", ten: "Tư Duy Đột Phá", link: "https://drive.google.com/file/d/1TB_x3UKtoklyX7fCAr64EzgpPyT4QtUp/view?usp=drive_open"},
    {ma: "vn27", ten: "Tử Huyệt Cảm Xúc", link: "https://drive.google.com/file/d/1PRPLJOS93UMpNkiH3w-Q22uyScTZLKem/view?usp=drive_open"},
    {ma: "vn28", ten: "Vị Giám Đốc Một Phút Và Xây Dựng Nhóm Làm Việc Hiệu Quả", link: "https://drive.google.com/file/d/1q7IeH_QmW6fB3OniayjoSgjV-vznrZh8/view?usp=drive_open"},
    {ma: "vn29", ten: "Từ Tốt Đến Vĩ Đại", link: "https://drive.google.com/file/d/1G1V2VJJ0Q-nkkOqXwsMNJOpyED4MiICJ/view?usp=drive_open"},
    {ma: "vn30", ten: "Hành Trình Về Phương Đông", link: "https://drive.google.com/file/d/1dYBtF5nWyCo15txZ54Edz5IE-JN2PD3C/view?usp=drive_open", tac_gia: "Baird T. Spalding", image_url: "https://salt.tikicdn.com/cache/w1200/ts/product/60/aa/d1/698a837a28488c0405a5303e87c0e6b8.jpg"},
    {ma: "vn31", ten: "Tôi Tài Giỏi, Bạn Cũng Thế", link: "https://drive.google.com/file/d/11g3DhfAH_fBVMRoOap1RteEWlFS5IcRD/view?usp=drive_open", tac_gia: "Adam Khoo", image_url: "https://salt.tikicdn.com/cache/750x750/ts/product/76/c0/1e/0ff7ee76ba4d2529b177c7891132abac.jpg"},
    {ma: "vn32", ten: "Nghệ Thuật Bán Hàng Bậc Cao", link: "https://drive.google.com/file/d/1ZI1PhpiMj6M8gKqvudGMZww2yjiBrZ-p/view?usp=drive_open"},
    {ma: "vn33", ten: "7 Thói Quen Để Thành Đạt", link: "https://drive.google.com/file/d/1X3_ky0H8pOxra4I8CmQy-zq_qVyF6fMG/view?usp=drive_open", tac_gia: "Stephen R. Covey", image_url: "https://product.hstatic.net/200000979221/product/7-thoi-quen-de-thanh-dat_028247b518f744c2b4ceb9d8ed5ee1e5.jpg"},
    {ma: "vn34", ten: "Người Bán Hàng Vĩ Đại Nhất Thế Giới", link: "https://drive.google.com/file/d/1iogy0P4RO2Cx9MyWzAR_TPQhkRDRraPT/view?usp=drive_open"},
    {ma: "vn35", ten: "Nhà Giả Kim", link: "https://drive.google.com/file/d/1PCzOLEzVqMx0F9Y-kNhqp3a8CTDORso8/view?usp=drive_open", tac_gia: "Paulo Coelho", image_url: "https://down-vn.img.susercontent.com/file/ea35cecdb662b48b73ec76f1c83ef110"},
    {ma: "vn36", ten: "Để Xây Dựng Doanh Nghiệp", link: "https://drive.google.com/file/d/16WSsMeh1Ha0mugyN-B8HxneP-6VCB2su/view?usp=drive_open"},
    {ma: "vn37", ten: "100 Ý Tưởng Bán Hàng Hay Nhất Mọi Thời Đại", link: "https://drive.google.com/file/d/1tuBTPNnj1u8BE-pY4YIwlJ_RW8glbzMB/view?usp=drive_open"},
    {ma: "vn38", ten: "1001 Cách Giữ Chân Khách Hàng", link: "https://drive.google.com/file/d/1r_OJkn0tBcepK5H4DsvvTMsOnvAqyShv/view?usp=drive_open"},
    {ma: "vn39", ten: "Tỷ Phú Bán Giày", link: "https://drive.google.com/file/d/1fCbFi_sObuahLcK6EXUmMnpHGOmZb4Yn/view?usp=drive_open"},
    {ma: "vn40", ten: "Xây Dựng Để Trường Tồn", link: "https://drive.google.com/file/d/1ymGvUxHe3c4t69-CjszPAsvzLPDKNbXj/view?usp=drive_open"},
    {ma: "vn41", ten: "Thế Giới Phẳng", link: "https://drive.google.com/file/d/1pTGzw-WBWHMPLVnq8KYM2dF1miymPFMK/view?usp=drive_open"},
    {ma: "vn42", ten: "101 Ý Tưởng Quảng Cáo Khôn Ngoan", link: "https://drive.google.com/file/d/1BBwDDZHWyaMCKJatGBByYKmGuFbtt9fR/view?usp=drive_open"},
    {ma: "vn43", ten: "12 Tuyệt Kỹ Bán Hàng", link: "https://drive.google.com/file/d/1Y6kEr2o8-WML1siMZEJqQj4cselL4z2P/view?usp=drive_open"}
];

// Giả lập dữ liệu trả về từ backend
async function LayDuLieuMau(DuongDan){
    // Tạo một khoảng chờ ngắn để giống lúc gửi yêu cầu đến server
    await new Promise((resolve) => setTimeout(resolve, 500));
    const Url = new URL(DuongDan, "http://mau");
    const CacPhan = Url.pathname.split("/");
    // Danh sách sách được đánh giá cao
    if(CacPhan[1] == "popular"){
        return {recommend_type: "Popularity (Cold Start)", popular_books: SachMau};
    }
    // Gợi ý sách theo User-ID
    if(CacPhan[1] == "recommend"){
        if(Number(CacPhan[2]) > 278858){
            const Loi = new Error("Không tìm thấy dữ liệu.");
            Loi.status = 404;
            throw Loi;
        }
        await new Promise((resolve) => setTimeout(resolve, 1000));
        return {recommendations: SachMau.slice(3)};
    }
    // Tìm sách theo tên sách hoặc tên tác giả
    if(CacPhan[2] == "search"){
        const TuKhoa = (Url.searchParams.get("q") || "").toLowerCase();
        const DanhSachTimDuoc = SachMau.filter((Sach) => {
            return (Sach.title + " " + Sach.author).toLowerCase().includes(TuKhoa);
        });
        return {books: DanhSachTimDuoc};
    }
    // Tìm cuốn sách đang được chọn
    const BookID = decodeURIComponent(CacPhan[2]);
    const SachGoc = SachMau.find((Sach) => Sach.book_id == BookID);
    if(SachGoc == undefined){
        const Loi = new Error("Không tìm thấy dữ liệu.");
        Loi.status = 404;
        throw Loi;
    }
    // Danh sách sách tương tự cuốn đang xem
    if(CacPhan[3] == "similar"){
        const DanhSachKhac = SachMau.filter((Sach) => Sach.book_id != BookID);
        DanhSachKhac.sort((SachA, SachB) => {
            return (SachB.author == SachGoc.author) - (SachA.author == SachGoc.author);
        });
        const DanhSachTuongTu = DanhSachKhac.slice(0, 5).map((Sach) => {
            return {
                book_id: Sach.book_id,
                title: Sach.title,
                author: Sach.author,
                year: Sach.year,
                publisher: Sach.publisher,
                image_url: Sach.image_url,
                score: Sach.author == SachGoc.author ? 0.9 : 0.2
            };
        });
        return {target_book_id: BookID, similar_books: DanhSachTuongTu};
    }
    // Trả về thông tin chi tiết của một cuốn sách
    return {
        book_id: SachGoc.book_id,
        title: SachGoc.title,
        author: SachGoc.author,
        year: SachGoc.year,
        publisher: SachGoc.publisher,
        image_url: SachGoc.image_url,
        score: SachGoc.score,
        rating_mean: SachGoc.score
    };
}
