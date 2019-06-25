from django.contrib.auth.models import AbstractUser
from django.db import models
from collab.models.project import Project


class CustomUser(AbstractUser):
    # add additional fields in here
    nickname = models.CharField('nickname', max_length=15, blank=True)

    def __str__(self):
        return '%s' % (self.username)

    def project_right(self, project):
        """
            Return the User project rights
            LEVEL = (
                ('0', 'Utilisateur anonyme'),
                ('1', 'Utilisateur connecté'),
                ('2', 'Contributeur'),
                ('3', 'Modérateur'),
                ('4', 'Administrateur'),
            )
        """
        user_right = {'proj_creation': False,
                      'proj_modification': False,
                      'proj_consultation': False,
                      'feat_archive': False,
                      'feat_creation': False,
                      'feat_modification': False,
                      'feat_consultation': False,
                      'user_admin': False,
                      'model_creation': False}
        # modification if admin or super admin
        try:
            if self.is_superuser:
                user_right = {'proj_creation': True,
                              'proj_modification': True,
                              'proj_consultation': True,
                              'feat_archive': True,
                              'feat_creation': True,
                              'feat_modification': True,
                              'feat_consultation': True,
                              'user_admin': True,
                              'model_creation': True}
            else:
                try:
                    autorisation = Autorisation.objects.get(user=self,
                                                            project=project)
                    level = int(autorisation.level)
                except Exception as e:
                    # no autorisation on this project but the user is connected
                    level = 1
                # Projet
                # if project and feature are visible
                # right to vizualize features and comments
                if level >= int(project.visi_feature) or \
                   int(project.visi_feature) < 2:
                    user_right['proj_consultation'] = True
                    user_right['feat_consultation'] = True
                # right to modify project fields and administrate users and add new type of feature
                if level >= 4:
                    user_right['proj_modification'] = True
                    user_right['user_admin'] = True
                    user_right['model_creation'] = True
                # right to archive features
                if level >= int(project.visi_archive)or \
                   int(project.visi_archive) < 2:
                    user_right['feat_archive'] = True
                # right to modify feature
                if level >= 3:
                    user_right['feat_modification'] = True
                # right to create a feature or a comment
                if level >= 2:
                    user_right['feat_creation'] = True

        except Exception as e:
            # no autorisation
            pass

        return user_right


class Autorisation(models.Model):
    LEVEL = (
        # ('0', 'Utilisateur anonyme'),
        ('1', 'Utilisateur connecté'),
        ('2', "Contributeur"),
        ('3', 'Modérateur'),
        ('4', "Administrateur"),
    )
    level = models.CharField("Niveau d'autorisation",
                             choices=LEVEL,
                             max_length=1)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    creation_date = models.DateTimeField("Date de création de l'abonnement",
                                         auto_now_add=True)
    modification_date = models.DateTimeField("Date de modification de l'abonnement",
                                         auto_now=True)

    class Meta:
        # un role par projet
        unique_together = (
            ('user', 'project'),
        )
