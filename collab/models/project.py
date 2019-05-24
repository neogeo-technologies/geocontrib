from django.db import models
from collab.choices import USER_TYPE
from collab.choices import USER_TYPE_ARCHIVE
from django.contrib.postgres.fields import JSONField
from django.utils.html import format_html

from django.conf import settings
from django.utils.text import slugify


class Project(models.Model):

    # Admin prepopulated_fields = {"slug": ("titre",)}
    title = models.CharField('Titre', max_length=128, unique=True)
    slug = models.SlugField('Slug', max_length=128, unique=True)
    creation_date = models.DateTimeField("Date de création du projet",
                                          auto_now_add=True)
    description = models.TextField('Description', blank=True)
    illustration = models.ImageField('illustration', upload_to="illustrations", null=True)
    moderation = models.BooleanField('Modération', default=False)
    visi_feature = models.CharField('Visibilité des signalements publiés',
                                    choices=USER_TYPE,
                                    max_length=1, default='0')
    visi_archive = models.CharField('Visibilité des signalements archivés',
                                    choices=USER_TYPE_ARCHIVE,
                                    max_length=1, default='0')
    archive_feature = models.DurationField('Délai avant archivage', blank=True,
                                            null=True)
    delete_feature = models.DurationField('Délai avant suppression',
                                           blank=True, null=True)
    feature_type = JSONField('Type de signalements disponibles',
                             blank=True, null=True)

    def __str__(self):
        return self.title

    def thumbLink(self):
        try:
            return format_html('<img src="{url}" width=200 height=200/>',
                               url=settings.BASE_URL+self.illustration.url)
        except Exception as e:
            pass

    thumbLink.allow_tags = True
    thumbLink.short_description = "Icône"

    def _get_unique_slug(self):
        slug = slugify(self.title)
        unique_slug = slug
        num = 1
        while Project.objects.filter(slug=unique_slug).exists():
            unique_slug = '{}-{}'.format(slug, num)
            num += 1
        return unique_slug

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._get_unique_slug()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Projet"
        verbose_name_plural = "Projets"
