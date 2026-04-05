"""
python manage.py seed_skills
Loads SkillsDataset.csv into OccupationRole + RequiredSkill tables.
"""
import csv
from django.core.management.base import BaseCommand
from django.conf import settings
from apps.skills.models import OccupationRole, RequiredSkill


class Command(BaseCommand):
    help = 'Seed OccupationRole and RequiredSkill from SkillsDataset.csv'

    def handle(self, *args, **kwargs):
        csv_path = settings.DATA_DIR / 'SkillsDataset.csv'
        if not csv_path.exists():
            self.stderr.write(f'File not found: {csv_path}')
            return

        created_roles = 0
        created_skills = 0

        with open(csv_path, encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                role_name = row.get('Role', '').strip()
                if not role_name:
                    continue

                role, _ = OccupationRole.objects.get_or_create(
                    name=role_name,
                    defaults={'source': 'csv'}
                )
                if _:
                    created_roles += 1

                def add_skills(raw, category):
                    nonlocal created_skills
                    if not raw:
                        return
                    for skill in raw.split(','):
                        skill = skill.strip()
                        if skill:
                            _, created = RequiredSkill.objects.get_or_create(
                                role=role, name=skill,
                                defaults={'category': category, 'importance': 50}
                            )
                            if created:
                                created_skills += 1

                add_skills(row.get('Skills', ''), 'technical')
                add_skills(row.get('Soft Skills', ''), 'soft')
                add_skills(row.get('Advanced Concepts', ''), 'advanced')
                add_skills(row.get('Suggested Certifications & Courses', ''), 'certification')

        self.stdout.write(
            self.style.SUCCESS(
                f'Done. Created {created_roles} roles, {created_skills} skills.'
            )
        )
