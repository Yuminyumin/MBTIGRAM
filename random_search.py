import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
import xgboost as xgb
from sklearn.preprocessing import LabelEncoder
from scipy.sparse import csr_matrix
from sklearn.model_selection import RandomizedSearchCV
from imblearn.over_sampling import SMOTE
from collections import Counter
import time

# CSV 파일 로드
data = pd.read_csv(r'c:\Users\신유민\Desktop\MBTI 500.csv', encoding='utf-8')
s_data = data.sample(frac=1)  # 샘플링을 위한 shuffle
s_data_s = s_data[1000:8000]

# 텍스트 데이터와 레이블 분리
X = s_data_s['posts']
y = s_data_s['type']

# 결측치를 0으로 대체
s_data_s = s_data_s.copy()
s_data_s['posts'].fillna(0, inplace=True)

# 레이블 인코딩
label_encoder = LabelEncoder()
label_y = label_encoder.fit_transform(y)

# 클래스별 샘플 개수 확인
class_counts = Counter(label_y)
print("Original class counts:", class_counts)

# TF-IDF 벡터화 객체 생성
tfidf_vectorizer = TfidfVectorizer()
X_tfidf = tfidf_vectorizer.fit_transform(X)
print("객체 생성")
# 희소 행렬로 변환
sparse_tfidf_matrix = csr_matrix(X_tfidf)
print("희소 행렬")
# SMOTE를 사용하여 클래스 불균형 보정
smote = SMOTE(k_neighbors=2)
X_resampled, label_y_resampled = smote.fit_resample(sparse_tfidf_matrix, label_y)
print("불균형 보정")
# 조정된 클래스별 샘플 개수 확인
resampled_class_counts = Counter(label_y_resampled)
print("Resampled class counts:", resampled_class_counts)

# 학습 데이터와 테스트 데이터로 분할
X_train, X_test, y_train, y_test = train_test_split(X_resampled, label_y_resampled, test_size=0.3, random_state=42)
print("분할완료")
# XGBoost 학습용 데이터 생성
dtrain = xgb.DMatrix(X_train, label=y_train, enable_categorical=True)
dtest = xgb.DMatrix(X_test, label=y_test, enable_categorical=True)
print("학습용 데이터 생성 완료")
# ----- Model
num_class = len(label_encoder.classes_)

# 하이퍼파라미터 범위 설정
param_dist = {
    'n_estimators': [10, 30],
    'max_depth': [3, 4],
    'learning_rate': [0.1, 0.01]
}
print("하이퍼파라미터 범위 설정 완료")
# XGBoost 모델 초기화
model = xgb.XGBClassifier(objective='multi:softmax', num_class=num_class, random_state=42)
print("모델 초기화 완료")

# RandomizedSearchCV를 사용하여 하이퍼파라미터 탐색
random_search = RandomizedSearchCV(estimator=model, param_distributions=param_dist, cv=4, scoring='accuracy', n_jobs=1)

# 탐색 진행
total_iterations = 8  # 탐색할 총 반복 횟수
random_search.fit(X_train, y_train)

# 실시간 탐색 진행 상황 출력 함수
def print_search_progress(search, total_iterations):
    results = search.cv_results_
    mean_fit_times = results['mean_fit_time']
    mean_scores = results['mean_test_score']

    print("Search Progress:")
    for i in range(total_iterations):
        print(f"Iteration {i+1}/{total_iterations} - Mean Fit Time: {mean_fit_times[i]:.3f}s, Mean Score: {mean_scores[i]:.3f}")

# 실시간 탐색 진행 상황 출력
print_search_progress(random_search, total_iterations)

# 최적의 하이퍼파라미터 조합 출력
print("Best Parameters:", random_search.best_params_)
print("Best Score:", random_search.best_score_)

# 최적의 모델로 재학습
best_model = random_search.best_estimator_
best_model.fit(X_train, y_train)

# 예측
preds = best_model.predict(X_test)

# 예측 결과 출력
for idx, prediction in enumerate(preds):
    predicted_type = label_encoder.inverse_transform([prediction])[0]
    print(f"Sample {idx+1}: {predicted_type}")

# 정확도 계산
accuracy = accuracy_score(y_test, preds)
print(f'Accuracy: {accuracy}')