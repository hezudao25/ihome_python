function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function() {
    $("#mobile").focus(function(){
        $("#mobile-err").hide();
    });
    $("#password").focus(function(){
        $("#password-err").hide();
    });
    $(".form-login").submit(function(e){
        $('#result-err').hide();

        //阻止表单的提交，而改为使用ajax提交
        e.preventDefault();
        var mobile = $("#mobile").val();
        var passwd = $("#password").val();
        if (!mobile) {
            $("#mobile-err span").html("请填写正确的手机号！");
            $("#mobile-err").show();
            return;
        } 
        if (!passwd) {
            $("#password-err span").html("请填写密码!");
            $("#password-err").show();
            return;
        }
        //提交
  var data = {
    mobile:mobile,
    password:passwd
}
// 将data数据转换成json字符串
var jsonData = JSON.stringify(data);
$.ajax({
    url:"/api/v1/login",
    type:"post",
    data:jsonData,
    contentType:"application/json",
    dataType:"json",
    headers:{
        "X-CSRFToken":getCookie("csrf_token")
    },
    success:function (data) {
        if(data.errno == "0"){
            // 则代表登录成功，跳转到主页
            location.href = "/";
        }
        else {
            // 登录不成功则在页面中显示错误信息
            $("#password-err span").html(data.errmsg);
            $("#password-err").show();
        }
    }
});
});
});
