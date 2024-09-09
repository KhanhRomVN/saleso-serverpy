from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.conf import settings
import os
import pickle
from train.product_recommend_train import update_and_train_product_recommend

BASE_DIR = settings.BASE_DIR
MODEL_PATH = os.path.join(BASE_DIR, 'model', 'recommender_model.pkl')

@require_http_methods(["GET"])
def updateAndTrainProductRecommend(request):
    try:
        result = update_and_train_product_recommend()
        return JsonResponse({'message': result})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def get_product_recommendations(product_id):
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError("Model file not found. Please train the model first.")
    
    with open(MODEL_PATH, 'rb') as f:
        df, cosine_sim = pickle.load(f)
    
    if product_id not in df['id'].values:
        raise ValueError(f"Product ID {product_id} not found in the model data")
    
    idx = df.index[df['id'] == product_id].tolist()[0]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:6]  # Top 5 similar products
    product_indices = [i[0] for i in sim_scores]
    return df['id'].iloc[product_indices].tolist()

@require_http_methods(["GET"])
def get_recommendations(request, id):
    try:
        recommended_ids = get_product_recommendations(id)
        return JsonResponse({'recommended_products': recommended_ids})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)