from collections import defaultdict 
from django.contrib.auth import get_user_model
from rest_framework import serializers

from api import logger
from geocontrib.models import Attachment
from geocontrib.models import Comment
from geocontrib.models import Feature
from geocontrib.models import FeatureType
from geocontrib.models import Project
from geocontrib.models import Event
from geocontrib.models import StackedEvent
from geocontrib.models import ImportTask


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):

    full_name = serializers.SerializerMethodField()

    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username

    class Meta:
        model = User
        fields = (
            'full_name',
            'username'
        )


class FeatureAttachmentSerializer(serializers.ModelSerializer):
    """
    Serializer for handling the serialization and deserialization of Attachment objects,
    specifically for features within a project. This serializer ensures that certain fields
    are read-only and handles the creation and updating of Attachment instances based on 
    validated data.
    """
    # Field to display the creation time of the attachment, not editable by the user
    created_on = serializers.DateTimeField(read_only=True)
    # Field to display the author's name or identifier, also read-only
    display_author = serializers.ReadOnlyField()
    # Field to manage file attachment, not editable directly by the user
    attachment_file = serializers.FileField(read_only=True)
    # Field to specify if the attachement is a key document, in order to send specific notifications
    is_key_document = serializers.BooleanField(default=False)

    class Meta:
        # Specifies the model associated with this serializer
        model = Attachment
        # Specifies which fields should be included in serialized output
        fields = (
            'id',
            'title',
            'info',
            'attachment_file',
            'extension',
            # 'comment',
            'created_on',
            'display_author',
            'is_key_document',
        )

    def get_user(self):
        """
        Retrieves the user from the request context, used to set the author field
        during creation or updating of an attachment.
        """
        request = self.context.get('request')
        user = getattr(request, 'user')
        return user

    def create(self, validated_data):
        """
        Custom creation method that sets additional fields based on the context and then
        creates an Attachment instance.
        """
        feature = self.context.get('feature')
        validated_data['feature_id'] = feature.feature_id
        validated_data['project'] = feature.project
        validated_data['author'] = self.get_user()
        validated_data['object_type'] = 'feature'
                
        try:
            # Attempt to create an Attachment instance with the provided validated data
            instance = Attachment.objects.create(**validated_data)
        except Exception as err:
            # If an error occurs during creation, raise a validation error
            raise serializers.ValidationError({'error': str(err)})
        return instance

    def update(self, instance, validated_data):
        """
        Custom update method that sets the author again and updates the instance
        based on the provided validated data.
        """
        # Update the author information
        validated_data['author'] = self.get_user()
        try:
            # Update instance fields with values from validated_data
            for k, v in validated_data.items():
                setattr(instance, k, v)
            instance.save()  # Save the updated instance
        except Exception as err:
            # If an error occurs during update, raise a validation error
            raise serializers.ValidationError({'error': str(err)})
        else:
            # Return the updated instance if no errors occurred
            return instance


class CommentDetailedSerializer(serializers.ModelSerializer):

    created_on = serializers.DateTimeField(format="%d/%m/%Y", read_only=True)

    display_author = serializers.ReadOnlyField()

    attachment = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = (
            'id',
            'comment',
            'created_on',
            'display_author',
            'attachment',
        )

    def get_attachment(self, comment):
        res = None
        attachment = comment.attachment_set.first()
        if attachment:
            res = {
                'url': attachment.attachment_file.url,
                'extension': attachment.extension,
                'title': attachment.title,
                'info': attachment.info,
            }
        return res

    def get_user(self):
        request = self.context.get('request')
        user = getattr(request, 'user')
        return user

    def create(self, validated_data):
        feature = self.context.get('feature')
        validated_data['feature_type_slug'] = feature.feature_type.slug
        validated_data['feature_id'] = feature.feature_id
        validated_data['project'] = feature.project
        validated_data['author'] = self.get_user()

        try:
            instance = Comment.objects.create(**validated_data)
        except Exception as err:
            raise serializers.ValidationError(f'Invalid Input. {err}')
        return instance


