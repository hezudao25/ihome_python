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

function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function () {
    $('.modal').on('show.bs.modal', centerModals);      //当模态框出现的时候
    $(window).on('resize', centerModals);
    //获取房东的所有订单
    $.get('/api/v1/user/orders?role=landlord', function (data) {
        if (RET.SESSIONERR == data.errno) {
            location.href="login.html"
        }else if (RET.OK == data.errno){
            var html = template('orders-list-tmpl', {orders: data.data.orders});
            $('.orders-list').html(html);
            //当页面元素存在后，再绑定接单、拒单事件
            //接单
            $(".order-accept").on("click", function () {
                var orderId = $(this).parents("li").attr("order-id");
                $(".modal-accept").attr("order-id", orderId);
            });
            //拒单
            $(".order-reject").on("click", function () {
                var orderId = $(this).parents("li").attr("order-id");
                $(".modal-reject").attr("order-id", orderId);
            });
        }
    });

    //确定接单
    $('.modal-accept').click(function () {
        var order_id = $(this).attr('order-id');
         $.ajax({
                    url:"/api/v1/orders/"+order_id+"/status",
                    type:"PUT",
                    data:'{"action":"accept"}',
                    contentType:"application/json",
                    dataType:"json",
                    headers:{
                        "X-CSRFTOKEN":getCookie("csrf_token"),
                    },
                    success:function (resp) {
                        if ("4101" == resp.errno) {
                            location.href = "/login.html";
                        } else if ("0" == resp.errno) {
                            $(".orders-list>li[order-id="+ order_id +"]>div.order-content>div.order-text>ul li:eq(4)>span").html("已接单");
                            $("ul.orders-list>li[order-id="+ order_id +"]>div.order-title>div.order-operate").hide();
                            $("#accept-modal").modal("hide");
                        }
                    }
                });

    });
    //拒单-确定
    $('.modal-reject').click(function () {
       var orderId = $(this).attr("order-id");
    var reject_reason = $("#reject-reason").val();
    if (!reject_reason) return;
    var data = {
        action: "reject",
        reason:reject_reason
    };
    $.ajax({
        url:"/api/v1/orders/"+orderId+"/status",
        type:"PUT",
        data:JSON.stringify(data),
        contentType:"application/json",
        headers: {
            "X-CSRFTOKEN":getCookie("csrf_token")
        },
        dataType:"json",
        success:function (resp) {
            if ("4101" == resp.errno) {
                location.href = "/login.html";
            } else if ("0" == resp.errno) {
                $(".orders-list>li[order-id="+ orderId +"]>div.order-content>div.order-text>ul li:eq(4)>span").html("已拒单");
                $("ul.orders-list>li[order-id="+ orderId +"]>div.order-title>div.order-operate").hide();
                $("#reject-modal").modal("hide");
            }
        }
    });

    });
});