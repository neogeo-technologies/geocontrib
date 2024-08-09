from django.contrib.gis.geos import GEOSGeometry
from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework import exceptions
from rest_framework import mixins
from rest_framework import permissions
from rest_framework import views
from rest_framework import viewsets
from rest_framework.response import Response

from api.serializers import FeatureAttachmentSerializer
from api.serializers import CommentSerializer
from api.serializers import CommentDetailedSerializer
from api.serializers import EventSerializer
from api.serializers import ImportTaskSerializer
from geocontrib.exif import exif
from geocontrib.models import Attachment
from geocontrib.models import Authorization
from geocontrib.models import Comment
from geocontrib.models import Event
from geocontrib.models import Feature
from geocontrib.models import FeatureType
from geocontrib.models import Project
from geocontrib.models.task import ImportTask
from geocontrib.tasks import task_geojson_processing, task_csv_processing


class ImportTaskSearch(
        mixins.CreateModelMixin,
        mixins.ListModelMixin,
        viewsets.GenericViewSet):
    """
    Allows the creation and retrieval of tasks for importing features from file.
    """
    
    queryset = ImportTask.objects.all()
    serializer_class = ImportTaskSerializer
    http_method_names = ['get', 'post']

    @swagger_auto_schema(
        operation_summary="List tasks for features import",
        tags=["misc"]
    )
    def list(self, request, *args, **kwargs):
        """
        Retrieve a list of import tasks with optional filters.
        """
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create a new task for features import",
        tags=["misc"]
    )
    def create(self, request, *args, **kwargs):
        """
        Create a new import task based on the provided file.
        """
        try:
            if request.FILES.get('json_file'):
                up_file = request.FILES['json_file']
                process = task_geojson_processing
            if request.FILES.get('csv_file'):
                up_file = request.FILES['csv_file']
                process = task_csv_processing
            feature_type = FeatureType.objects.get(slug=request.data.get('feature_type_slug'))
            import_task = ImportTask.objects.create(
                created_on=timezone.now(),
                project=feature_type.project,
                feature_type=feature_type,
                user=request.user,
                file=up_file
            )
        except Exception as e:
            return Response(
                {'error': 'error'},
                status=400,
            )
        else:
            process.apply_async(kwargs={'import_task_id': import_task.pk})

        return Response({'detail': "L'import du fichier réussi. Le traitement des données est en cours. "}, status=200)

    def filter_queryset(self, queryset):
        """
        Apply filters to the queryset based on query parameters.
        """
        status = self.request.query_params.get('status')
        feature_type_slug = self.request.query_params.get('feature_type_slug')
        project_slug = self.request.query_params.get('project_slug')
        if project_slug:
            queryset = queryset.filter(project__slug=project_slug)
        if status:
            queryset = queryset.filter(status__icontains=status)
        if feature_type_slug:
            queryset = queryset.filter(feature_type__slug=feature_type_slug)
        queryset = queryset.order_by('-id')[:5]
        return queryset

    def get_queryset(self):
        """
        Get the base queryset with related data preloaded.
        """
        queryset = super().get_queryset()
        queryset = queryset.select_related('user')
        queryset = queryset.select_related('feature_type')
        queryset = queryset.select_related('project')
        # NB filter_queryset() bien appelé par ListModelMixin
        return queryset


class ProjectComments(views.APIView):
    queryset = Project.objects.all()
    lookup_field = 'slug'
    http_method_names = ['get', ]

    def get_object(self):
        slug = self.kwargs.get('slug') or None
        obj = get_object_or_404(Project, slug=self.kwargs.get('slug'))
        return obj

    def get(self, request, slug):
        user = self.request.user
        project = self.get_object()
        permissions = Authorization.all_permissions(user, project)

        # On filtre les signalements selon leur statut et l'utilisateur courant
        features = Feature.handy.availables(
            user=user,
            project=project
        ).order_by('-created_on')

        # filter out features with a deletion date, since deleted features are not anymore deleted directly from database (https://redmine.neogeo.fr/issues/16246)
        features = features.filter(deletion_on__isnull=True)

        # On filtre les commentaire selon les signalements visibles
        last_comments = Comment.objects.filter(
            project=project,
            feature_id__in=[feat.feature_id for feat in features]
        ).order_by('-created_on')[0:5]

        serialized_comments = CommentSerializer(last_comments, many=True).data
        data = {
            'last_comments': serialized_comments,
        }
        return Response(data, status=200)


