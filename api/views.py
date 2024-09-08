import pickle
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

@require_http_methods(["GET"])
def get_recommendations(request, product_id):
    try:
        with open('../model/recommendation_model.pkl', 'rb') as f:
            model_data = pickle.load(f)
        
        cosine_sim = model_data['cosine_sim']
        product_ids = model_data['product_ids']
        get_recommendations_func = model_data['get_recommendations']
        
        recommended_ids = get_recommendations_func(product_id, cosine_sim)
        
        return JsonResponse({'recommended_products': recommended_ids})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)