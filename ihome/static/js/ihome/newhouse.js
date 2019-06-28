function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

//查询地区信息
$.get('/api/v1/house/areas',function (data) {
    //地区
    var area_html=template('area_list',{area_list:data.data});
    $('#area-id').html(area_html);
});

//查询设施信息
$.get('/api/v1/house/facility',function (data) {
    //设施
    var facility_html=template('facility_list',{facility_list:data.data});
    $('.house-facility-list').html(facility_html);
});

//为房屋表单绑定提交事件
$('#form-house-info').submit(function (e) {
    e.preventDefault();
    $('.error-msg text-center').hide();
    var data = {};
    $("#form-house-info").serializeArray().map(function (x) { data[x.name] = x.value });
    var facility = [];
    $(":checked[name=facility]").each(function (index, x) {facility[index] = $(x).val()});
    data.facility = facility;
    $.ajax({
    url:"/api/v1/house/info",
    type:"post",
    contentType:"application/json",
    data:JSON.stringify(data),
    dataType:"json",
    headers:{
        "X-CSRFToken": getCookie("csrf_token")
    },
    success: function (resp) {
        if (resp.errno == RET.SESSIONERR){
            location.href = "/login.html"
        } else if (resp.errno == RET.OK){
            // 将设备设施表单隐藏
            $("#form-house-info").hide();

            // 将上传房屋图片表单显示
            $("#form-house-image").show();

            // 设置上传房屋图片表单中的house_id
            $("#house-id").val(resp.data.house_id);
        }else {
            $('.error-msg text-center').show().find('span').html(ret_map[data.errno]);
        }
    }
    },"json");

});

//为图片表单绑定事件
$('#form-house-image').submit(function (e) {
    e.preventDefault();
    $(this).ajaxSubmit({
        url: "/api/v1/house/image",
        type: "post",
        dataType: "json",
        headers:{
        "X-CSRFToken": getCookie("csrf_token")
    },
        success: function (data) {
            if (data.errno == "4101") {
                location.href = "/login.html"
            } else if (data.errno == RET.OK) {
                $('.house-image-cons').append('<img src="' + data.data.image_url + '"/>');
            } else {
                alert(data.errmsg);
            }
        }
    });
});
