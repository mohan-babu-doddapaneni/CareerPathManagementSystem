from django.core.management.base import BaseCommand
from apps.courses.models import Course


COURSES = [
    # Python
    {'title': 'Python for Everybody', 'platform': 'coursera', 'url': 'https://www.coursera.org/specializations/python', 'skill_tags': 'python,programming,data structures', 'difficulty': 'beginner', 'duration_hours': 40, 'is_free': True, 'rating': 4.8},
    {'title': 'Python Crash Course – Full Tutorial', 'platform': 'youtube', 'url': 'https://www.youtube.com/watch?v=rfscVS0vtbw', 'skill_tags': 'python,programming', 'difficulty': 'beginner', 'duration_hours': 4, 'is_free': True, 'rating': 4.7},
    {'title': 'Automate the Boring Stuff with Python', 'platform': 'udemy', 'url': 'https://www.udemy.com/course/automate/', 'skill_tags': 'python,automation,scripting', 'difficulty': 'beginner', 'duration_hours': 9, 'is_free': False, 'rating': 4.7},
    # JavaScript
    {'title': 'JavaScript Algorithms and Data Structures', 'platform': 'freecodecamp', 'url': 'https://www.freecodecamp.org/learn/javascript-algorithms-and-data-structures/', 'skill_tags': 'javascript,algorithms,data structures', 'difficulty': 'beginner', 'duration_hours': 30, 'is_free': True, 'rating': 4.8},
    {'title': 'The Complete JavaScript Course', 'platform': 'udemy', 'url': 'https://www.udemy.com/course/the-complete-javascript-course/', 'skill_tags': 'javascript,es6,nodejs', 'difficulty': 'beginner', 'duration_hours': 69, 'is_free': False, 'rating': 4.7},
    {'title': 'JavaScript Full Course for Beginners', 'platform': 'youtube', 'url': 'https://www.youtube.com/watch?v=PkZNo7MFNFg', 'skill_tags': 'javascript,programming', 'difficulty': 'beginner', 'duration_hours': 3, 'is_free': True, 'rating': 4.6},
    # Machine Learning / AI
    {'title': 'Machine Learning Specialization', 'platform': 'coursera', 'url': 'https://www.coursera.org/specializations/machine-learning-introduction', 'skill_tags': 'machine learning,python,sklearn,supervised learning,neural networks', 'difficulty': 'intermediate', 'duration_hours': 60, 'is_free': True, 'rating': 4.9},
    {'title': 'Deep Learning Specialization', 'platform': 'coursera', 'url': 'https://www.coursera.org/specializations/deep-learning', 'skill_tags': 'deep learning,neural networks,tensorflow,python', 'difficulty': 'advanced', 'duration_hours': 80, 'is_free': True, 'rating': 4.9},
    {'title': 'Intro to Machine Learning – Kaggle', 'platform': 'kaggle', 'url': 'https://www.kaggle.com/learn/intro-to-machine-learning', 'skill_tags': 'machine learning,python,sklearn', 'difficulty': 'beginner', 'duration_hours': 3, 'is_free': True, 'rating': 4.7},
    {'title': 'Fast.ai Practical Deep Learning', 'platform': 'other', 'url': 'https://course.fast.ai/', 'skill_tags': 'deep learning,pytorch,python,computer vision', 'difficulty': 'intermediate', 'duration_hours': 40, 'is_free': True, 'rating': 4.8},
    # Data Science
    {'title': 'Data Science Professional Certificate', 'platform': 'coursera', 'url': 'https://www.coursera.org/professional-certificates/ibm-data-science', 'skill_tags': 'data science,python,pandas,sql,machine learning,data visualization', 'difficulty': 'beginner', 'duration_hours': 120, 'is_free': True, 'rating': 4.6},
    {'title': 'Pandas Tutorial – Full Course', 'platform': 'youtube', 'url': 'https://www.youtube.com/watch?v=vmEHCJofslg', 'skill_tags': 'pandas,python,data analysis', 'difficulty': 'beginner', 'duration_hours': 4, 'is_free': True, 'rating': 4.7},
    {'title': 'Data Analysis with Python – freeCodeCamp', 'platform': 'freecodecamp', 'url': 'https://www.freecodecamp.org/learn/data-analysis-with-python/', 'skill_tags': 'python,pandas,numpy,data analysis', 'difficulty': 'intermediate', 'duration_hours': 20, 'is_free': True, 'rating': 4.6},
    # SQL
    {'title': 'SQL for Data Science', 'platform': 'coursera', 'url': 'https://www.coursera.org/learn/sql-for-data-science', 'skill_tags': 'sql,databases,data analysis', 'difficulty': 'beginner', 'duration_hours': 14, 'is_free': True, 'rating': 4.6},
    {'title': 'SQL Tutorial – Full Database Course', 'platform': 'freecodecamp', 'url': 'https://www.youtube.com/watch?v=HXV3zeQKqGY', 'skill_tags': 'sql,databases,postgresql,mysql', 'difficulty': 'beginner', 'duration_hours': 4, 'is_free': True, 'rating': 4.8},
    {'title': 'Intro to SQL – Kaggle', 'platform': 'kaggle', 'url': 'https://www.kaggle.com/learn/intro-to-sql', 'skill_tags': 'sql,bigquery,databases', 'difficulty': 'beginner', 'duration_hours': 3, 'is_free': True, 'rating': 4.7},
    # React
    {'title': 'React – The Complete Guide', 'platform': 'udemy', 'url': 'https://www.udemy.com/course/react-the-complete-guide-incl-redux/', 'skill_tags': 'react,javascript,redux,hooks', 'difficulty': 'intermediate', 'duration_hours': 49, 'is_free': False, 'rating': 4.8},
    {'title': 'Full Stack Open – React', 'platform': 'other', 'url': 'https://fullstackopen.com/en/', 'skill_tags': 'react,nodejs,javascript,graphql,typescript', 'difficulty': 'intermediate', 'duration_hours': 80, 'is_free': True, 'rating': 4.9},
    # Node.js
    {'title': 'Node.js Crash Course', 'platform': 'youtube', 'url': 'https://www.youtube.com/watch?v=fBNz5xF-Kx4', 'skill_tags': 'nodejs,javascript,express', 'difficulty': 'beginner', 'duration_hours': 1, 'is_free': True, 'rating': 4.7},
    # Django
    {'title': 'Django for Everybody', 'platform': 'coursera', 'url': 'https://www.coursera.org/specializations/django', 'skill_tags': 'django,python,web development,rest api', 'difficulty': 'intermediate', 'duration_hours': 60, 'is_free': True, 'rating': 4.8},
    {'title': 'Django Crash Course', 'platform': 'youtube', 'url': 'https://www.youtube.com/watch?v=e1IyzVyrLSU', 'skill_tags': 'django,python,web development', 'difficulty': 'beginner', 'duration_hours': 2, 'is_free': True, 'rating': 4.6},
    # Cloud / AWS / Azure / GCP
    {'title': 'AWS Cloud Practitioner Essentials', 'platform': 'coursera', 'url': 'https://www.coursera.org/learn/aws-cloud-practitioner-essentials', 'skill_tags': 'aws,cloud computing,devops', 'difficulty': 'beginner', 'duration_hours': 12, 'is_free': True, 'rating': 4.7},
    {'title': 'Google Cloud Fundamentals', 'platform': 'coursera', 'url': 'https://www.coursera.org/learn/gcp-fundamentals', 'skill_tags': 'gcp,cloud computing,google cloud', 'difficulty': 'beginner', 'duration_hours': 9, 'is_free': True, 'rating': 4.6},
    {'title': 'AZ-900 Microsoft Azure Fundamentals', 'platform': 'microsoft', 'url': 'https://learn.microsoft.com/en-us/training/paths/az-900-describe-cloud-concepts/', 'skill_tags': 'azure,cloud computing,microsoft', 'difficulty': 'beginner', 'duration_hours': 10, 'is_free': True, 'rating': 4.7},
    # Docker / Kubernetes / DevOps
    {'title': 'Docker and Kubernetes: The Practical Guide', 'platform': 'udemy', 'url': 'https://www.udemy.com/course/docker-kubernetes-the-practical-guide/', 'skill_tags': 'docker,kubernetes,devops,containers', 'difficulty': 'intermediate', 'duration_hours': 23, 'is_free': False, 'rating': 4.7},
    {'title': 'Docker Tutorial for Beginners', 'platform': 'youtube', 'url': 'https://www.youtube.com/watch?v=3c-iBn73dDE', 'skill_tags': 'docker,containers,devops', 'difficulty': 'beginner', 'duration_hours': 2, 'is_free': True, 'rating': 4.7},
    {'title': 'DevOps Prerequisites Course', 'platform': 'youtube', 'url': 'https://www.youtube.com/watch?v=Wvf0mBNGjXY', 'skill_tags': 'devops,linux,networking,git', 'difficulty': 'beginner', 'duration_hours': 3, 'is_free': True, 'rating': 4.6},
    # Cybersecurity
    {'title': 'Google Cybersecurity Certificate', 'platform': 'coursera', 'url': 'https://www.coursera.org/professional-certificates/google-cybersecurity', 'skill_tags': 'cybersecurity,network security,linux,sql,python', 'difficulty': 'beginner', 'duration_hours': 180, 'is_free': True, 'rating': 4.8},
    {'title': 'CompTIA Security+ Study Course', 'platform': 'youtube', 'url': 'https://www.youtube.com/watch?v=9NE33fpQuw8', 'skill_tags': 'cybersecurity,security+,network security,cryptography', 'difficulty': 'intermediate', 'duration_hours': 10, 'is_free': True, 'rating': 4.7},
    # Git / Version Control
    {'title': 'Git and GitHub for Beginners', 'platform': 'freecodecamp', 'url': 'https://www.youtube.com/watch?v=RGOj5yH7evk', 'skill_tags': 'git,github,version control', 'difficulty': 'beginner', 'duration_hours': 1, 'is_free': True, 'rating': 4.8},
    # TypeScript
    {'title': 'TypeScript Course for Beginners', 'platform': 'youtube', 'url': 'https://www.youtube.com/watch?v=BwuLxPH8IDs', 'skill_tags': 'typescript,javascript,angular', 'difficulty': 'beginner', 'duration_hours': 3, 'is_free': True, 'rating': 4.7},
    # TensorFlow / PyTorch
    {'title': 'TensorFlow Developer Certificate', 'platform': 'coursera', 'url': 'https://www.coursera.org/professional-certificates/tensorflow-in-practice', 'skill_tags': 'tensorflow,deep learning,python,computer vision,nlp', 'difficulty': 'intermediate', 'duration_hours': 60, 'is_free': True, 'rating': 4.7},
    {'title': 'PyTorch for Deep Learning – Full Course', 'platform': 'youtube', 'url': 'https://www.youtube.com/watch?v=V_xro1bcAuA', 'skill_tags': 'pytorch,deep learning,python', 'difficulty': 'intermediate', 'duration_hours': 25, 'is_free': True, 'rating': 4.8},
    # System Design
    {'title': 'System Design for Interviews', 'platform': 'youtube', 'url': 'https://www.youtube.com/watch?v=UzLMhqg3_Wc', 'skill_tags': 'system design,scalability,databases,microservices', 'difficulty': 'advanced', 'duration_hours': 2, 'is_free': True, 'rating': 4.8},
    # Algorithms / DSA
    {'title': 'Data Structures and Algorithms in Python', 'platform': 'udemy', 'url': 'https://www.udemy.com/course/data-structures-algorithms-python/', 'skill_tags': 'algorithms,data structures,python,leetcode', 'difficulty': 'intermediate', 'duration_hours': 20, 'is_free': False, 'rating': 4.5},
    {'title': 'Algorithms – Stanford', 'platform': 'coursera', 'url': 'https://www.coursera.org/specializations/algorithms', 'skill_tags': 'algorithms,data structures,graph theory,dynamic programming', 'difficulty': 'advanced', 'duration_hours': 80, 'is_free': True, 'rating': 4.9},
    # Soft Skills
    {'title': 'Communication Skills – How to Communicate Effectively', 'platform': 'coursera', 'url': 'https://www.coursera.org/learn/communication-skills', 'skill_tags': 'communication,soft skills,leadership,presentation', 'difficulty': 'beginner', 'duration_hours': 10, 'is_free': True, 'rating': 4.5},
    {'title': 'Agile Project Management', 'platform': 'google', 'url': 'https://www.coursera.org/professional-certificates/google-project-management', 'skill_tags': 'agile,scrum,project management,teamwork', 'difficulty': 'beginner', 'duration_hours': 180, 'is_free': True, 'rating': 4.8},
    # Blockchain
    {'title': 'Blockchain Specialization', 'platform': 'coursera', 'url': 'https://www.coursera.org/specializations/blockchain', 'skill_tags': 'blockchain,ethereum,solidity,smart contracts', 'difficulty': 'intermediate', 'duration_hours': 60, 'is_free': True, 'rating': 4.5},
    # Mobile Development
    {'title': 'Android Developer Fundamentals', 'platform': 'google', 'url': 'https://developer.android.com/courses', 'skill_tags': 'android,kotlin,java,mobile development', 'difficulty': 'beginner', 'duration_hours': 30, 'is_free': True, 'rating': 4.6},
    {'title': 'Flutter & Dart – The Complete Guide', 'platform': 'udemy', 'url': 'https://www.udemy.com/course/learn-flutter-dart-to-build-ios-android-apps/', 'skill_tags': 'flutter,dart,mobile development,ios,android', 'difficulty': 'intermediate', 'duration_hours': 42, 'is_free': False, 'rating': 4.7},
    # Linux
    {'title': 'The Linux Command Line Bootcamp', 'platform': 'udemy', 'url': 'https://www.udemy.com/course/the-linux-command-line-bootcamp/', 'skill_tags': 'linux,bash,command line,shell scripting', 'difficulty': 'beginner', 'duration_hours': 22, 'is_free': False, 'rating': 4.7},
    {'title': 'Linux for Beginners', 'platform': 'youtube', 'url': 'https://www.youtube.com/watch?v=sWbUDq4S6Y8', 'skill_tags': 'linux,operating systems,bash', 'difficulty': 'beginner', 'duration_hours': 3, 'is_free': True, 'rating': 4.6},
    # NLP
    {'title': 'Natural Language Processing Specialization', 'platform': 'coursera', 'url': 'https://www.coursera.org/specializations/natural-language-processing', 'skill_tags': 'nlp,deep learning,python,transformers,bert', 'difficulty': 'advanced', 'duration_hours': 80, 'is_free': True, 'rating': 4.7},
    # Computer Vision
    {'title': 'Computer Vision with Python', 'platform': 'kaggle', 'url': 'https://www.kaggle.com/learn/computer-vision', 'skill_tags': 'computer vision,deep learning,python,cnn', 'difficulty': 'intermediate', 'duration_hours': 5, 'is_free': True, 'rating': 4.7},
    # Statistics / Math
    {'title': 'Statistics with Python Specialization', 'platform': 'coursera', 'url': 'https://www.coursera.org/specializations/statistics-with-python', 'skill_tags': 'statistics,python,data analysis,probability', 'difficulty': 'intermediate', 'duration_hours': 60, 'is_free': True, 'rating': 4.6},
]


class Command(BaseCommand):
    help = 'Seed curated course recommendations into the database'

    def handle(self, *args, **kwargs):
        created = 0
        for data in COURSES:
            _, c = Course.objects.get_or_create(
                title=data['title'],
                platform=data['platform'],
                defaults=data,
            )
            if c:
                created += 1
        self.stdout.write(self.style.SUCCESS(f'Done. {created} courses created ({len(COURSES)} total).'))
