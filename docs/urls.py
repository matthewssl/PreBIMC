from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.HomeView.as_view(), name='home'),
    path('add_doc/', views.DocumentCreate.as_view(), name='add_doc'),
    path('<int:pk>/update/', views.DocumentUpdate.as_view(), name='update_doc'),
    path('add_files/', views.HoldDocCreate.as_view(), name='add_files'),
    path('search/', views.search_documents, name='search_documents'),
    path('mupload/', views.FileFieldView.as_view(), name='multi_upload'),
    path('<pk>/editQ/', views.HoldDocUpdate.as_view(), name='Update_Q'),
    path('getcontent/', views.update_content_field, name='get_pdf_content'),
    path('fitz/', views.fitz_pdf_view, name='usefitz'),
    path('<pk>/test/', views.TestView.as_view(), name='test'),
    path('showpdf/', views.show_pdf, name='show_pdf'),
    path('edit_type/', views.add_edit_doctype, name='edit_type'),
    path('doctype/', views.EnterDoctype.as_view(), name='enter_doctype'),

]

    #   path('miner/', views.miner_pdf_view, name='miner'),
    #