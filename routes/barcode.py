import requests
from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from datetime import date
from models import db
from models.food_log import FoodLog

barcode_bp = Blueprint('barcode', __name__)


@barcode_bp.route('/barcode')
@login_required
def scan():
    return render_template('food/barcode.html')


@barcode_bp.route('/barcode/lookup/<barcode>')
@login_required
def lookup(barcode):
    """Open Food Facts API'den ürün bilgisi çek"""
    try:
        url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
        resp = requests.get(url, timeout=5, headers={
            'User-Agent': 'FitOl/1.0 (fitness tracker app)'
        })
        data = resp.json()

        if data.get('status') != 1:
            return jsonify({'found': False, 'message': 'Ürün bulunamadı'})

        product = data.get('product', {})
        nutrients = product.get('nutriments', {})

        # Türkçe veya genel isim
        name = product.get('product_name_tr') or product.get('product_name') or 'Bilinmeyen Ürün'
        brand = product.get('brands', '')
        image = product.get('image_front_small_url', '')

        # 100g başına besin değerleri
        cal_100g = nutrients.get('energy-kcal_100g', 0) or nutrients.get('energy_100g', 0)
        protein_100g = nutrients.get('proteins_100g', 0)
        carbs_100g = nutrients.get('carbohydrates_100g', 0)
        fat_100g = nutrients.get('fat_100g', 0)

        # Porsiyon bilgisi
        serving_size = product.get('serving_size', '100g')
        serving_quantity = product.get('serving_quantity', 100)

        # Porsiyon başına
        ratio = serving_quantity / 100 if serving_quantity else 1
        cal_serving = round(cal_100g * ratio)
        protein_serving = round(protein_100g * ratio, 1)
        carbs_serving = round(carbs_100g * ratio, 1)
        fat_serving = round(fat_100g * ratio, 1)

        return jsonify({
            'found': True,
            'name': name,
            'brand': brand,
            'image': image,
            'barcode': barcode,
            'serving_size': serving_size,
            'per_100g': {
                'calories': round(cal_100g),
                'protein': round(protein_100g, 1),
                'carbs': round(carbs_100g, 1),
                'fat': round(fat_100g, 1)
            },
            'per_serving': {
                'calories': cal_serving,
                'protein': protein_serving,
                'carbs': carbs_serving,
                'fat': fat_serving
            }
        })

    except requests.Timeout:
        return jsonify({'found': False, 'message': 'API zaman aşımı — tekrar deneyin'})
    except Exception as e:
        return jsonify({'found': False, 'message': f'Hata: {str(e)}'})


@barcode_bp.route('/barcode/add', methods=['POST'])
@login_required
def add():
    """Barkod ile taranan ürünü yemek kaydına ekle"""
    data = request.get_json()

    entry = FoodLog(
        user_id=current_user.id,
        date=date.today(),
        meal_type=data.get('meal_type', 'atistirmalik'),
        food_name=data.get('name', 'Barkodlu Ürün'),
        portion=data.get('portion', 1),
        portion_unit='porsiyon',
        calories=data.get('calories', 0),
        protein=data.get('protein', 0),
        carbs=data.get('carbs', 0),
        fat=data.get('fat', 0)
    )
    db.session.add(entry)
    db.session.commit()

    return jsonify({'success': True, 'message': f'{entry.food_name} eklendi!'})
