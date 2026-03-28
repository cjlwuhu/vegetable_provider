function bindEmailCodeClick(){
    //用#获取id=send-code的字符，用.send-code为获得class=send-code
    $("#send-code").click(function (event){
        event.preventDefault();
        let that = $(this);

        //1,获取用户输入邮箱
        let email = $("#reg-email").val();
        let emailReg = /^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$/;
        if(!emailReg.test(email)){
            alert("请输入合法邮箱!");
            return;
        }

        //2,倒计时过程，取消点击事件
        that.off('click');


        //3,倒计时
        let countdown = 6;
        that.text(countdown+'s');
        let timer = setInterval(function(){
            countdown-=1;
            that.text(countdown+'s');
            if(countdown <= 0){
                that.text("获取验证码");
                clearInterval(timer);

                //重新绑定点击事件
                bindEmailCodeClick();
            }
        },1000 )

        //4,发送ajax请求
        $.get({
            url:"/email/code",
            data:{"email":email},
            success:function(result){
                console.log(result);
            }
        })
    });
}

function bindRegisterEvent(){
    $("#submit-btn").click(function(event){
        event.preventDefault();

        let email = $("#reg-email").val();
        let username = $("#reg-username").val();
        let password = $("#reg-password").val();
        let code = $("#reg-code").val();
        let confirm_password = $("#reg-confirm-password").val();
        if(confirm_password != password){
            alert("密码输入不一致!");
            return;
        }

        $.post({
            url:"/register",
            data:{email,code,username,password},
            success:function (resp){
                if(resp['result'] == true){
                    location.href ='/login';
                }
                else {
                    let message = resp['message'];
                    alert(message);
                }
            }
        })
    })
}

//整个网页加载之后
$(function (){
    bindEmailCodeClick();
    bindRegisterEvent();
})