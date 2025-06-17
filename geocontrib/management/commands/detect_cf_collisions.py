from django.core.management.base import BaseCommand
from geocontrib.models import CustomField
import re


class Command(BaseCommand):
    help = "Detect CustomFields with normalized name collisions within the same FeatureType."

    def handle(self, *args, **options):
        self.stdout.write("\nScanning for CustomField name collisions after normalization (per FeatureType)...\n")

        def normalize_column_name(name: str) -> str:
            name = name.lower().replace('-', '_')
            name = re.sub(r"[^a-z0-9_]", "", name)
            return name

        # Collect custom fields grouped by feature_type_id
        grouped_fields = {}
        for cf in CustomField.objects.all():
            grouped_fields.setdefault(cf.feature_type_id, []).append(cf)

        has_collision = False
        for ft_id, fields in grouped_fields.items():
            seen = {}
            for cf in fields:
                norm = normalize_column_name(cf.name)
                seen.setdefault(norm, []).append(cf)

            for norm_name, dupes in seen.items():
                if len(dupes) > 1:
                    has_collision = True
                    self.stdout.write(self.style.WARNING(
                        f"\n❗ Collision on normalized name '{norm_name}' in FeatureType {ft_id}:"
                    ))
                    for cf in dupes:
                        self.stdout.write(
                            f"  - ID={cf.id}, name='{cf.name}', feature_type_id={cf.feature_type_id}, label='{cf.label}'"
                        )

        if not has_collision:
            self.stdout.write(self.style.SUCCESS("\n✅ No collisions found."))
