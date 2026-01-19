import datetime
import json

def handler(request):
    return {
        'statusCode': 200,
        'body': json.dumps({
            'status': 'healthy',
            'model_loaded': True,
            'timestamp': datetime.now().isoformat()
        })
    }