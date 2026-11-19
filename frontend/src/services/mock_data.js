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
    // Gợi ý sách theo User-ID (SVD hoặc Popularity Cold Start Fallback)
    if(CacPhan[1] == "recommend"){
        await new Promise((resolve) => setTimeout(resolve, 600));
        const UserID = Number(CacPhan[2]);
        if(UserID > 278858){
            return {
                user_id: UserID,
                recommend_type: "Popularity-Based (Cold Start Fallback)",
                is_cold_start: true,
                message: `User-ID ${UserID} chưa có lịch sử đánh giá (Cold Start). Hệ thống tự động dùng Popularity-Based để gợi ý sách phổ biến nhất.`,
                recommendations: SachMau.slice(0, 10)
            };
        }
        return {
            user_id: UserID,
            recommend_type: "Collaborative Filtering (SVD)",
            is_cold_start: false,
            message: `Gợi ý cá nhân hóa cho User-ID ${UserID} bằng Collaborative Filtering (SVD).`,
            recommendations: SachMau.slice(3)
        };
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
