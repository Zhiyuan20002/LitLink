import json
import uuid
import os
import copy
from django.utils import timezone
from uuid import UUID
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.http import StreamingHttpResponse
import fitz
from . import llm_process
from .models import PdfDocument, FlashCard, User, ChatMessage
from django.shortcuts import get_object_or_404
from django.utils.decorators import sync_and_async_middleware


@csrf_exempt
def get_papers(request):
    if request.method == 'GET':
        # 查询所有 PdfDocument，并统计每个文档的 FlashCard 数量
        all_papers = PdfDocument.objects.all()

        # 构建 paperData 列表
        paper_data_list = [
            {
                'key': str(paper.paper_id),
                'name': paper.name,
                'highlightCardCount': FlashCard.objects.filter(pdf_document=paper).count(),
                'createdAt': paper.create_time.strftime('%Y-%m-%d'),
                'pdfUrl': os.path.join("http://localhost:8000", "media", "paper_file", str(paper.pdf_file)),
                'description': paper.detail
            }
            for paper in all_papers
        ]

        return JsonResponse({'paperData': paper_data_list}, status=200)
    return JsonResponse({'error': 'Invalid request method'}, status=400)


@csrf_exempt
def upload_pdf(request):
    if request.method == 'POST' and request.FILES.get('pdf_file'):
        pdf_file = request.FILES['pdf_file']
        paper_id = uuid.uuid4()
        file_name = f"{paper_id}.pdf"
        file_path = os.path.join('paper_file', file_name)

        # 保存文件到 media 目录
        default_storage.save(file_path, pdf_file)

        print(f"INFO: File uploaded successfully: {file_name}")

        return JsonResponse({'message': 'File uploaded successfully', 'file_name': file_name}, status=201)
    return JsonResponse({'error': 'File not found or invalid request method'}, status=400)


