import uuid
from django.utils import timezone
from django.db import models
from django.db.models import JSONField


# 用户信息表
class User(models.Model):
    username = models.CharField(max_length=255, unique=True)
    avatar_url = models.URLField(max_length=500, blank=True, null=True)

    def __str__(self):
        return self.username


class PdfDocument(models.Model):
    paper_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    detail = models.TextField()
    summary = models.TextField(blank=True)
    pdf_file = models.FileField(upload_to='paper_file/', blank=True, null=True)  # 文件存储字段
    num_pages = models.IntegerField(blank=True, null=True)
    create_time = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name


# 文档高亮内容表
class Highlight(models.Model):
    pdf_document = models.ForeignKey(PdfDocument, on_delete=models.CASCADE, related_name="highlights")
    page_number = models.IntegerField()  # 高亮所在的页码
    highlighted_text = models.TextField()  # 高亮的文本内容
    start_offset = models.IntegerField()  # 文本层的高亮起始点
    end_offset = models.IntegerField()  # 文本层的高亮结束点

    def __str__(self):
        return f"Highlight on page {self.page_number} of {self.pdf_document.name}"


# 学习卡片信息表
class FlashCard(models.Model):
    STATUS_CHOICES = [
        ('TO_READ', 'TO_READ'),
        ('READING', 'READING'),
        ('UNDERSTAND', 'UNDERSTAND'),
        ('REVIEW', 'REVIEW'),
        ('KEY_POINT', 'KEY_POINT'),
        ('APPLY', 'APPLY'),
        ('TO_DISCUSS', 'TO_DISCUSS'),
    ]

    flashcard_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    pdf_document = models.ForeignKey(PdfDocument, on_delete=models.CASCADE, related_name="flashcards")
    title = models.CharField(max_length=255)
    content = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    highlight_by = models.CharField(max_length=255)  # This can also be a ForeignKey to User if needed
    notes = models.TextField(blank=True)
    ai_analysis = models.TextField(blank=True)
    related_to = JSONField(blank=True, null=True)  # 存储列表，列表中的内容为关联的Flashcard的flashcard_id
    feature_data = JSONField(blank=True, null=True)  # 用于存储特征向量

    def __str__(self):
        return self.title


# 群聊信息表
class ChatMessage(models.Model):
    message_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="messages")
    pdf_document = models.ForeignKey(PdfDocument, on_delete=models.CASCADE, related_name="chat_messages")  # 关联的文档
    content = JSONField()  # 使用 JSON 列表格式存储消息，包含 role 和 content 字段
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.from_user} in document {self.pdf_document.name} at {self.timestamp}"


# AI 助手信息表
class Agent(models.Model):
    name = models.CharField(max_length=255)
    details = models.TextField(blank=True)
    avatar_url = models.URLField(max_length=500, blank=True, null=True)

    def __str__(self):
        return self.name
