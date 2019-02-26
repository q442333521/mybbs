from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.


class UserInfo(AbstractUser):
    """
    用户信息表
    """
    nid = models.AutoField(primary_key=True)
    phone = models.CharField(max_length=11, null=True, unique=True)
    avatar = models.FileField(upload_to='avatars/', default='avatars/defuault.png', verbose_name='头像')
    create_time = models.DateField(auto_now_add=True)

    blog = models.OneToOneField(to='Blog', to_field='nid', null=True)

    def __str__(self):
        return self.username


class Blog(models.Model):
    """
    博客信息
    """
    nid = models.AutoField(primary_key=True)
    title = models.CharField(max_length=64)
    site = models.CharField(max_length=32, unique=True)
    theme = models.CharField(max_length=32)

    def __str__(self):
        return self.title


class Category(models.Model):
    """
    个人文章博客分类
    """
    nid = models.AutoField(primary_key=True)
    title = models.CharField(max_length=32)
    blog = models.ForeignKey(to='Blog', to_field='nid')

    def __str__(self):
        return self.title


class Tag(models.Model):
    """
    标签
    """
    nid = models.AutoField(primary_key=True)
    title = models.CharField(max_length=32)
    blog = models.ForeignKey(to='Blog', to_field='nid')

    def __str__(self):
        return self.title


class Article(models.Model):
    """
    文章
    """
    nid = models.AutoField(primary_key=True)
    title = models.CharField(max_length=50)
    desc = models.CharField(max_length=255)
    create_time = models.DateTimeField()

    category = models.ForeignKey(to='Category', to_field='nid', null=True)
    user = models.ForeignKey(to='UserInfo', to_field='nid')
    tags = models.ManyToManyField(to='Tag', through='Article2Tag', through_fields=('article', 'tag'),)

    def __str__(self):
        return self.title


class ArticleDetail(models.Model):
    """
    文章详情表
    """
    nid = models.AutoField(primary_key=True)
    content = models.TextField()
    article = models.OneToOneField(to='Article', to_field='nid')

    def __str__(self):
        return self.content


class Article2Tag(models.Model):
    """
    文章和标签的多对多关系表
    """
    nid = models.AutoField(primary_key=True)
    article = models.ForeignKey(to='Article', to_field='nid')
    tag = models.ForeignKey(to='Tag', to_field='nid')

    class Meta:
        unique_together = (('article', 'tag'),)


class ArticleUpDown(models.Model):
    """
    点赞表
    """
    nid = models.AutoField(primary_key=True)
    user = models.ForeignKey(to='UserInfo', null=True)
    article = models.ForeignKey(to='Article', null=True)
    is_up = models.BooleanField(default=True)

    class Meta:
        unique_together = (('article', 'user'),)


class Comment(models.Model):
    """
    评论表
    """
    nid = models.AutoField(primary_key=True)
    article = models.ForeignKey(to='Article', to_field='nid')
    user = models.ForeignKey(to='UserInfo', to_field='nid')
    content = models.CharField(max_length=255)
    create_time = models.DateTimeField(auto_now_add=True)
    parent_comment = models.ForeignKey('self', null=True)

    def __str__(self):
        return self.content