class FeatureAttachmentView(
        mixins.ListModelMixin,
        mixins.CreateModelMixin,
        mixins.RetrieveModelMixin,
        mixins.UpdateModelMixin,
        mixins.DestroyModelMixin,
        viewsets.GenericViewSet
        ):
    """
    ViewSet for handling CRUD operations on attachments related to a specific feature.
    This class combines multiple mixins to provide list, create, retrieve, update,
    and destroy actions.
    """
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly
    ]
    # Queryset specifically filters attachments by the 'feature' object_type.
    queryset = Attachment.objects.filter(object_type='feature')
    # Specifies the serializer class to be used for serializing and deserializing data.
    serializer_class = FeatureAttachmentSerializer

    def get_object(self):
        """
        Retrieve a specific attachment by 'attachment_id' and 'feature_id' provided in the URL.
        """
        attachment_id = self.kwargs['attachment_id']
        feature_id = self.kwargs['feature_id']
        # Retrieves an object or throws a 404 if the attachment does not exist
        return get_object_or_404(
            Attachment, id=attachment_id, feature_id=feature_id)

    def get_queryset(self):
        """
        Override to filter the queryset based on 'feature_id' provided in the URL,
        ensuring that only attachments for a specific feature are returned.
        """
        feature_id = self.kwargs['feature_id']
        # Filters the initial queryset by 'feature_id'
        qs = super().get_queryset().filter(feature_id=feature_id)
        return qs

    def get_serializer_context(self):
        """
        Provides additional context to the serializer.
        If the view is being used for schema generation (`swagger_fake_view`),
        it short-circuits and returns the default context. 
        Otherwise, it retrieves the `feature_id` from the URL parameters,
        fetches the corresponding feature instance, and adds it to the context.
        """
        # Gets the default context from the base class, which includes request, view, etc.
        context = super().get_serializer_context()
        if getattr(self, 'swagger_fake_view', False):
            return context
        feature_id = self.kwargs['feature_id']
        # Retrieves the feature instance associated with 'feature_id' or throws a 404
        feature = get_object_or_404(Feature, feature_id=feature_id)
        # Updates the context with the feature instance
        context.update({'feature': feature})
        return context


class FeatureAttachmentUploadView(views.APIView):
    """
    APIView for handling the uploading of attachment files linked to a specific feature.
    This view handles updating an existing attachment with a new file.
    """

    # Ensures that only authenticated users can access this view
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    def get_object(self, feature_id, attachment_id):
        """
        Retrieves the attachment object based on feature_id and attachment_id or returns a 404 error if not found.
        """
        return get_object_or_404(
            Attachment, id=attachment_id, feature_id=feature_id)

    def read_file(self, request):
        """
        Extracts the file from the request. Raises a validation error if no file is found in the request data.
        """
        _file = request.data.get('file')
        if not _file:
            raise exceptions.ValidationError({
                'error': "File entry is missing",
            })
        return _file

    def put(self, request, feature_id, attachment_id):
        """
        Handles the PUT request to update an attachment's file. Retrieves the existing attachment,
        reads the new file from the request, saves it, and returns the updated attachment data.
        """
        # Retrieve the attachment object using feature and attachment IDs
        instance = self.get_object(feature_id, attachment_id)
        # Read the new file from the request
        attachment_file = self.read_file(request)
        # Save the new file to the instance, updating the file on disk
        instance.attachment_file.save(
            attachment_file.name, attachment_file, save=True)
        # Serialize the updated attachment instance to prepare response data
        data = FeatureAttachmentSerializer(
            instance=instance,
            context={'request': request}
        ).data
        # Return the serialized data as a response with status code 200
        return Response(data=data, status=200)


class CommentView(
        mixins.ListModelMixin,
        mixins.CreateModelMixin,
        mixins.RetrieveModelMixin,
        mixins.UpdateModelMixin,
        mixins.DestroyModelMixin,
        viewsets.GenericViewSet
        ):
    """
    Viewset  for handling CRUD operations associated with specific features.
    This class combines multiple mixins to provide list, create, retrieve, update,
    and destroy actions.
    """
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly
    ]

    queryset = Comment.objects.all()

    serializer_class = CommentDetailedSerializer

    def get_object(self):
        """
        Retrieves a specific comment object based on comment_id and feature_id.
        """
        comment_id = self.kwargs['comment_id']
        feature_id = self.kwargs['feature_id']
        return get_object_or_404(
            Comment, id=comment_id, feature_id=feature_id)

    def get_queryset(self):
        """
        Retrieves the queryset of comments filtered by feature_id.
        """
        feature_id = self.kwargs['feature_id']
        qs = super().get_queryset().filter(feature_id=feature_id)
        return qs

    def get_serializer_context(self):
        """
        Provides additional context to the serializer.
        If the view is being used for schema generation (`swagger_fake_view`),
        it short-circuits and returns the default context.
        Otherwise, it retrieves the `feature_id` from the URL parameters,
        fetches the corresponding feature instance, and adds it to the context.
        """
        context = super().get_serializer_context()
        if getattr(self, 'swagger_fake_view', False):
            return context
        feature_id = self.kwargs['feature_id']
        feature = get_object_or_404(Feature, feature_id=feature_id)
        context.update({'feature': feature})
        return context


