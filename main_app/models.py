from django.db import models
from django.contrib.auth.models import User

# 句子类型（如：高亮，理解，翻译，思考）
class SentenceType(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

# 难易程度（如：简单，一般，困难）
class DifficultyLevel(models.Model):
    level = models.CharField(max_length=50)

    def __str__(self):
        return self.level

# 领域分类（如：Machine Learning, Data Mining, Quantum Computing）
class Topic(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

# 关键词标签（如：Deep Learning, Neural Networks, Encryption）
class Tag(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

# 情感分类（如：Positive, Negative, Neutral）
class Sentiment(models.Model):
    label = models.CharField(max_length=50)

    def __str__(self):
        return self.label

# 句子功能分类（如：Introduction, Hypothesis, Data Presentation, Conclusion）
class SentenceFunction(models.Model):
    label = models.CharField(max_length=50)

    def __str__(self):
        return self.label

# 参考来源（引用的文献或其他资料来源）
class Source(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    publication_date = models.DateField()

    def __str__(self):
        return f"{self.title} by {self.author}"

# 语言分类（如：English, French, Chinese）
class Language(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

# 句子模型，扩展了多个分类
class Sentence(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # 句子由哪个用户创建
    content = models.TextField()  # 句子内容
    filename = models.CharField(max_length=255, null=True, blank=True)
    sentence_type = models.ForeignKey(SentenceType, on_delete=models.SET_NULL, null=True)  # 句子类型
    difficulty = models.ForeignKey(DifficultyLevel, on_delete=models.SET_NULL, null=True)  # 难易程度
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True)  # 领域分类
    tags = models.ManyToManyField(Tag, blank=True)  # 关键词标签（多对多）
    sentiment = models.ForeignKey(Sentiment, on_delete=models.SET_NULL, null=True)  # 情感分类
    sentence_function = models.ForeignKey(SentenceFunction, on_delete=models.SET_NULL, null=True)  # 句子功能分类
    source = models.ForeignKey(Source, on_delete=models.SET_NULL, null=True)  # 引用来源
    language = models.ForeignKey(Language, on_delete=models.SET_NULL, null=True)  # 语言分类
    created_at = models.DateTimeField(auto_now_add=True)  # 创建时间

    def __str__(self):
        return self.content[:50]  # 返回句子的前50个字符

# 笔记模型，记录用户针对句子的笔记内容
class Note(models.Model):
    sentence = models.ForeignKey(Sentence, on_delete=models.CASCADE, related_name='notes')  # 关联句子
    content = models.TextField()  # 笔记内容
    created_at = models.DateTimeField(auto_now_add=True)  # 笔记创建时间
    weight = models.FloatField(default=0)  # 笔记的权重，默认为0，用于推荐系统

    def __str__(self):
        return self.content[:50]

# 用户行为模型，记录用户针对笔记的行为（查看、点赞、收藏）
class UserAction(models.Model):
    ACTION_CHOICES = [
        ('view', 'View'),        # 查看行为
        ('like', 'Like'),        # 点赞行为
        ('favorite', 'Favorite') # 收藏行为
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)  # 用户
    note = models.ForeignKey(Note, on_delete=models.CASCADE)  # 针对的笔记
    action_type = models.CharField(max_length=10, choices=ACTION_CHOICES)  # 行为类型
    timestamp = models.DateTimeField(auto_now_add=True)  # 行为发生时间

    def __str__(self):
        return f'{self.user.username} {self.action_type} {self.note.id}'
    



