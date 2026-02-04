from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Загружаем места
PLACES = []
try:
    with open('places.json', 'r', encoding='utf-8') as f:
        PLACES = json.load(f)
    print(f"Загружено мест: {len(PLACES)}")
except Exception as e:
    print(f"Ошибка загрузки places.json: {e}")

def generate_route(data):
    days = data.get('days', 1)
    hours = data.get('hours', '8')
    interests = data.get('interests', [])
    budget = data.get('budget', '$')

    places_per_day = 2 if hours == '4' else 3 if hours == '8' else 4
    total_places_needed = days * places_per_day

    price_map = {'$': ['Free', 'Low'], '$$': ['Medium'], '$$$': ['High']}
    allowed_prices = price_map.get(budget, ['Free', 'Low', 'Medium', 'High'])

    matched_places = []
    for place in PLACES:
        if place.get("City", "").strip().lower() != "shenzhen":
            continue
        price = place.get("Price level", "").strip()
        if price and price not in allowed_prices:
            continue
        interest_str = place.get("Interest type", "").replace(',', ';').strip()
        place_interests = [i.strip() for i in interest_str.split(';') if i.strip()]
        if interests:
            if not any(i in place_interests for i in interests):
                continue
        matched_places.append(place)

    if not matched_places:
        matched_places = [p for p in PLACES if p.get("City", "").strip().lower() == "shenzhen"]

    selected = matched_places[:total_places_needed]

    if not selected:
        return "Извини, нет подходящих мест. Попробуй другие параметры."

    route = "🗺 <b>Your Shenzhen trip plan</b> 🇨🇳\n\n"
    idx = 0
    for day in range(1, days + 1):
        day_interests = ', '.join(interests[:2]) if interests else 'Общий'
        route += f"✨ <b>Day {day}</b> — {day_interests}\n"
        for place_num in range(places_per_day):
            if idx < len(selected):
                p = selected[idx]
                emoji = "🌄" if place_num == 0 else "🌆" if place_num == places_per_day - 1 else "☀️"
                route += f"{emoji} <b>{p.get('Name', 'Unknown')}</b>\n"
                desc = p.get('Short description', 'No description')
                route += f"  {desc[:150]}{'...' if len(desc) > 150 else ''}\n"
                route += f"  🚇 Metro: {p.get('Metro station', 'N/A')}\n"
                route += f"  💸 Price: {p.get('Price level', 'N/A')}\n"
                route += f"  📍 District: {p.get('District', 'N/A')}\n\n"
                idx += 1
        route += "─────\n"

    if len(selected) < total_places_needed:
        route += f"⚠️ Найдено только {len(selected)} мест вместо {total_places_needed}.\n"

    route += "\n<b>Tips:</b>\n"
    route += "• Используй метро для перемещений 🚇\n"
    route += "• Копировать название в Amap или Apple Maps\n"
    route += "• Подстраивай темп под себя 🌴\n"

    return route

@app.route('/api/generate', methods=['POST'])
def api_generate():
    try:
        data = request.get_json()
        route = generate_route(data)
        return jsonify({'route': route})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
