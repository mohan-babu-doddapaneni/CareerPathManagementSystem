"""
python manage.py seed_jobs
Seeds JobListing table from career_path_dataset.csv so the job board
works out of the box without needing an Adzuna API key.
"""
import csv
import uuid
from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from apps.jobs.models import JobListing
from apps.skills.models import OccupationRole

TITLE_TO_ROLE = {
    r.name.lower(): r for r in OccupationRole.objects.all()
} if False else {}   # populated in handle()

LOCATIONS = [
    'New York, NY', 'San Francisco, CA', 'Austin, TX', 'Seattle, WA',
    'Chicago, IL', 'Boston, MA', 'Los Angeles, CA', 'Denver, CO',
    'Atlanta, GA', 'Remote',
]


class Command(BaseCommand):
    help = 'Seed job listings from career_path_dataset.csv'

    def add_arguments(self, parser):
        parser.add_argument('--clear', action='store_true', help='Clear existing seeded jobs first')

    def handle(self, *args, **options):
        csv_path = settings.DATA_DIR / 'career_path_dataset.csv'
        if not csv_path.exists():
            self.stderr.write(f'File not found: {csv_path}')
            return

        if options['clear']:
            JobListing.objects.filter(adzuna_id__startswith='seed-').delete()
            self.stdout.write('Cleared existing seeded jobs.')

        roles = {r.name.lower(): r for r in OccupationRole.objects.all()}
        expires = timezone.now() + timedelta(days=365)  # 1 year for seeded data

        created = 0
        skipped = 0

        with open(csv_path, encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader):
                job_id = row.get('Job_ID', f'JOB{i:04d}').strip()
                title = row.get('Predicted_Job_Title', '').strip()
                company = row.get('Company_Name', 'Unknown').strip()
                location = row.get('Company_Location', 'Remote').strip()
                skills_raw = row.get('Skills', '').strip()
                salary_raw = row.get('Salary (USD)', '').strip()
                industry = row.get('Industry', '').strip()

                if not title:
                    skipped += 1
                    continue

                seed_id = f'seed-{job_id}'

                # Parse salary
                salary_min = salary_max = None
                try:
                    sal = float(salary_raw.replace(',', '').replace('$', ''))
                    salary_min = sal * 0.9
                    salary_max = sal * 1.1
                except (ValueError, AttributeError):
                    pass

                # Skill tags
                skill_tags = [s.strip() for s in skills_raw.split(',') if s.strip()]

                # Match role
                matched_role = None
                for role_name, role_obj in roles.items():
                    if role_name in title.lower() or title.lower() in role_name:
                        matched_role = role_obj
                        break

                # Build a realistic job description
                description = (
                    f"We are looking for a talented {title} to join our team at {company}. "
                    f"This is an exciting opportunity in the {industry} industry based in {location}. "
                    f"\n\nRequired Skills: {skills_raw}. "
                    f"\n\nYou will work on challenging projects, collaborate with cross-functional teams, "
                    f"and contribute to the growth of our organization."
                )

                # Use a real redirect URL (company career pages or LinkedIn)
                redirect_url = f'https://www.linkedin.com/jobs/search/?keywords={title.replace(" ", "%20")}'

                _, was_created = JobListing.objects.update_or_create(
                    adzuna_id=seed_id,
                    defaults={
                        'title': title,
                        'company': company,
                        'location': location,
                        'country': 'us',
                        'description': description,
                        'salary_min': salary_min,
                        'salary_max': salary_max,
                        'redirect_url': redirect_url,
                        'category': industry,
                        'skill_tags': skill_tags,
                        'matched_role': matched_role,
                        'expires_at': expires,
                    }
                )
                if was_created:
                    created += 1

        self.stdout.write(self.style.SUCCESS(
            f'Done. Created {created} job listings, skipped {skipped}.'
        ))
