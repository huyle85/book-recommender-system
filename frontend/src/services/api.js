// Địa chỉ backend FastAPI
const API_URL = "http://localhost:8000/api";

// Để true thì dùng dữ liệu mẫu. Khi backend đã chạy thì đổi thành false.
const DUNG_DU_LIEU_MAU = true;

/* Các đường dẫn API frontend sẽ sử dụng:
   GET /popular?top_k=10                -> {popular_books: [Sach]}
   GET /books/search?q=harry            -> {books: [Sach]}
   GET /books/{book_id}                 -> Sach
   GET /books/{book_id}/similar?top_k=5 -> {similar_books: [Sach]}
   GET /recommend/{user_id}?top_k=10    -> {recommendations: [Sach]}

   Thông tin một cuốn sách gồm: book_id, title, author, year,
   publisher, image_url và score.
*/

// Gửi yêu cầu đến backend hoặc lấy dữ liệu mẫu
async function GoiAPI(DuongDan){
    if(DUNG_DU_LIEU_MAU){
        return await LayDuLieuMau(DuongDan);
    }
    let Response;
    try{
        Response = await fetch(API_URL + DuongDan);
    }
    catch(error){
        console.log(error);
        throw new Error("Không kết nối được tới backend. Hãy kiểm tra backend đã chạy ở " + API_URL + " chưa.");
    }
    if(Response.status == 404){
        const Loi = new Error("Không tìm thấy dữ liệu.");
        Loi.status = 404;
        throw Loi;
    }
    if(!Response.ok){
        throw new Error("Backend trả về lỗi " + Response.status);
    }
    return await Response.json();
}
// Đưa dữ liệu từ các file của nhóm về cùng một dạng thông tin sách
function ChuanHoaSach(Sach){
    let DiemSo = null;
    if(Sach.score != undefined){
        DiemSo = Number(Sach.score);
    }
    else if(Sach.similarity_score != undefined){
        DiemSo = Number(Sach.similarity_score);
    }
    else if(Sach.Predicted_Rating != undefined){
        DiemSo = Number(Sach.Predicted_Rating);
    }
    let Nam = Sach.year || Sach["Year-Of-Publication"] || "";
    if(Nam == 0){
        Nam = "";
    }
    return {
        book_id: String(Sach.book_id || Sach.ISBN || ""),
        title: Sach.title || Sach["Book-Title"] || "Chưa có tên sách",
        author: Sach.author || Sach["Book-Author"] || "",
        year: Nam,
        publisher: Sach.publisher || Sach.Publisher || "",
        image_url: Sach.image_url || Sach["Image-URL-M"] || "",
        rating_mean: Sach.rating_mean,
        rating_count: Sach.rating_count,
        score: DiemSo
    };
}
async function LayPhoBien(SoLuong){
    const Data = await GoiAPI("/popular?top_k=" + SoLuong);
    return Data.popular_books.map(ChuanHoaSach);
}ả
async function TimSach(TuKhoa){
    const Data = await GoiAPI("/books/search?q=" + encodeURIComponent(TuKhoa));
    return Data.books.map(ChuanHoaSach);
}
async function LayChiTietSach(BookID){
    const Data = await GoiAPI("/books/" + encodeURIComponent(BookID));
    return ChuanHoaSach(Data);
}
async function LaySachTuongTu(BookID, SoLuong){
    const Data = await GoiAPI("/books/" + encodeURIComponent(BookID) + "/similar?top_k=" + SoLuong);
    return Data.similar_books.map(ChuanHoaSach);
}
async function LayGoiYTheoUser(UserID, SoLuong){
    const Data = await GoiAPI("/recommend/" + encodeURIComponent(UserID) + "?top_k=" + SoLuong);
    return Data.recommendations.map(ChuanHoaSach);
}
