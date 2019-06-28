function showSuccessMsg() {
    $('.popup_con').fadeIn('fast', function () {
        setTimeout(function () {
            $('.popup_con').fadeOut('fast', function () {
            });
        }, 1000)
    });
}

function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(function () {
    $.get('/api/v1/users/profile', function (data) {
        // 用户未登录
            if (data.errno == RET.SESSIONERR) {
                location.href = "/login.html";
            }
            // 查询到了用户的信息
            else if (data.errno == "0") {
                $('#user-avatar').attr('src', data.user.avatar);
                $('#user-name').val(data.user.name);
            }
    });


$('#form-avatar').submit(function (e) {
    $('#error_msg1').hide();
    e.preventDefault();
    $(this).ajaxSubmit({
        url: "/api/v1/users/avatar",
        type: "post",
        dataType: "json",
        headers:{
            "X-CSRFToken":getCookie("csrf_token")
        },
        success: function (data) {
            if (data.errno == RET.OK) {
                $('#user-avatar').attr('src',data.data.avatar_url);
            } else {
                $('#error_msg1').show();
            }
        }
    });
    return false;
});

$('#form-name').submit(function (e) {
    $('#error_msg2').hide();
     e.preventDefault();
     var name = $("#user-name").val();
      var data = {
            name:name
        };
      var jsonData = JSON.stringify(data);
      $.ajax({
            url:"/api/v1/users/name",
            type:"post",
            data:jsonData,
            contentType:"application/json",
            dataType:"json",
            headers:{
                "X-CSRFToken": getCookie("csrf_token")
            },
            success:function (data) {
            if(data.errno==RET.OK){
                //
                showSuccessMsg()
            }else{
                $('#error_msg2').show();
          }
       }
    });
    return false;
});
});