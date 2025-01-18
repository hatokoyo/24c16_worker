from django.urls import path
from django.urls import re_path
from .views import koban,delete_Koban,nipposuccess,nippohistory,nippohome,delete_Sagyo,nippologin,nippoedit,nippoinformation,nipposettings,nippodetail,nippokoban,nippomultiple,nippoerror,nipposuccess_multiple,nippohelp,nippoedit_multiple,nippodetail_multiple,approval,update_status
urlpatterns = [
    path("", delete_Sagyo,name='delete_sagyo'),

    path("koban/", koban,name='koban_update'),
    path("deletekoban/", delete_Koban,name='koban_delete'),

    path('nippohome/', nippohome, name='nhome'),  # 日報作成のURL
    path('nippologin/', nippologin, name='nlogin'),  # 日報作成のURL
    path('nippohistory/', nippohistory, name='nhistory'),  # 日報作成のURL
    path('nipposuccess/', nipposuccess, name='nsuccess'),  # 日報作成のURL
    path('nipposuccess_multiple/', nipposuccess_multiple, name='nsuccess_multiple'),  # 日報作成のURL
    path('nippoinformation/', nippoinformation, name='ninformation'),  # 日報作成のURL
    path('nipposettings/', nipposettings, name='nsettings'),  # 日報作成のURL
    path('nippokoban/', nippokoban, name='nkoban'),  # 日報作成のURL
    path('nippomultiple/', nippomultiple, name='nmultiple'),  # 日報作成のURL
    path('nippoerror/', nippoerror, name='nerror'),  # 日報作成のURL
    path('nippohelp/', nippohelp, name='nhelp'),  # 日報作成のURL

    path('nippoedit/<int:idx>/', nippoedit, name='nedit'),
    path('nippodetail/<int:idx>/', nippodetail, name='ndetail'),

    re_path(r'^nippoedit_multiple/(?P<idx>[0-9\-]+)/$', nippoedit_multiple, name='nedit_multiple'),
    re_path(r'^nippodetail_multiple/(?P<idx>[0-9\-]+)/$', nippodetail_multiple, name='ndetail_multiple'),

    path('update_status/', update_status, name='update_status'),
    path('nippoapproval/', approval, name='napproval'),
]


