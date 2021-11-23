from django.db import models
from django.db.models import Q, When, Case, CharField, Value
from django.apps import apps
from geocontrib.choices import MODERATOR, SUPER_CONTRIBUTOR


class AvailableFeaturesManager(models.Manager):

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.select_related('creator')
        queryset = queryset.select_related('feature_type')
        queryset = queryset.select_related('project')
        return queryset

    def availables(self, user, project):
        Authorization = apps.get_model(app_label='geocontrib', model_name='Authorization')
        UserLevelPermission = apps.get_model(app_label='geocontrib', model_name='UserLevelPermission')
        queryset = self.get_queryset().filter(project=project)

        # 0 - si utlisateur anonyme
        if not user.is_authenticated:
            if Authorization.has_permission(user, 'can_view_archived_feature', project):
                queryset = queryset.filter(Q(status='published') | Q(status='archived'))
            else:
                queryset = queryset.filter(status='published')
            return queryset

        # 1 - si is_project_administrator on liste toutes les features
        if Authorization.has_permission(user, 'is_project_administrator', project) \
                or Authorization.has_permission(user, 'is_project_moderator', project):
            return queryset

        user_rank = Authorization.get_rank(user, project)
        project_arch_rank = project.access_level_arch_feature.rank
        project_pub_rank = project.access_level_pub_feature.rank
        moderateur_rank = UserLevelPermission.objects.get(user_type_id=MODERATOR).rank
        supercontributeur_rank = UserLevelPermission.objects.get(user_type_id=SUPER_CONTRIBUTOR).rank

        #  - si is_project_super_contributor:
        # Dans le cas de projets non modérés, il peut modifier le statut
        # de tous les signalements qu'il peut voir
        # ("brouillons", "publiés" ; pour les "archivés" c'est en fonction des paramètres du projet)
        # vers les statuts de "brouillons", "publiés", et "archivés".
        # Dans le cas de projets modérés, il peut modifier le statut
        # de tous les signalements qu'il peut voir
        # ("brouillons", "publication en cours", "publiés" ; pour les "archivés" c'est en fonction des paramètres du projet)
        # vers les statuts de "brouillons", "publication en cours".
        if Authorization.has_permission(
                user, 'is_project_super_contributeur', project):

            if project.moderation and user_rank < moderateur_rank:
                queryset = queryset.exclude(
                    ~Q(creator=user), status='pending',
                )
            if user_rank < project_arch_rank:
                queryset = queryset.exclude(
                    status='archived',
                )
            if user_rank < project_pub_rank:
                queryset = queryset.exclude(
                    ~Q(creator=user), status='published',
                )
            return queryset

        else:
            # A TESTER => REDMINE ISSUES 9784
            if user_rank != supercontributeur_rank:
                queryset = queryset.exclude(
                    ~Q(creator=user), status='draft',
                )

            # if project.moderation and user_rank < moderateur_rank:
            #     # import pdb; pdb.set_trace()
            #     queryset = queryset.exclude(
            #         ~Q(creator=user), 
            #         status='pending',
            #     )

            if user_rank < project_arch_rank:
                queryset = queryset.exclude(
                    status='archived',
                )

            if user_rank < project_pub_rank:
                queryset = queryset.exclude(
                    ~Q(creator=user), status='published',
                )

        return queryset


class LayerManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset()

    def project_filter(self, project):
        BaseMap = apps.get_model(app_label='geocontrib', model_name='BaseMap')
        return self.get_queryset().filter(
            pk__in=BaseMap.objects.filter(project=project).values_list('layers__pk', flat=True)
        )


class FeatureLinkManager(models.Manager):

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.select_related('feature_from')
        queryset = queryset.select_related('feature_to')
        return queryset

    def context(self, feature_id):
        res = self.get_queryset().filter(
            Q(feature_from__feature_id=feature_id) | Q(feature_to__feature_id=feature_id)
        ).annotate(
            relation_display=Case(
                # TODO: Les conditions sur champs liés feature_to / feature_from ne passent pas
                When(feature_to__feature_id=feature_id, relation_type='est_remplace_par', then=Value('Est remplacé par')),
                When(feature_from__feature_id=feature_id, relation_type='remplace', then=Value('Remplace')),

                When(relation_type='doublon', then=Value('Doublon')),
                When(relation_type='depend_de', then=Value('Dépend de')),
                default=Value('N/A'),
                output_field=CharField(),
            )
        ).values_list('relation_display', 'relation_type')
        return res

    def related(self, feature_id):
        queryset = self.get_queryset().filter(Q(feature_from__feature_id=feature_id))
        return queryset
