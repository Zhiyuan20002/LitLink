# urls.py
from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('upload_pdf/', views.upload_pdf, name='upload_pdf'),
    path('auto_fill_stream/', views.auto_fill_stream, name='auto_fill_stream'),
    path('save_paper/', views.save_paper, name='save_paper'),
    path('delete_paper/', views.delete_paper, name='delete_paper'),
    path('get_papers/', views.get_papers, name='get_papers'),
    path('update_paper/', views.update_paper, name='update_paper'),
    path('delete_paper/', views.delete_paper, name='delete_paper'),
    path('generate_avatar/', views.generate_avatar, name='generate_avatar'),
    path('get_summary_and_flashcards/<str:paper_id>/', views.get_summary_and_flashcards,
         name='get_summary_and_flashcards'),
    path('update_summary/', views.update_summary, name='update_summary'),
    path('generate_flashcards/', views.generate_flashcards, name='generate_flashcards'),
    path('update_flashcard/', views.update_flashcard, name='update_flashcard'),
    path('delete_flashcard/', views.delete_flashcard, name='delete_flashcard'),
    path('load_messages/', views.load_message, name='load_messages'),
    path('send_message/', views.send_message, name='send_message'),
    path('clear_messages/', views.clear_messages, name='clear_messages'),
    path('get_flashcard_highlights/<str:paper_id>/', views.get_flashcard_highlights, name='get_flashcard_highlights'),
    path('create_flashcard/', views.create_flashcard, name='create_flashcard'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
