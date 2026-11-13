function HienThiSearchBar(){
    document.getElementById("search_bar").innerHTML = `
        <form class="search_form" onsubmit="TimKiem(event)">
            <label for="o_tim_kiem">Tìm sách:</label>
            <input type="search" id="o_tim_kiem" placeholder="Tên sách hoặc tác giả">
            <button type="submit" class="button_chinh">Tìm sách</button>
        </form>
    `;
}function TimKiem(event){
    event.preventDefault();
    const TuKhoa = document.getElementById("o_tim_kiem").value.trim();
    if(TuKhoa == ""){
        return;
    }
    location.hash = "search/" + encodeURIComponent(TuKhoa);
}