@csrf_exempt
def auto_fill_stream(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        file_name = data.get("file_name")
        file_path = os.path.join(settings.MEDIA_ROOT, 'paper_file', file_name)

        # 使用流式响应逐步返回 AI 生成的内容
        response = StreamingHttpResponse(
            llm_process.upload_process(file_path),
            content_type='text/event-stream'
        )
        response['Cache-Control'] = 'no-cache'
        response['X-Accel-Buffering'] = 'no'  # 防止代理缓存
        return response
    return JsonResponse({'error': 'AI fill not run!'}, status=400)


@csrf_exempt
def save_paper(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        # 计算 PDF 页数
        file_name = data.get("FileName")
        full_pdf_path = os.path.join(settings.MEDIA_ROOT, 'paper_file', file_name)
        pdf_document = fitz.open(full_pdf_path)
        num_pages = pdf_document.page_count
        pdf_document.close()

        # 存储 PDF 数据
        PdfDocument.objects.create(
            name=data.get("name"),
            detail=data.get("description"),
            summary=data.get("summary"),
            pdf_file=data.get("FileName"),
            num_pages=num_pages
        )

        all_papers = PdfDocument.objects.all()

        # 构建 paperData 列表
        paper_data_list = [
            {
                'key': str(paper.paper_id),
                'name': paper.name,
                'highlightCardCount': FlashCard.objects.filter(pdf_document=paper).count(),
                'createdAt': paper.create_time.strftime('%Y-%m-%d'),
                'pdfUrl': os.path.join("http://localhost:8000", "media", "paper_file", str(paper.pdf_file)),
                'description': paper.detail
            }
            for paper in all_papers
        ]

        # 返回 JSON 响应
        return JsonResponse({'message': 'Paper saved successfully', 'paperData': paper_data_list}, status=201)
    return JsonResponse({'error': 'Invalid request'}, status=400)


@csrf_exempt
def delete_paper(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        file_name = data.get('path')
        file_path = os.path.join(settings.MEDIA_ROOT, 'paper_file', file_name)

        # 删除文件
        if os.path.exists(file_path):
            os.remove(file_path)
            return JsonResponse({'message': 'File deleted successfully'}, status=200)
        else:
            return JsonResponse({'error': 'File not found'}, status=404)
    return JsonResponse({'error': 'Invalid request'}, status=400)


@csrf_exempt
def update_paper(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        paper_id = data.get("id")
        name = data.get("name")
        description = data.get("description")

        try:
            paper = PdfDocument.objects.get(pk=paper_id)
            paper.name = name
            paper.detail = description
            paper.save()

            return JsonResponse({'message': 'Paper updated successfully'}, status=200)
        except PdfDocument.DoesNotExist:
            return JsonResponse({'error': 'Paper not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=400)


@csrf_exempt
def delete_paper(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        paper_id = data.get("id")

        try:
            # 获取 PdfDocument 对象
            paper = PdfDocument.objects.get(pk=paper_id)

            # 获取文件路径
            file_path = os.path.join(settings.MEDIA_ROOT, 'paper_file', str(paper.pdf_file))

            # 删除数据库中的记录
            paper.delete()

            # 删除关联的文件
            if os.path.exists(file_path):
                os.remove(file_path)

            return JsonResponse({'message': 'Paper and associated file deleted successfully'}, status=200)
        except PdfDocument.DoesNotExist:
            return JsonResponse({'error': 'Paper not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=400)


@csrf_exempt
def generate_avatar(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            content = data.get("content")

            if not content:
                return JsonResponse({'error': 'Content is required to generate an avatar.'}, status=400)

            # 调用头像生成函数
            avatar_url = llm_process.generate_avatar(content)

            return JsonResponse({'avatar_url': avatar_url}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=400)


# 获取文档的摘要和学习卡片
def get_summary_and_flashcards(request, paper_id):
    print("Received paper_id:", paper_id)
    if request.method == 'GET':
        # 获取对应的 PdfDocument 对象
        pdf_document = get_object_or_404(PdfDocument, paper_id=paper_id)

        # 获取 summary 和 flashcards
        summary = pdf_document.summary
        flashcards = pdf_document.flashcards.all().values(
            'flashcard_id', 'title', 'content', 'status', 'highlight_by', 'notes', 'ai_analysis', 'related_to',
        )

        all_related_to = []
        for card in flashcards:
            related_to = card.get('related_to', [])
            all_related_to = merge_unique_lists(all_related_to, related_to)
        print(f"INFO: All related_to: {all_related_to}")

        related_uuids = [UUID(flashcard_id) for flashcard_id in all_related_to]
        history_flashcards = FlashCard.objects.filter(flashcard_id__in=related_uuids)
        history_highlights = [
            {
                'number': str(history_card.flashcard_id),
                'title': history_card.title,
                'content': history_card.content,
                'status': history_card.status,
                'highlightBy': history_card.highlight_by,
                'Notes': history_card.notes,
                'AIAnalysis': history_card.ai_analysis,
                'relatedTo': history_card.pdf_document.name,
                'pdfUrl': os.path.join("http://localhost:8000", "media", "paper_file",
                                       str(history_card.pdf_document.pdf_file)),
            }
            for idx, history_card in enumerate(history_flashcards)
        ]

        # 返回数据，确保 flashcards 和 historyHighlights 不为空
        data = {
            'summary': summary if summary else "",  # 如果 summary 为空，返回空字符串
            'flashcards': list(flashcards) if flashcards.exists() else [],  # 如果没有 FlashCard，返回空列表
            'historyHighlights': history_highlights if history_highlights else [],  # 如果没有历史高亮，返回空列表
        }
        print("Returning flashcards:", data["flashcards"])
        print("Returning historyHighlights:", data["historyHighlights"])
        return JsonResponse(data, safe=False)


@csrf_exempt
def update_summary(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        paper_id = data.get("paper_id")
        new_summary = data.get("summary", "")

        # 查找并更新 PdfDocument 的 summary 字段
        pdf_document = get_object_or_404(PdfDocument, paper_id=paper_id)
        pdf_document.summary = new_summary
        pdf_document.save()

        return JsonResponse({'message': 'Summary updated successfully'}, status=200)
    return JsonResponse({'error': 'Invalid request method'}, status=400)


def build_related_to(flashcard_id):
    # 根据 flashcard_id 获取当前 flashcard 对象
    flashcard = get_object_or_404(FlashCard, flashcard_id=flashcard_id)
    this_related_to = []

    # 获取所有其他文档的 flashcards（排除当前文档的 flashcards）
    other_flashcards = FlashCard.objects.exclude(pdf_document=flashcard.pdf_document)

    # 将当前 flashcard 的特征向量转换为数组
    current_embedding = np.array(flashcard.feature_data).reshape(1, -1)

    # 定义相似度阈值，用于判断两者是否相似
    similarity_threshold = 0.7

    for other_flashcard in other_flashcards:
        # 获取其他 flashcard 的特征向量并转换为数组
        other_embedding = np.array(other_flashcard.feature_data).reshape(1, -1)

        # 计算余弦相似度
        similarity = cosine_similarity(current_embedding, other_embedding)[0][0]

        # 如果相似度大于阈值且不在当前列表中，则添加到 related_to 列表中
        if similarity >= similarity_threshold and other_flashcard.flashcard_id not in this_related_to:
            this_related_to.append(str(other_flashcard.flashcard_id))
            print(f"Similarity: {similarity}")
            print(f"Related to: {this_related_to}")

            # 更新对方的 related_to 列表，添加当前 flashcard_id
            if flashcard.flashcard_id not in other_flashcard.related_to:
                other_related_to = other_flashcard.related_to
                print(f"INFO: Updating related_to for {other_flashcard.title}")
                print(f"Related to: {other_flashcard.related_to}")
                other_related_to.append(str(flashcard.flashcard_id))
                other_flashcard.related_to = other_related_to
                other_flashcard.save()

    print(f"INFO: Related flashcards for {flashcard.title}: {this_related_to}")
    return this_related_to


def merge_unique_lists(list1, list2):
    # 使用集合去重，并将结果转换为列表
    merged_list = list(set(list1) | set(list2))
    return merged_list


def back_all_flashcards(pdf_document, all_related_to):
    # 获取该论文现有的所有 FlashCard
    existing_flashcards = FlashCard.objects.filter(pdf_document=pdf_document)

    # 将现有的 FlashCard 数据添加到 flashcards 列表
    flashcards = [
        {
            'flashcard_id': card.flashcard_id,
            'title': card.title,
            'content': card.content,
            'status': card.status,
            'highlight_by': card.highlight_by,
            'notes': card.notes,
            'ai_analysis': card.ai_analysis,
            'related_to': card.related_to,
        }
        for card in existing_flashcards
    ]

    # 根据 all_related_to 找出所有的historyHighlights数据
    related_uuids = [UUID(flashcard_id) for flashcard_id in all_related_to]
    history_flashcards = FlashCard.objects.filter(flashcard_id__in=related_uuids)
    history_highlights = [
        {
            'number': history_card.flashcard_id,
            'title': history_card.title,
            'content': history_card.content,
            'status': history_card.status,
            'highlightBy': history_card.highlight_by,
            'Notes': history_card.notes,
            'AIAnalysis': history_card.ai_analysis,
            'relatedTo': history_card.pdf_document.name,
            'pdfUrl': os.path.join("http://localhost:8000", "media", "paper_file",
                                   str(history_card.pdf_document.pdf_file)),
        }
        for idx, history_card in enumerate(history_flashcards)
    ]

    return flashcards, history_highlights


@csrf_exempt
def generate_flashcards(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        paper_id = data.get("paper_id")

        # 获取对应的 PdfDocument 实例
        pdf_document = get_object_or_404(PdfDocument, paper_id=paper_id)

        # 调用生成 flashcard 的方法并获取生成结果
        file_name = str(pdf_document.pdf_file)
        file_path = os.path.join(settings.MEDIA_ROOT, 'paper_file', file_name)
        flashcards_json = llm_process.new_flashcard(file_path)

        # 解析生成的 JSON 数据
        flashcards_data = flashcards_json.get("key_sentences", [])

        all_related_to = []

        for card_data in flashcards_data:
            # 获取特征向量
            content = card_data.get("content")
            print(f"INFO: Generating embeddings for: {content}")
            embeddings = llm_process.get_embeddings(content)

            # 保存每个 flashcard 到数据库
            flashcard = FlashCard.objects.create(
                pdf_document=pdf_document,
                title=card_data.get("title"),
                content=card_data.get("content"),
                status='KEY_POINT',  # 默认状态
                highlight_by='AI',  # 假设高亮者为 AI
                notes="",
                ai_analysis=card_data.get("ai_analysis"),
                related_to=[],  # 默认为空列表
                feature_data=embeddings
            )

            this_related_to = build_related_to(flashcard.flashcard_id)
            all_related_to = merge_unique_lists(all_related_to, this_related_to)
            flashcard.related_to = this_related_to
            flashcard.save()

        flashcards, history_highlights = back_all_flashcards(pdf_document, all_related_to)

        # 返回包含 flashcards 和 historyHighlights 的 JSON 数据
        return JsonResponse({'flashcards': flashcards, 'historyHighlights': history_highlights}, status=200)
    return JsonResponse({'error': 'Invalid request method'}, status=400)


@csrf_exempt
def delete_flashcard(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        flashcard_id = data.get("flashcard_id")

        # 获取要删除的 FlashCard 实例
        flashcard = get_object_or_404(FlashCard, flashcard_id=flashcard_id)

        # 删除目标 FlashCard 前，收集受影响的关联卡片 ID
        affected_related_ids = flashcard.related_to  # 保留删除卡片的关联数据以更新其他卡片

        # 删除 FlashCard 实例
        flashcard.delete()

        # 更新受影响的关联卡片
        for related_id in affected_related_ids:
            print(f"INFO: Updating related_to for {related_id}")
            related_id = UUID(related_id)
            related_flashcard = get_object_or_404(FlashCard, flashcard_id=related_id)
            related_related_to = related_flashcard.related_to
            related_related_to.remove(flashcard_id)
            related_flashcard.related_to = related_related_to
            related_flashcard.save()

        # 返回包含 flashcards 和 historyHighlights 的 JSON 数据
        return JsonResponse({'status': 'success', 'message': 'Flashcard deleted successfully.'}, status=200)
    return JsonResponse({'error': 'Invalid request method'}, status=400)


@csrf_exempt
def update_flashcard(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        flashcard_id = data.get("flashcard_id")
        status = data.get("status")
        notes = data.get("notes")
        ai_analysis = data.get("ai_analysis")

        # 获取要更新的 FlashCard 实例
        flashcard = get_object_or_404(FlashCard, flashcard_id=flashcard_id)

        # 更新 FlashCard 实例的字段
        flashcard.status = status
        flashcard.notes = notes
        flashcard.ai_analysis = ai_analysis

        # 保存更新后的 FlashCard 实例
        flashcard.save()

        return JsonResponse({'status': 'success', 'message': 'Flashcard updated successfully.'}, status=200)
    return JsonResponse({'error': 'Invalid request method'}, status=400)


@csrf_exempt
def send_message(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        message_text = data.get('messages')
        document_id = data.get('document_id')
        agent = data.get('agent')

        pdf_document = PdfDocument.objects.get(paper_id=document_id)
        file_name = pdf_document.pdf_file
        file_path = os.path.join(settings.MEDIA_ROOT, 'paper_file', str(file_name))
        flashcards = FlashCard.objects.filter(pdf_document=pdf_document)
        flashcards_data = [
            {
                'title': card.title,
                'content': card.content,
                'status': card.status,
                'notes': card.notes,
                'ai_analysis': card.ai_analysis,
            }
            for card in flashcards
        ]
        user = User.objects.get(username="you")  # Example user; modify for actual authentication

        user_message = {
            'role': 'user',
            'content': message_text,
        }

        # 获取或创建消息记录
        chat_message, created = ChatMessage.objects.get_or_create(
            pdf_document=pdf_document,
            from_user=user,
            defaults={'content': [user_message], 'timestamp': timezone.now()}
        )

        if not created:
            chat_message.content.append(user_message)
            chat_message.timestamp = timezone.now()
            chat_message.save()

        # 准备传给 AI 的消息上下文
        all_content = copy.deepcopy(chat_message.content)
        print(f"INFO: All content: {all_content}")
        # 将content中所有的非user角色消息的名称替换为system并把新的消息内容存储到all_content中
        for contents in all_content:
            if contents['role'] != 'user':
                contents['role'] = 'system'

        print(f"INFO: New content: {chat_message.content}")

        ai_response_content = ""

        # 流式生成 AI 响应
        def ai_response_generator():
            nonlocal ai_response_content
            for response_chunk in llm_process.chat_with_ai(all_content, agent, file_path, flashcards_data):
                ai_response_content += response_chunk
                yield response_chunk

            ai_message = {'role': agent, 'content': ai_response_content}
            chat_message.content.append(ai_message)
            chat_message.timestamp = timezone.now()
            chat_message.save()
            print(f"{chat_message.content}")

        response = StreamingHttpResponse(ai_response_generator(), content_type="text/event-stream")
        response['Cache-Control'] = 'no-cache'

        return response

    return JsonResponse({'error': 'Invalid request method'}, status=400)


@csrf_exempt
def load_message(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        document_id = data.get('document_id')

        # 获取 PDF 文档实例
        pdf_document = PdfDocument.objects.get(paper_id=document_id)

        # 检查是否已有聊天记录
        try:
            chat_message = ChatMessage.objects.filter(pdf_document=pdf_document).order_by('timestamp').last()
            messages = chat_message.content if chat_message else []
            return JsonResponse({'messages': messages}, status=200)
        except PdfDocument.DoesNotExist:
            return JsonResponse({'messages': []}, status=200)

    return JsonResponse({'error': 'Invalid request method'}, status=400)


@csrf_exempt
def clear_messages(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        document_id = data.get('document_id')

        # 获取 PDF 文档实例
        pdf_document = PdfDocument.objects.get(paper_id=document_id)

        # 删除聊天记录
        try:
            chat_message = ChatMessage.objects.filter(pdf_document=pdf_document)
            chat_message.delete()
            return JsonResponse({'message': 'Messages cleared successfully'}, status=200)
        except PdfDocument.DoesNotExist:
            return JsonResponse({'error': 'Document not found'}, status=404)

    return JsonResponse({'error': 'Invalid request method'}, status=400)
