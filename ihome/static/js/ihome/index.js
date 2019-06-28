function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}
//模态框居中的控制
function centerModals() {
    $('.modal').each(function (i) {   //遍历每一个模态框
        var $clone = $(this).clone().css('display', 'block').appendTo('body');
        var top = Math.round(($clone.height() - $clone.find('.modal-content').height()) / 2);
        top = top > 0 ? top : 0;
        $clone.remove();
        $(this).find('.modal-content').css("margin-top", top - 30);  //修正原先已经有的30个像素
    });
}

function setStartDate() {
    var startDate = $("#start-date-input").val();
    if (startDate) {
        $(".search-btn").attr("start-date", startDate);
        $("#start-date-btn").html(startDate);
        $("#end-date").datepicker("destroy");
        $("#end-date-btn").html("离开日期");
        $("#end-date-input").val("");
        $(".search-btn").attr("end-date", "");
        $("#end-date").datepicker({
            language: "zh-CN",
            keyboardNavigation: false,
            startDate: startDate,
            format: "yyyy-mm-dd"
        });
        $("#end-date").on("changeDate", function () {
            $("#end-date-input").val(
                $(this).datepicker("getFormattedDate")
            );
        });
        $(".end-date").show();
    }
    $("#start-date-modal").modal("hide");
}

function setEndDate() {
    var endDate = $("#end-date-input").val();
    if (endDate) {
        $(".search-btn").attr("end-date", endDate);
        $("#end-date-btn").html(endDate);
    }
    $("#end-date-modal").modal("hide");
}

function goToSearchPage(th) {
    var url = "/search.html?";
    url += ("aid=" + $(th).attr("area-id"));
    url += "&";
    var areaName = $(th).attr("area-name");
    if (undefined == areaName) areaName = "";
    url += ("aname=" + areaName);
    url += "&";
    url += ("sd=" + $(th).attr("start-date"));
    url += "&";
    url += ("ed=" + $(th).attr("end-date"));
    location.href = url;
}

function logout() {
    $.ajax({
        url: '/api/v1/loginout',
        type: 'DELETE',
        headers:{
            "X-CSRFToken":getCookie("csrf_token")
        },
        success: function (data) {
            if (data.errno == RET.OK) {
                $(".top-bar>.user-info").hide();
                $(".top-bar>.register-login").show();
            }
        }
    });
}

$(document).ready(function () {
    //请求，获取是否登录、最新的5个房屋、地区信息
    $.get('/api/v1/house/index', function (data) {
        //是否登录
        if (data.errno == RET.OK) {
            $(".top-bar>.user-info").show().find('.user-name').text(data.data.name);
        } else {
            $(".top-bar>.register-login").show();
        }
        //最新5个房屋
        var html = template('house_list', {hlist: data.data.hlist});
        $('.swiper-wrapper').html(html);
        //图片播放
        var mySwiper = new Swiper('.swiper-container', {
            loop: true,
            autoplay: 2000,
            autoplayDisableOnInteraction: false,
            pagination: '.swiper-pagination',
            paginationClickable: true
        });
    });

    //查询地区信息
    $.get('/api/v1/house/areas',function (data) {
        //地区
        var html=template('area_list',{area_list:data.data});
        $('.area-list').html(html);
        $(".area-list a").click(function (e) {
            $("#area-btn").html($(this).html());
            $(".search-btn").attr("area-id", $(this).attr("area-id"));
            $(".search-btn").attr("area-name", $(this).html());
            $("#area-modal").modal("hide");
        });
    });


    $('.modal').on('show.bs.modal', centerModals);      //当模态框出现的时候
    $(window).on('resize', centerModals);               //当窗口大小变化的时候
    $("#start-date").datepicker({
        language: "zh-CN",
        keyboardNavigation: false,
        startDate: "today",
        format: "yyyy-mm-dd"
    });
    $("#start-date").on("changeDate", function () {
        var date = $(this).datepicker("getFormattedDate");
        $("#start-date-input").val(date);
    });
})
