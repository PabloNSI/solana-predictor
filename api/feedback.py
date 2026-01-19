import json
from datetime import datetime

def handler(request):
    data = request.get_json()
    
    # Guardar feedback en base de datos o CSV
    feedback_entry = {
        'timestamp': datetime.now().isoformat(),
        'prediction': data['prediction'],
        'actual': data.get('actual'),
        'user_rating': data['rating'],
        'comments': data.get('comments')
    }
    
    # Guardar en Vercel KV o PostgreSQL
    # ...
    
    return {'status': 'feedback recorded'}