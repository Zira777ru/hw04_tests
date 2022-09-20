from django.db import models
from django.contrib.auth import get_user_model

from posts.constants import LEN_TEXT_MODEL_POST

User = get_user_model()


class Post(models.Model):
    text = models.TextField('Текст поста', help_text='Введите текст поста')
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор'
    )
    group = models.ForeignKey(
        'Group',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='posts',
        help_text='Группа, к которой будет относиться пост',
        verbose_name='Группа'
    )

    class Meta:
        ordering = ['-pub_date']

    def __str__(self) -> str:
        return self.text[:LEN_TEXT_MODEL_POST]


class Group(models.Model):
    title = models.CharField('Название группы', max_length=200)
    slug = models.SlugField(unique=True, verbose_name='Ссылка')
    description = models.TextField('Описание группы', blank=True)

    class Meta:
        verbose_name = 'Группа',
        verbose_name_plural = 'Группы'

    def __str__(self) -> str:
        return self.title