class CommentSerializer(serializers.ModelSerializer):

    created_on = serializers.DateTimeField(format="%d/%m/%Y", read_only=True)

    display_author = serializers.ReadOnlyField()

    related_feature = serializers.SerializerMethodField()

    def get_related_feature(self, obj):
        res = {}
        if obj.feature_id:
            try:
                feature = Feature.objects.get(feature_id=obj.feature_id)
                res = {
                    'feature_id': str(feature.feature_id),
                    'feature_type_slug': str(feature.feature_type.slug),
                    'title': str(feature.title),
                }
            except Exception:
                logger.exception('No related feature found')
        return res

    class Meta:
        model = Comment
        fields = (
            'created_on',
            'comment',
            'display_author',
            'related_feature',
        )
        read_only_fields = fields


class EventSerializer(serializers.ModelSerializer):

    created_on = serializers.DateTimeField(format="%d/%m/%Y %H:%M", read_only=True)

    display_user = serializers.ReadOnlyField()

    related_comment = serializers.SerializerMethodField()

    related_feature = serializers.SerializerMethodField()

    project_title = serializers.SerializerMethodField()

    attachment_details = serializers.SerializerMethodField()

    def get_related_comment(self, obj):
        res = {}
        if obj.object_type == 'comment':
            try:
                comment = Comment.objects.get(id=obj.comment_id)
                res = {
                    'comment': comment.comment,
                    'attachments': [
                        {'url': att.attachment_file.url, 'title': att.title} for att in comment.attachment_set.all()
                    ]
                }
            except Exception:
                logger.exception('No related comment found')
        return res

    def get_related_feature(self, obj):
        res = {}
        if obj.feature_id:
            feature = Feature.objects.filter(feature_id=obj.feature_id).first()
            if feature:
                res = {
                    'title': str(feature.title),
                    'deletion_on': str(feature.deletion_on),
                    'feature_url': feature.get_view_url()
                }
            else:
                logger.exception(f'Feature with ID {obj.feature_id} not found.')
        return res

    def get_project_title(self, obj):
        title = None
        if obj.project_slug:
            try:
                project = Project.objects.get(slug=obj.project_slug)
                if project :
                    title = project.title
            except Exception:
                logger.exception('No related project found')
        return title

    def get_attachment_details(self, obj):
        # Fetch attachment details if the event is related to an attachment
        if obj.attachment_id:
            try:
                attachment = Attachment.objects.get(id=obj.attachment_id)
                return {
                    'title': attachment.title,
                    'url': attachment.attachment_file.url,
                }
            except Attachment.DoesNotExist:
                logger.exception('Attachment not found for id {}'.format(obj.attachment_id))
                return {}
        return {}

    class Meta:
        model = Event
        fields = (
            'created_on',
            'object_type',
            'event_type',
            'data',
            'project_slug',
            'feature_type_slug',
            'feature_id',
            'comment_id',
            'attachment_id',
            'display_user',
            'related_comment',
            'related_feature',
            'project_title',
            'attachment_details',
        )


class FeatureEventSerializer(serializers.ModelSerializer):

    created_on = serializers.DateTimeField(format="%d/%m/%Y %H:%M", read_only=True)

    display_user = serializers.ReadOnlyField()

    related_comment = serializers.SerializerMethodField()

    def get_related_comment(self, obj):
        res = {}
        if obj.object_type == 'comment':
            try:
                comment = Comment.objects.get(id=obj.comment_id)
                res['comment'] = comment.comment
                attachment = comment.attachment_set.first()
                res['attachment'] = {'url': attachment.attachment_file.url, 'title': attachment.title}
            except Exception:
                pass
        return res

    class Meta:
        model = Event
        fields = (
            'created_on',
            'object_type',
            'event_type',
            'display_user',
            'related_comment',
        )