class CommentAttachmentUploadView(views.APIView):
    """
    API View for uploading attachments related to a specific comment on a feature.
    Manages attachment uploads by validating and saving files linked to comments, and updates the database accordingly.

    Code commented previously, to be removed if not necessary anymore:
        comment = Comment.objects.create(
            feature_id=feature.feature_id,
            feature_type_slug=feature.feature_type.slug,
            author=user,
            project=project,
            comment=form.cleaned_data.get('comment')
        )
        up_file = form.cleaned_data.get('attachment_file')
        title = form.cleaned_data.get('title')
        info = form.cleaned_data.get('info')
        if comment and up_file and title:
            Attachment.objects.create(
                feature_id=feature.feature_id,
                author=user,
                project=project,
                comment=comment,
                attachment_file=up_file,
                title=title,
                info=info,
                object_type='comment'
            )
    """
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    def get_object(self, feature_id, comment_id):
        # Retrieve and return a Comment object or raise a 404 if not found
        return get_object_or_404(Comment, id=comment_id, feature_id=feature_id)

    def read_file(self, request):
        # Extracts file from request, raises error if missing
        _file = request.data.get('file')
        if not _file:
            raise exceptions.ValidationError({'error': "File entry is missing"})
        return _file

    def read_title(self, request):
        # Extracts title from request, raises error if missing
        title = request.data.get('title')
        if not title:
            raise exceptions.ValidationError({'error': "Field 'title' is missing"})
        return title


    def put(self, request, feature_id, comment_id):
        # Retrieve the feature datas needed for attachment creation/update
        feature = get_object_or_404(Feature, feature_id=feature_id)
        # Retrieve the comment related to the uploaded attachment
        comment = self.get_object(feature_id, comment_id)
        # Get the file from the request to save in static folder
        attachment_file = self.read_file(request)
        # Create the attachment instance related to the uploaded file
        attachment, create = Attachment.objects.update_or_create(
            comment=comment,
            defaults={
                'project': feature.project,
                'title': self.read_title(request),
                'info': request.data.get('info', ''),
                'feature_id': feature.feature_id,
                'author': request.user,
                'object_type': 'comment',
                # Retrieve the 'is_key_document' as a string and convert it to a boolean in Python;
                # 'true' or 'True' yields True, anything else yields False.
                'is_key_document': request.data.get('is_key_document') in ['true', 'True']
            }
        )
        # Save the attachment file on the disk
        attachment.attachment_file.save(
            attachment_file.name, attachment_file, save=True)
        # Prepare data to be sent with the response
        data = CommentDetailedSerializer(
            instance=comment,
            context={'request': request}
        ).data
        return Response(data=data, status=200)

