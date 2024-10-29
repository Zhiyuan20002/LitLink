# from django.http import HttpResponse
#
#
# def index(request):
#     return HttpResponse("Hello, world. You're at the polls index.")

from django.http import JsonResponse
from django.views import View
from django.core.files.storage import FileSystemStorage
from django.db import IntegrityError
from .models import PDFHighlight
import json
import os
from PyPDF2 import PdfFileReader


# class PDFUploadView(View):
#     def post(self, request):
#         # Handling PDF file upload
#         if 'file' not in request.FILES:
#             return JsonResponse({
#                 "status": "error",
#                 "message": "No file provided"
#             }, status=400)
#
#         pdf_file = request.FILES['file']
#         fs = FileSystemStorage()
#         filename = fs.save(pdf_file.name, pdf_file)
#         file_url = fs.url(filename)
#         file_path = os.path.join(fs.location, filename)
#
#         try:
#             pdf_reader = PdfFileReader(file_path)
#             num_pages = pdf_reader.numPages
#         except Exception as e:
#             return JsonResponse({
#                 "status": "error",
#                 "message": f"Failed to read PDF file: {str(e)}"
#             }, status=500)
#
#         response_data = {
#             "status": "success",
#             "message": "PDF uploaded successfully",
#             "fileName": filename,
#             "fileUrl": file_url,
#             "fileSize": pdf_file.size,
#             "numPages": num_pages
#         }
#         return JsonResponse(response_data, status=200)


class PDFHighlightView(View):
    def post(self, request):
        # Handling highlight information
        try:
            data = json.loads(request.body)
            file_name = data.get("fileName")
            highlight_data = data.get("highlightData", [])

            if not file_name or not highlight_data:
                return JsonResponse({
                    "status": "error",
                    "message": "Invalid data format"
                }, status=400)

            # Save highlight data to database
            try:
                pdf_highlight = PDFHighlight(file_name=file_name)
                sentence = Sentence(content=highlight_data)
                sentence.save()
                pdf_highlight.save()
            except IntegrityError as e:
                return JsonResponse({
                    "status": "error",
                    "message": f"Failed to save highlight data: {str(e)}"
                }, status=500)

            response_data = {
                "status": "success",
                "message": "Highlight data saved successfully",
                "fileName": file_name,
                "highlightData": highlight_data
            }
            return JsonResponse(response_data, status=200)

        except json.JSONDecodeError:
            return JsonResponse({
                "status": "error",
                "message": "Invalid JSON format"
            }, status=400)
        except Exception as e:
            return JsonResponse({
                "status": "error",
                "message": f"An error occurred: {str(e)}"
            }, status=500)