class StackedEventSerializer(serializers.ModelSerializer):
    """
    Serializer for StackedEvent objects. This serializer dynamically groups and serializes events 
    associated with a StackedEvent instance. The events are grouped by feature type and feature title,
    and each group is further processed to include only those events whose feature types have notifications enabled.

    The serializer performs several key operations:
    - Retrieves and groups all events related to the stacked event instance.
    - Fetches all Feature objects associated with these events in a single query to minimize database hits.
    - Utilizes a nested defaultdict to organize events by feature type and then by feature title.
    - Filters out any events linked to feature types where 'disable_notification' is set to True.
    - Serializes grouped events, ensuring that each event is associated with its correct feature URL and sorted by creation time.
    """

    # Define a custom field to dynamically create the serialized event data
    events = serializers.SerializerMethodField()

    class Meta:
        model = StackedEvent
        fields = '__all__'  # Serialize all fields from StackedEvent model

    def get_events(self, obj):
        # Retrieve all related events for the stacked event instance
        events = obj.events.all()
        # Initialize a nested defaultdict for grouping events by feature type and title
        events_grouped = defaultdict(lambda: defaultdict(list))

        # Gather all unique feature IDs from the events to minimize database queries
        feature_ids = {event.feature_id for event in events if event.feature_id}
        # Retrieve all corresponding Feature objects in a single query, including their types
        features = Feature.objects.filter(feature_id__in=feature_ids).select_related('feature_type')
        # Map feature IDs to Feature objects for quick access
        feature_map = {feature.feature_id: feature for feature in features}

        # Fetch FeatureTypes including the disable_notification attribute
        feature_types = FeatureType.objects.all().values('slug', 'title', 'disable_notification')
        # Dictionary mapping feature type slugs to their titles with disable notification param
        slug_to_title_and_notification = {ft['slug']: (ft['title'], ft['disable_notification']) for ft in feature_types}

        # Iterate through each event to group them by feature type and title
        for event in events:
            feature_type_slug = event.feature_type_slug
            # Check and assign the correct feature type slug if not available
            if not feature_type_slug and event.feature_id and event.feature_id in feature_map:
                feature = feature_map[event.feature_id]
                feature_type_slug = feature.feature_type.slug if feature.feature_type else None

            # Get notification settings with default fallback if slug is not in the dictionary
            notification_settings = slug_to_title_and_notification.get(feature_type_slug, ('Type inconnu', False))

            # Check if feature_type slug is found and if notifications are not disabled in case it is not a key document
            if feature_type_slug and (event.object_type == 'key_document' or not notification_settings[1]):
                # Assign a title from the feature map or use 'Élément inconnu' if missing
                feature_title = feature_map[event.feature_id].title if event.feature_id in feature_map else 'Élément inconnu'
                # Use the feature type title from the map, fallback to 'Type inconnu' if not found
                feature_type_title = slug_to_title_and_notification.get(feature_type_slug, ('Type inconnu', False))[0]
                # Group the event under the appropriate feature type and title
                events_grouped[feature_type_title][feature_title].append(event)

        # Serialize the grouped events for output
        grouped_data = {}
        for feature_type, features in events_grouped.items():
            feature_data = {}
            for feature_title, events in features.items():
                # Retrieve the Feature object if it exists in the feature_map
                feature = feature_map.get(events[0].feature_id)
                # Only provide the feature URL if the feature has not been deleted
                # (i.e., deletion_on should be None to include the URL)
                feature_url = feature.get_view_url() if feature and feature.deletion_on is None else "deleted"
                # Sort events by creation time or other criteria as needed
                events_sorted = sorted(events, key=lambda x: x.created_on)
                # Store the sorted events with the feature URL in the serialized data
                feature_data[feature_title] = {
                    'feature_url': feature_url,
                    'events': EventSerializer(events_sorted, many=True, read_only=True).data
                }
            grouped_data[feature_type] = feature_data

        return grouped_data


class ImportTaskSerializer(serializers.ModelSerializer):

    project_title = serializers.SerializerMethodField()
    feature_type_title = serializers.SerializerMethodField()
    geojson_file_name = serializers.SerializerMethodField()
    csv_file_name = serializers.SerializerMethodField()

    def get_project_title(self, obj):
        return str(obj.project.slug)

    def get_feature_type_title(self, obj):
        return str(obj.feature_type.slug)

    def get_geojson_file_name(self, obj):
        try:
            filename = str(obj.file.name.split('/')[-1])
        except Exception:
            filename = 'example_error.file'
        return filename

    def get_csv_file_name(self, obj):
        try:
            filename = str(obj.file.name.split('/')[-1])
        except Exception:
            filename = 'example_error.file'
        return filename

    class Meta:
        model = ImportTask
        fields = (
            'created_on',
            'started_on',
            'finished_on',
            'status',
            # 'project',
            'project_title',
            # 'feature_type',
            'feature_type_title',
            'user',
            # 'geojson_file',
            'geojson_file_name',
            'infos',
            'csv_file_name'
        )
