"""
ML classifier — trains on JobDataset, persists model to TrainedModel.
"""
import io
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.compose import ColumnTransformer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.preprocessing import OneHotEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import BernoulliNB
from sklearn.svm import LinearSVC
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import logging

logger = logging.getLogger(__name__)

ALGORITHM_MAP = {
    'random_forest': lambda: RandomForestClassifier(n_estimators=100, random_state=42),
    'naive_bayes': lambda: BernoulliNB(),
    'svm': lambda: LinearSVC(max_iter=2000),
    'neural_net': lambda: MLPClassifier(max_iter=500, random_state=42),
}


def _tokenize_skills(x):
    return [s.strip().lower() for s in x.split(',')]


def build_preprocessor():
    return ColumnTransformer(
        transformers=[
            ('skills', CountVectorizer(
                tokenizer=_tokenize_skills,
                token_pattern=None
            ), 'Skills'),
            ('education', OneHotEncoder(handle_unknown='ignore'), ['Education_Level']),
            ('experience', 'passthrough', ['Years_of_Experience']),
        ]
    )


def train_model(algorithm_key):
    """
    Train a model using JobDataset records.
    Returns (TrainedModel instance, metrics dict).
    """
    from apps.ml.models import JobDataset, TrainedModel, ModelPerformance

    qs = JobDataset.objects.all().values(
        'skills', 'years_of_experience', 'education_level', 'job_id'
    )
    if not qs.exists():
        raise ValueError('No training data. Run seed_dataset first.')

    df = pd.DataFrame(list(qs))
    df.columns = ['Skills', 'Years_of_Experience', 'Education_Level', 'Job_ID']
    df = df.dropna()

    X = df[['Skills', 'Years_of_Experience', 'Education_Level']]
    # Predict job title (the meaningful class), not job_id (unique per row)
    from apps.ml.models import JobDataset as JD
    title_map = dict(JD.objects.values_list('job_id', 'predicted_job_title'))
    y = df['Job_ID'].map(title_map)

    alg_factory = ALGORITHM_MAP.get(algorithm_key)
    if alg_factory is None:
        raise ValueError(f'Unknown algorithm: {algorithm_key}')

    preprocessor = build_preprocessor()
    pipeline = make_pipeline(preprocessor, alg_factory())

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)
    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_test)

    metrics = {
        'accuracy': round(accuracy_score(y_test, y_pred), 4),
        'precision': round(precision_score(y_test, y_pred, average='weighted', zero_division=0), 4),
        'recall': round(recall_score(y_test, y_pred, average='weighted', zero_division=0), 4),
        'f1_score': round(f1_score(y_test, y_pred, average='weighted', zero_division=0), 4),
    }

    # Serialize model
    buf = io.BytesIO()
    joblib.dump(pipeline, buf)
    model_bytes = buf.getvalue()

    # Save to DB
    trained = TrainedModel.objects.create(
        algorithm=algorithm_key,
        artifact=model_bytes,
        is_active=True,
    )
    ModelPerformance.objects.create(
        model=trained,
        training_samples=len(df),
        **metrics
    )

    logger.info(f'Trained {algorithm_key}: {metrics}')
    return trained, metrics


def predict(skills_str, years_exp, education_level, algorithm_key='random_forest'):
    """Load active model and predict job title."""
    from apps.ml.models import TrainedModel

    trained = TrainedModel.objects.filter(
        algorithm=algorithm_key, is_active=True
    ).order_by('-trained_at').first()

    if not trained or not trained.artifact:
        raise ValueError(f'No active trained model for {algorithm_key}. Train one first.')

    pipeline = joblib.load(io.BytesIO(bytes(trained.artifact)))

    df = pd.DataFrame([{
        'Skills': skills_str,
        'Years_of_Experience': int(years_exp),
        'Education_Level': education_level,
    }])

    # Returns predicted job title string
    return pipeline.predict(df)[0]
