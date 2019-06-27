function hrefBack() {
    history.go(-1);
}

function decodeQuery() {
    var search = decodeURI(document.location.search);
    return search.replace(/(^\?)/, '').split('&').reduce(function (result, item) {
        values = item.split('=');
        result[values[0]] = values[1];
        return result;
    }, {});
}

$(document).ready(function () {
    var id = decodeQuery()['id'];
    $.get('/api/v1/house/' + id, function (data) {
        if(data.errno == "0") {
            $(".swiper-container").html(template("house-image-tmpl", {img_urls:data.data.house.img_urls, price:data.data.house.price}));
            var html = template('house-detail-tmpl', {house: data.data.house});
            $(".detail-con").html(html);
            //图片播放
            var mySwiper = new Swiper('.swiper-container', {
                loop: true,
                autoplay: 2000,
                autoplayDisableOnInteraction: false,
                pagination: '.swiper-pagination',
                paginationType: 'fraction'
            });
            //判断是否显示预订按钮
            // resp.user_id为访问页面用户,resp.data.user_id为房东
        if (data.data.user_id != data.data.house.user_id) {
            $(".book-house").attr("href", "/booking.html?hid="+data.data.house.hid);
            $(".book-house").show();
        }
        }
    });
})