# Schema for swagger API documentation of EventView
event_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'created_on': openapi.Schema(type=openapi.TYPE_STRING, format='date-time', description='Creation date'),
        'object_type': openapi.Schema(type=openapi.TYPE_STRING, description='Type of the object (feature, project, comment, etc.)'),
        'event_type': openapi.Schema(type=openapi.TYPE_STRING, description='Type of event (create, update, delete)'),
        'data': openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'extra': openapi.Schema(type=openapi.TYPE_OBJECT, additional_properties=openapi.Schema(type=openapi.TYPE_STRING)),
                'feature_title': openapi.Schema(type=openapi.TYPE_STRING, description='Title of the feature'),
                'feature_status': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'new_status': openapi.Schema(type=openapi.TYPE_STRING, description='New status of the feature'),
                        'has_changed': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Indicates if the status has changed')
                    }
                )
            }
        ),
        'project_slug': openapi.Schema(type=openapi.TYPE_STRING, description='Slug of the project'),
        'feature_type_slug': openapi.Schema(type=openapi.TYPE_STRING, description='Slug of the feature type'),
        'feature_id': openapi.Schema(type=openapi.TYPE_STRING, format='uuid', description='ID of the feature'),
        'comment_id': openapi.Schema(type=openapi.TYPE_STRING, format='uuid', description='ID of the comment', nullable=True),
        'attachment_id': openapi.Schema(type=openapi.TYPE_STRING, format='uuid', description='ID of the attachment', nullable=True),
        'display_user': openapi.Schema(type=openapi.TYPE_STRING, description='Username of the user who triggered the event'),
        'related_comment': openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'comment': openapi.Schema(type=openapi.TYPE_STRING, description='Content of the related comment'),
                'attachments': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'url': openapi.Schema(type=openapi.TYPE_STRING, description='URL of the attachment'),
                            'title': openapi.Schema(type=openapi.TYPE_STRING, description='Title of the attachment')
                        }
                    )
                )
            }
        ),
        'related_feature': openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'title': openapi.Schema(type=openapi.TYPE_STRING, description='Title of the related feature'),
                'deletion_on': openapi.Schema(type=openapi.TYPE_STRING, format='date', description='Deletion date', nullable=True),
                'feature_url': openapi.Schema(type=openapi.TYPE_STRING, description='URL of the related feature')
            }
        ),
        'project_title': openapi.Schema(type=openapi.TYPE_STRING, description='Title of the project'),
        'attachment_details': openapi.Schema(type=openapi.TYPE_OBJECT, description='Details about the attachment', additional_properties=openapi.Schema(type=openapi.TYPE_STRING))
    }
)

response_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'events': openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=event_schema
        ),
        'features': openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=event_schema
        ),
        'comments': openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=event_schema
        )
    }
)

class EventView(views.APIView):
    """
    Retrieve the latest events, features, and comments for the authenticated user.
    
    - **events**: List of recent events.
    - **features**: List of recent feature-related events.
    - **comments**: List of recent comment-related events.
    """
    permission_classes = [
        permissions.IsAuthenticated
    ]

    @swagger_auto_schema(
        operation_summary="Get user events",
        tags=["users"],
        manual_parameters=[
            openapi.Parameter(
                'project_slug',
                openapi.IN_QUERY,
                description="Filter events by project slug",
                type=openapi.TYPE_STRING
            )
        ],
        responses={
            200: openapi.Response(
                description="A list of events, features, and comments",
                schema=response_schema
            ),
            403: openapi.Response(
                description="Forbidden",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "detail": openapi.Schema(type=openapi.TYPE_STRING, description="Error message")
                    },
                    example={"detail": "Informations d'authentification incorrectes."}
                )
            ),
        }
    )
    def get(self, request):
        user = request.user
        project_slug = request.GET.get('project_slug', '')
        
        # notifications
        all_events = Event.objects.filter(user=user).order_by('-created_on')
        if project_slug:
            all_events = all_events.filter(project_slug=project_slug)
        serialized_events = EventSerializer(all_events[0:5], many=True)
        
        # signalements
        feature_events = Event.objects.filter(
            user=user, object_type='feature').order_by('-created_on')
        if project_slug:
            feature_events = feature_events.filter(project_slug=project_slug)
        serialized_feature_events = EventSerializer(feature_events[0:5], many=True)
        
        # commentaires
        comment_events = Event.objects.filter(
            user=user, object_type='comment').order_by('-created_on')
        if project_slug:
            comment_events = comment_events.filter(project_slug=project_slug)
        serialized_comment_events = EventSerializer(comment_events[0:5], many=True)

        data = {
            'events': serialized_events.data,
            'features': serialized_feature_events.data,
            'comments': serialized_comment_events.data
        }
        return Response(data=data, status=200)


class ExifGeomReaderView(views.APIView):

    def get_geom(self, geom):
        # Si geoJSON
        if isinstance(geom, dict):
            geom = str(geom)
        geom = GEOSGeometry(geom, srid=4326)
        return geom

    def post(self, request):
        image_file = request.data.get('image_file')
        if not image_file:
            raise exceptions.ValidationError({
                'error': "Aucun fichier à ajouter",
            })
        try:
            data_geom_wkt = exif.get_image_geoloc_as_wkt(
                image_file, with_alt=False, ewkt=False)
            geom = self.get_geom(data_geom_wkt)
        except Exception:
            raise exceptions.ValidationError({
                'error': "Erreur lors de la lecture des données GPS.",
            })

        return Response({'geom': geom.wkt}, status=200)
