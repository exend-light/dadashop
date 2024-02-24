
from django.urls import path
from . import views

urlpatterns = [
    # path('register/',views.register),前端要求写为'register/'

    path('register',views.register),
    path('activation',views.activation),
    path('sms/code',views.smscode),
    path('check',views.check),
    path('login',views.login),

# var username=window.localStorage.getItem('dashop_user')
#    //页面加载完成加载用户列表
#    $(function(){
# 	   loadUserList();
#    })
# 	//加载用户列表：
# 	function loadUserList(){
# 		$.ajax({
# 			url:baseUrl+'/v1/users/'+username+'/address',


    path('<str:username>/address',views.AddressView.as_view()),
    path('<str:username>/address/<int:id>',views.AddressView.as_view()),

]

