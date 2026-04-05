"""
python manage.py seed_dataset
Loads career_path_dataset.csv into JobDataset table.
"""
import csv
from django.core.management.base import BaseCommand
from django.conf import settings
from apps.ml.models import JobDataset


class Command(BaseCommand):
    help = 'Seed JobDataset from career_path_dataset.csv'

    def handle(self, *args, **kwargs):
        csv_path = settings.DATA_DIR / 'career_path_dataset.csv'
        if not csv_path.exists():
            self.stderr.write(f'File not found: {csv_path}')
            return

        created = 0
        updated = 0

        with open(csv_path, encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    _, was_created = JobDataset.objects.update_or_create(
                        job_id=row['Job_ID'],
                        defaults={
                            'skills': row.get('Skills', ''),
                            'years_of_experience': int(row.get('Years_of_Experience', 0)),
                            'predicted_job_title': row.get('Predicted_Job_Title', ''),
                            'company_name': row.get('Company_Name', ''),
                            'company_location': row.get('Company_Location', ''),
                            'industry': row.get('Industry', ''),
                            'salary_usd': int(row.get('Salary (USD)', 0)),
                            'education_level': row.get('Education_Level', ''),
                        }
                    )
                    if was_created:
                        created += 1
                    else:
                        updated += 1
                except Exception as e:
                    self.stderr.write(f'Error on row {row}: {e}')

        self.stdout.write(
            self.style.SUCCESS(f'Done. Created {created}, updated {updated} records.')
        )
