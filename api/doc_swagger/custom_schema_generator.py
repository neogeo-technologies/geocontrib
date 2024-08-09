from drf_yasg.generators import OpenAPISchemaGenerator

class CustomSchemaGenerator(OpenAPISchemaGenerator):
    def get_schema(self, request=None, public=False):
        schema = super().get_schema(request, public)
        schema.tags = [
            {
                "name": "auth",
                "description": "Login and logout user in app"
            },
            {
                "name": "users",
                "description": "Get users related informations"
            },
            {
                "name": "projects",
                "description": "Retrieve, list, edit and delete projects"
            },
            {
                "name": "feature types",
                "description": "Retrieve, list, edit and delete feature types"
            },
            {
                "name": "features",
                "description": "Retrieve, list, edit and delete features"
            },
            {
                "name": "misc",
                "description": "Miscellaneous"
            },
            {
                "name": "[deprecated] feature types",
                "description": "Retrieve, list, edit and delete feature types"
            },
            {
                "name": "[deprecated] features",
                "description": "Retrieve, list, edit and delete features"
            },
        ]
        return schema
