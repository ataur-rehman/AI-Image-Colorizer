from django.contrib import admin
from django.urls import path

from .views import *

urlpatterns = [

    path('',getting_started, name='start_page'),    
    path('colorize-result/<int:image_id>/', colorize_result, name='colorize_result'),  # New URL
    path('update_membership', update_membership, name='update_membership'),
    path('upload-image/', upload_image2, name='upload_image2'),
    path('photo_editor/', photo_editor, name='photo_editor'),
    path('colorizer/',colorizer_view, name='colorizer'),
    path('photo-editor/<int:image_id>/', photo_editor, name='photo_editor'),
    path('signup' , signup,  name = 'signup'),
    path('login/' , login , name = 'login'),
    path('dashboard/', dashboard, name='dashboard'),
    path('upload/', upload_image, name = 'upload_image'),
    path('history' , show_history, name='show_history'),
    path('logout/', getting_started, name='logout'),
    path('edit/<int:image_id>/', edit_image, name='edit_image'),
    path('edit-image-history/<int:image_id>/', edit_image_page_history, name='edit_image_page_history'),
    path('edit-image-upload/<int:image_id>/', edit_image_page_upload, name='edit_image_page_upload'),
    path('save-edited/<int:image_id>/', save_edited_image, name='save_edited'),
    path('uploads/', show_uploads, name='show_uploads'),
    path('save-edit2/', save_edit2, name='save_edit2'),


]
