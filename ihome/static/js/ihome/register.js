function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

var imageCodeId = "";

function generateUUID() {
    var d = new Date().getTime();
    if(window.performance && typeof window.performance.now === "function"){
        d += performance.now(); //use high-precision timer if available
    }
    var uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        var r = (d + Math.random()*16)%16 | 0;
        d = Math.floor(d/16);
        return (c=='x' ? r : (r&0x3|0x8)).toString(16);
    });
    return uuid;
}

//生成图片验证码
function generateImageCode() {
    imageCodeId = generateUUID();
    var url = "/api/v1/image_codes/"+ imageCodeId
    $('#image_code').attr('src',url);
}

//发送短信验证码
function sendSMSCode() {
    //点击后不可再点击
    $(".phonecode-a").removeAttr("onclick");
    $('#phone-code-err').hide();
    //获取手机号
    var mobile = $("#mobile").val();
    if (!mobile) {
        $("#mobile-err span").html("请填写正确的手机号！");
        $("#mobile-err").show();
        $(".phonecode-a").attr("onclick", "sendSMSCode();");
        return;
    }
    //获取图片验证码
    var imageCode = $("#imagecode").val();
    if (!imageCode) {
        $("#image-code-err span").html("请填写验证码！");
        $("#image-code-err").show();
        $(".phonecode-a").attr("onclick", "sendSMSCode();");
        return;
    }
    var req_data = {
        image_code: imageCode,
        image_code_id: imageCodeId
    }
    //如果手机号、图片验证码都已经填写，则发起ajax请求，让服务器向指定手机号发送短信验证码
    $.get("/api/v1/sms_codes/" + mobile, req_data, function (resp) {
        // 回调函数中的resp是后端返回的json字符串，通过ajax将这个字符串转换成js对象
        // 所以这里的resp为ajax转换后的对象
        if (resp.errno == "0") {
            // 表示发送成功
            var num = 60;
            var timer = setInterval(function () {
                if (num > 1) {
                    // 修改倒计时的文本内容
                    $(".phonecode-a").html(num + "s");
                    num -= 1
                } else {
                    $(".phonecode-a").html("获取验证码");
                    $(".phonecode-a").attr("onclick", "sendSMSCode();");
                    clearInterval(timer)
                }
            }, 1000, 60)
        } else {
            alert(resp.errmsg);
            $(".phonecode-a").attr("onclick", "sendSMSCode();");
        }

    });

}

$(document).ready(function() {
    generateImageCode();
    $("#mobile").focus(function(){
        $("#mobile-err").hide();
    });
    $("#imagecode").focus(function(){
        $("#image-code-err").hide();
    });
    $("#phonecode").focus(function(){
        $("#phone-code-err").hide();
    });
    $("#password").focus(function(){
        $("#password-err").hide();
        $("#password2-err").hide();
    });
    $("#password2").focus(function(){
        $("#password2-err").hide();
    });
    $(".form-register").submit(function(e){
        //验证填写的数据是否合法
        //....
        //调用api完成注册
        $('#result-err').hide();
        e.preventDefault();
        var mobile = $("#mobile").val();
        var phonecode = $("#phonecode").val();
        var password = $("#password").val();
        var password2 = $("#password2").val();
        if(!mobile){
            $("#mobile-err span").html("请填写正确的手机号！");
            $("#mobile-err").show();
            return;
        }
        if(!phonecode){
            $("#phone-code-err span").html("请填写短信验证码！");
            $("#phone-code-err").show();
            return;
        }
        if(!password){
            $("#password-err span").html("请填写密码！");
            $("#password-err").show();
            return;
        }
        if(password != password2){
            $("#password2-err span").html("两次密码不一致！");
            $("#password2-err").show();
            return;
        }

       // 调用ajax向后端发送注册请求
        var req_data = {
            mobile:mobile,
            phonecode:phonecode,
            password:password,
            password2:password

        };
        var req_json = JSON.stringify(req_data)
        $.ajax({
            url:"/api/v1/users",
            type:"post",
            data:req_json,
            contentType:"application/json",
            dataType: "json",
            headers:{
              "X-CSRFToken":getCookie("csrf_token")
            },
            success: function (resp) {
                if (resp.errno== "0"){
                    // 注册成功，即跳转到主页
                    location.href = "/index.html";
                }else {
                    alert(resp.errmsg);
                }

            }

        });

    });
})