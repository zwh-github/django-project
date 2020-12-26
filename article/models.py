from django.db import models
from django.contrib.auth.models import User
from django.utils import  timezone
from mdeditor.fields import MDTextField
from django.urls import reverse
from taggit.managers import TaggableManager
from PIL import Image
#from imagekit.models import ProcessedImageField
#from imagekit.processors import ResizeToFit




class ArticleColumn(models.Model):
    title = models.CharField(max_length=100,blank = True)
    created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title



class ArticlePost(models.Model):
    author=models.ForeignKey(User,on_delete=models.CASCADE)
    column = models.ForeignKey(
        ArticleColumn,
            null=True,
        blank = True,
        on_delete=models.CASCADE,
        related_name ='acticle'
    )
    likes = models.PositiveIntegerField(default=0)
    title = models.CharField(max_length=100)
    body = MDTextField()
    avatar = models.ImageField(upload_to = 'article/%Y%m%d/',blank = True)
    created = models.DateTimeField(default=timezone.now)
    update=models.DateTimeField(auto_now=True)
    total_views = models.PositiveIntegerField(default=0)
    tags = TaggableManager(blank=True)
    '''avatar = ProcessedImageField(
        upload_to='article/%Y%m%d',
        processors=[ResizeToFit(width=400)],
        format='JPEG',
        options={'quality': 100},
    )'''

    class Meta:
        ordering = ('-created',)
    def __str__(self):
        return self.title
    def get_absolute_url(self):
        return reverse('article:article_detail',args=[self.id])
    def save(self,*args,**kwargs):
        article = super().save(*args,**kwargs)
        if self.avatar and not kwargs.get('update_fields'):
            image = Image.open(self.avatar)
            (x,y)=image.size
            new_x=400
            new_y=int(new_x*(y/x))
            resized_image = image.resize((new_x,new_y),Image.ANTIALIAS)
            resized_image.save(self.avatar.path)
        return article



# Create your models here.
