function hrefBack() {
    history.go(-1);
}

function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

function decodeQuery() {
    var search = decodeURI(document.location.search);
    return search.replace(/(^\?)/, '').split('&').reduce(function (result, item) {
        values = item.split('=');
        result[values[0]] = values[1];
        return result;
    }, {});
}

function showErrorMsg() {
    $('.popup_con').fadeIn('fast', function () {
        setTimeout(function () {
            $('.popup_con').fadeOut('fast', function () {
            });
        }, 1000)
    });
}

$(document).ready(function () {
    $.get("/api/v1/session", function(resp) {
    if ("0" != resp.errno) {
        location.href = "/login.html";
    }
}, "json");

    $(".input-daterange").datepicker({
        format: "yyyy-mm-dd",
        startDate: "today",
        language: "zh-CN",
        autoclose: true
    });
    $(".input-daterange").on("changeDate", function () {
        var startDate = $("#start-date").val();
        var endDate = $("#end-date").val();

        if (startDate && endDate && startDate > endDate) {
            showErrorMsg();
        } else {
            var sd = new Date(startDate);
            var ed = new Date(endDate);
            days = (ed - sd) / (1000 * 3600 * 24) + 1;
            var price = $(".house-text>p>span").html();
            var amount = days * parseFloat(price);
            $(".order-amount>span").html(amount.toFixed(2) + "(共" + days + "晚)");
        }
    });

    var hid = decodeQuery()['hid'];
    $.get('/api/v1/order/house/' + hid, function (data) {
        var html = template('house_info', {house: data.data.house});
        $('.house-info').html(html);
    });
    //提交订单
    $('.submit-btn').click(function () {
       if ($(".order-amount>span").html()) {
        $(this).prop("disabled", true);
         var hid = decodeQuery()['hid']
        var startDate = $("#start-date").val();
        var endDate = $("#end-date").val();
        var data = {
            "house_id":hid,
            "start_date":startDate,
            "end_date":endDate
        };
        $.ajax({
            url:"/api/v1/orders",
            type:"POST",
            data: JSON.stringify(data),
            contentType: "application/json",
            dataType: "json",
            headers:{
                "X-CSRFTOKEN":getCookie("csrf_token"),
            },
            success: function (resp) {
                if ("4101" == resp.errno) {
                    location.href = "/login.html";
                } else if ("4004" == resp.errno) {
                    showErrorMsg("房间已被抢定，请重新选择日期！");
                } else if ("0" == resp.errno) {
                    location.href = "/orders.html";
                }
            }
        });
    }

    });
})
