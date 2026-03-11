"""
AOFinder Backend - Déployable sur Railway
==========================================

Ce backend :
1. Récupère les AO depuis l'API BOAMP
2. Expose une API sans CORS
3. Sert le frontend HTML

Railway détecte automatiquement Python et déploie !
"""

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import requests
import os

app = Flask(__name__, static_folder='.')
CORS(app)  # Autorise tous les domaines

# API BOAMP
BOAMP_API = 'https://boamp-datadila.opendatasoft.com/api/explore/v2.1/catalog/datasets/boamp/records'

# Mapping départements
DEPT_NAMES = {
    '75': 'Paris', '67': 'Bas-Rhin', '68': 'Haut-Rhin', '69': 'Rhône',
    '13': 'Bouches-du-Rhône', '59': 'Nord', '33': 'Gironde', '31': 'Haute-Garonne',
    '44': 'Loire-Atlantique', '06': 'Alpes-Maritimes', '92': 'Hauts-de-Seine',
    '93': 'Seine-Saint-Denis', '94': 'Val-de-Marne', '91': 'Essonne',
    '78': 'Yvelines', '77': 'Seine-et-Marne', '95': "Val-d'Oise",
    '38': 'Isère', '54': 'Meurthe-et-Moselle', '34': 'Hérault',
    '35': 'Ille-et-Vilaine', '29': 'Finistère', '57': 'Moselle',
    '76': 'Seine-Maritime', '01': 'Ain', '03': 'Allier'
}

@app.route('/')
def index():
    """Sert le fichier index.html"""
    return send_from_directory('.', 'index.html')

@app.route('/api/ao')
def get_ao():
    """
    Endpoint API : récupère les AO depuis BOAMP
    
    Paramètres :
    - search : terme de recherche
    - dept : code département (67, 75, etc.)
    - min : budget minimum
    - max : budget maximum
    """
    try:
        # Récupérer les paramètres
        search = request.args.get('search', '')
        dept = request.args.get('dept', '')
        min_budget = int(request.args.get('min', 0))
        max_budget = int(request.args.get('max', 999999999))
        
        # Construire la requête BOAMP
        where = '(objet LIKE "%informatique%" OR objet LIKE "%IT%" OR objet LIKE "%cloud%" OR objet LIKE "%cyber%" OR objet LIKE "%logiciel%" OR objet LIKE "%serveur%" OR objet LIKE "%réseau%")'
        
        if search:
            where = f'(objet LIKE "%{search}%")'
        
        if dept:
            where += f' AND departement="{dept}"'
        
        params = {
            'where': where,
            'limit': 100,
            'offset': 0
        }
        
        print(f"🔍 Requête BOAMP: {where}")
        
        # Appeler l'API BOAMP
        response = requests.get(BOAMP_API, params=params, timeout=30)
        
        if response.status_code != 200:
            return jsonify({
                'error': True,
                'message': f'Erreur API BOAMP: HTTP {response.status_code}'
            }), 500
        
        data = response.json()
        
        # Transformer les données
        results = []
        for item in data.get('results', []):
            try:
                fields = item.get('fields', {}) or item.get('record', {}).get('fields', {})
                
                if not fields.get('objet'):
                    continue
                
                # Extraire le budget
                budget = extract_budget(fields)
                
                # Filtrer par budget
                if budget < min_budget or budget > max_budget:
                    continue
                
                dept_code = fields.get('departement', '')
                
                results.append({
                    'id': fields.get('idweb', item.get('id', 'N/A')),
                    'title': fields.get('objet', 'Sans titre'),
                    'client': fields.get('denominationsociale') or fields.get('nomentite') or fields.get('denomination') or 'Non spécifié',
                    'budget': budget,
                    'deadline': fields.get('datelimitereponse', 'N/A'),
                    'dept': dept_code,
                    'deptName': DEPT_NAMES.get(dept_code, dept_code),
                    'commune': fields.get('commune', ''),
                    'url': f"https://www.boamp.fr/avis/detail/{fields.get('idweb', item.get('id', ''))}",
                    'source': 'BOAMP',
                    'publishDate': fields.get('dateparution', '')
                })
                
            except Exception as e:
                print(f"  ⚠️ Item ignoré: {e}")
                continue
        
        print(f"✅ {len(results)} AO trouvés")
        
        return jsonify({
            'total': len(results),
            'results': results
        })
        
    except requests.exceptions.Timeout:
        return jsonify({
            'error': True,
            'message': "L'API BOAMP met trop de temps à répondre"
        }), 504
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return jsonify({
            'error': True,
            'message': str(e)
        }), 500

def extract_budget(fields):
    """Extrait le budget des champs BOAMP"""
    montant = fields.get('montant') or fields.get('valeurestimee') or fields.get('montantmarche') or 0
    
    if isinstance(montant, str):
        try:
            return int(float(montant.replace(' ', '').replace(',', '.')))
        except:
            return 0
    
    try:
        return int(float(montant))
    except:
        return 0

@app.route('/api/status')
def status():
    """Status de l'API"""
    return jsonify({
        'status': 'online',
        'version': '1.0',
        'boamp_api': BOAMP_API,
        'cors': 'enabled'
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
