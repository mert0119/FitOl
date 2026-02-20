import json
import os
import base64
import requests as http_requests
from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from datetime import date
from models import db
from models.food_log import FoodLog

food_photo_bp = Blueprint('food_photo', __name__)

GROQ_API_KEY = os.environ.get('GROQ_API_KEY', '')


def load_foods():
    path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'foods.json')
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


@food_photo_bp.route('/food/photo')
@login_required
def index():
    foods = load_foods()
    return render_template('food/photo.html', foods_json=json.dumps(foods, ensure_ascii=False))


@food_photo_bp.route('/food/photo/analyze', methods=['POST'])
@login_required
def analyze():
    """Fotoğrafı Groq Llama 4 Vision ile analiz et"""
    if 'photo' not in request.files:
        return jsonify({'success': False, 'message': 'Fotoğraf yüklenmedi'})

    photo = request.files['photo']
    image_data = base64.b64encode(photo.read()).decode('utf-8')
    mime_type = photo.content_type or 'image/jpeg'

    prompt = """Sen profesyonel bir diyetisyen ve besin uzmanısın. Bu fotoğraftaki TÜM yemekleri dikkatlice analiz et.

Her yemek için gerçekçi porsiyon tahmini yap ve besin değerlerini hesapla. Türk mutfağını iyi biliyorsun.

Yanıtını SADECE aşağıdaki JSON formatında ver, başka hiçbir şey yazma:

{
  "foods": [
    {
      "name": "Yemek adı (Türkçe)",
      "portion": "Tahmini porsiyon açıklaması",
      "grams": tahmini gram (sayı),
      "calories": kalori (sayı),
      "protein": protein gram (sayı, 1 ondalık),
      "carbs": karbonhidrat gram (sayı, 1 ondalık),
      "fat": yağ gram (sayı, 1 ondalık),
      "fiber": lif gram (sayı, 1 ondalık),
      "confidence": güven yüzdesi 0-100 arası (sayı)
    }
  ],
  "total_calories": toplam kalori (sayı),
  "total_protein": toplam protein (sayı, 1 ondalık),
  "total_carbs": toplam karbonhidrat (sayı, 1 ondalık),
  "total_fat": toplam yağ (sayı, 1 ondalık),
  "description": "Tabağın kısa açıklaması (Türkçe, 1 cümle)",
  "health_score": sağlık puanı 1-10 (sayı),
  "tips": "Kısa beslenme önerisi (Türkçe, 1 cümle)"
}"""

    try:
        resp = http_requests.post(
            'https://api.groq.com/openai/v1/chat/completions',
            headers={
                'Authorization': f'Bearer {GROQ_API_KEY}',
                'Content-Type': 'application/json'
            },
            json={
                'model': 'meta-llama/llama-4-maverick-17b-128e-instruct',
                'messages': [{
                    'role': 'user',
                    'content': [
                        {'type': 'text', 'text': prompt},
                        {'type': 'image_url', 'image_url': {
                            'url': f'data:{mime_type};base64,{image_data}'
                        }}
                    ]
                }],
                'max_tokens': 1500,
                'temperature': 0.2
            },
            timeout=30
        )

        result = resp.json()

        if 'error' in result:
            return jsonify({'success': False, 'message': f"API hatası: {result['error'].get('message', 'Bilinmeyen hata')}"})

        text = result['choices'][0]['message']['content']

        # JSON temizle
        text = text.strip()
        if text.startswith('```'):
            lines = text.split('\n')
            text = '\n'.join(lines[1:])
        if text.endswith('```'):
            text = text[:-3]
        text = text.strip()

        food_data = json.loads(text)
        food_data['success'] = True
        return jsonify(food_data)

    except json.JSONDecodeError:
        return jsonify({'success': False, 'message': 'AI yanıtı işlenemedi, tekrar deneyin'})
    except http_requests.Timeout:
        return jsonify({'success': False, 'message': 'API zaman aşımı — tekrar deneyin'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Hata: {str(e)}'})


@food_photo_bp.route('/food/photo/add', methods=['POST'])
@login_required
def add():
    """Tanınan yemekleri kayda ekle"""
    data = request.get_json()
    foods = data.get('foods', [])
    meal_type = data.get('meal_type', 'ogle')
    added = []

    for food in foods:
        entry = FoodLog(
            user_id=current_user.id,
            date=date.today(),
            meal_type=meal_type,
            food_name=food.get('name', 'Bilinmeyen'),
            portion=1,
            portion_unit='porsiyon',
            calories=food.get('calories', 0),
            protein=food.get('protein', 0),
            carbs=food.get('carbs', 0),
            fat=food.get('fat', 0)
        )
        db.session.add(entry)
        added.append(food.get('name'))

    db.session.commit()
    return jsonify({'success': True, 'message': f'{len(added)} yemek eklendi: {", ".join(added)}'})
