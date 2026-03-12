from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import requests
import os

app = Flask(__name__, static_folder='.')
CORS(app)

BOAMP_API = 'https://boamp-datadila.opendatasoft.com/api/explore/v2.1/catalog/datasets/boamp/records'

# Mapping départements
DEPTS = {
    '75': {'region': 'Île-de-France', 'name': 'Paris'},
    '77': {'region': 'Île-de-France', 'name': 'Seine-et-Marne'},
    '78': {'region': 'Île-de-France', 'name': 'Yvelines'},
    '91': {'region': 'Île-de-France', 'name': 'Essonne'},
    '92': {'region': 'Île-de-France', 'name': 'Hauts-de-Seine'},
    '93': {'region': 'Île-de-France', 'name': 'Seine-Saint-Denis'},
    '94': {'region': 'Île-de-France', 'name': 'Val-de-Marne'},
    '95': {'region': 'Île-de-France', 'name': "Val-d'Oise"},
    '08': {'region': 'Grand Est', 'name': 'Ardennes'},
    '10': {'region': 'Grand Est', 'name': 'Aube'},
    '51': {'region': 'Grand Est', 'name': 'Marne'},
    '52': {'region': 'Grand Est', 'name': 'Haute-Marne'},
    '54': {'region': 'Grand Est', 'name': 'Meurthe-et-Moselle'},
    '55': {'region': 'Grand Est', 'name': 'Meuse'},
    '57': {'region': 'Grand Est', 'name': 'Moselle'},
    '67': {'region': 'Grand Est', 'name': 'Bas-Rhin'},
    '68': {'region': 'Grand Est', 'name': 'Haut-Rhin'},
    '88': {'region': 'Grand Est', 'name': 'Vosges'},
    '01': {'region': 'Auvergne-Rhône-Alpes', 'name': 'Ain'},
    '03': {'region': 'Auvergne-Rhône-Alpes', 'name': 'Allier'},
    '07': {'region': 'Auvergne-Rhône-Alpes', 'name': 'Ardèche'},
    '15': {'region': 'Auvergne-Rhône-Alpes', 'name': 'Cantal'},
    '26': {'region': 'Auvergne-Rhône-Alpes', 'name': 'Drôme'},
    '38': {'region': 'Auvergne-Rhône-Alpes', 'name': 'Isère'},
    '42': {'region': 'Auvergne-Rhône-Alpes', 'name': 'Loire'},
    '43': {'region': 'Auvergne-Rhône-Alpes', 'name': 'Haute-Loire'},
    '63': {'region': 'Auvergne-Rhône-Alpes', 'name': 'Puy-de-Dôme'},
    '69': {'region': 'Auvergne-Rhône-Alpes', 'name': 'Rhône'},
    '73': {'region': 'Auvergne-Rhône-Alpes', 'name': 'Savoie'},
    '74': {'region': 'Auvergne-Rhône-Alpes', 'name': 'Haute-Savoie'},
    '33': {'region': 'Nouvelle-Aquitaine', 'name': 'Gironde'},
    '31': {'region': 'Occitanie', 'name': 'Haute-Garonne'},
    '34': {'region': 'Occitanie', 'name': 'Hérault'},
    '13': {'region': "Provence-Alpes-Côte d'Azur", 'name': 'Bouches-du-Rhône'},
    '06': {'region': "Provence-Alpes-Côte d'Azur", 'name': 'Alpes-Maritimes'},
    '59': {'region': 'Hauts-de-France', 'name': 'Nord'},
    '44': {'region': 'Pays de la Loire', 'name': 'Loire-Atlantique'},
    '35': {'region': 'Bretagne', 'name': 'Ille-et-Vilaine'},
}

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/api/ao')
def get_ao():
    try:
        search = request.args.get('search', '')
        dept = request.args.get('dept', '')
        min_b = int(request.args.get('min', 0))
        max_b = int(request.args.get('max', 999999999))
        
        # Requête BOAMP
        where = '(objet LIKE "%informatique%" OR objet LIKE "%IT%" OR objet LIKE "%cloud%")'
        if search:
            where = f'(objet LIKE "%{search}%")'
        
        response = requests.get(BOAMP_API, params={'where': where, 'limit': 100}, timeout=30)
        
        if response.status_code != 200:
            return jsonify({'error': True, 'message': f'HTTP {response.status_code}'}), 500
        
        data = response.json()
        results = []
        
        for item in data.get('results', []):
            try:
                f = item.get('fields', {})
                if not f.get('objet'):
                    continue
                
                # Budget
                budget = 0
                m = f.get('montant') or f.get('valeurestimee') or 0
                try:
                    budget = int(float(str(m).replace(' ', '').replace(',', '.')))
                except:
                    pass
                
                if budget < min_b or budget > max_b:
                    continue
                
                # Département
                d = f.get('departement', '')
                if dept and d != dept:
                    continue
                
                dinfo = DEPTS.get(d, {})
                
                results.append({
                    'id': f.get('idweb', 'N/A'),
                    'title': f.get('objet', 'Sans titre'),
                    'client': f.get('denominationsociale') or f.get('nomentite') or 'Non spécifié',
                    'budget': budget,
                    'deadline': f.get('datelimitereponse', 'N/A'),
                    'dept': d,
                    'deptName': dinfo.get('name', d),
                    'region': dinfo.get('region', 'France'),
                    'commune': f.get('commune', ''),
                    'url': f"https://www.boamp.fr/avis/detail/{f.get('idweb', '')}",
                    'source': 'BOAMP',
                    'publishDate': f.get('dateparution', '')
                })
            except:
                continue
        
        return jsonify({'total': len(results), 'results': results})
        
    except Exception as e:
        return jsonify({'error': True, 'message': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
