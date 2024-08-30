import pandas as pd
from django.shortcuts import render, HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .util.apriori_analyzer import init_placement_ai
from .util.llm_runner import solve_user_query, give_imp_pairs

def home(request): 
  return render(request, "home.html")

@csrf_exempt
def run_query(request):
  if request.method == 'POST':
    query = request.POST.get('query')

    response = solve_user_query(query)

    return JsonResponse({
      'message': "AI Generated the Response",
      'response': response
    }, status=200)

  return JsonResponse({'error': 'Invalid request method.'}, status=405)

@csrf_exempt 
def upload_csv_files(request):
  if request.method == 'POST':
    products_file = request.FILES.get('products_file')
    purchase_file = request.FILES.get('purchase_file')

    if not products_file or not purchase_file:
      return JsonResponse({'error': 'Both files are required.'}, status=400)

    try:
      products_df = pd.read_csv(products_file)
      purchase_df = pd.read_csv(purchase_file)

      init_placement_ai(products_df=products_df, purchases_df=purchase_df)

      response = solve_user_query("Give some suggestions based on the data, Just use the data to give me top usable pairings and insights.")

      pairings = give_imp_pairs()

      return JsonResponse({
          'message': 'Files uploaded and processed successfully',
          'accessAI': True,
          'response': response,
          'impPairings': pairings
      }, status=200)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
  
  return JsonResponse({'error': 'Invalid request method.'}, status=405)