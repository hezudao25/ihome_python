//获取用户信息，判断是否进行过实名认证
$.get('/api/v1/users/houses',function (data) {
    if(data.errno==RET.OK){
        //已经完成实名认证
        $('#houses-list').show();
        var html=template('house_list',{hlist:data.data.houses});
        $('#houses-list').append(html);
         $('.auth-warn').hide();
    }else if(data.errno==RET.USERERR){
        //未实名认证
        $('.auth-warn').show();
    }
});
