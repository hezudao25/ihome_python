function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}
function logout() {
     $.ajax({
        url:"/api/v1/loginout",
        type:"delete",
        headers:{
            "X-CSRFToken":getCookie("csrf_token")
        },
        dataType:"json",
        success:function (resp) {
            if (resp.errno == "0"){
                location.href = "/"
            }
        }
    });
}

$(document).ready(function(){
   $.ajax({
        url:"/api/v1/users/profile",
        type:"get",
        headers:{
            "X-CSRFToken":getCookie("csrf_token")
        },
        dataType:"json",
        success:function (data) {
            // 用户未登录
            if (data.errno == RET.SESSIONERR) {
                location.href = "/login.html";
            }
            // 查询到了用户的信息
            else if (data.errno == "0") {
                $('#user-avatar').attr('src', data.user.avatar);
                $('#user-name').html(data.user.name);
                $('#user-mobile').text(data.user.phone);
            }
        }
    });
})