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

# Mapping départements → régions et noms complets
DEPT_TO_REGION = {
    # Île-de-France
    '75': {'region': 'Île-de-France', 'name': 'Paris'},
    '77': {'region': 'Île-de-France', 'name': 'Seine-et-Marne'},
    '78': {'region': 'Île-de-France', 'name': 'Yvelines'},
    '91': {'region': 'Île-de-France', 'name': 'Essonne'},
    '92': {'region': 'Île-de-France', 'name': 'Hauts-de-Seine'},
    '93': {'region': 'Île-de-France', 'name': 'Seine-Saint-Denis'},
    '94': {'region': 'Île-de-France', 'name': 'Val-de-Marne'},
    '95': {'region': 'Île-de-France', 'name': "Val-d'Oise"},
    # Grand Est
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
    # Auvergne-Rhône-Alpes
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
    # Nouvelle-Aquitaine
    '16': {'region': 'Nouvelle-Aquitaine', 'name': 'Charente'},
    '17': {'region': 'Nouvelle-Aquitaine', 'name': 'Charente-Maritime'},
    '19': {'region': 'Nouvelle-Aquitaine', 'name': 'Corrèze'},
    '23': {'region': 'Nouvelle-Aquitaine', 'name': 'Creuse'},
    '24': {'region': 'Nouvelle-Aquitaine', 'name': 'Dordogne'},
    '33': {'region': 'Nouvelle-Aquitaine', 'name': 'Gironde'},
    '40': {'region': 'Nouvelle-Aquitaine', 'name': 'Landes'},
    '47': {'region': 'Nouvelle-Aquitaine', 'name': 'Lot-et-Garonne'},
    '64': {'region': 'Nouvelle-Aquitaine', 'name': 'Pyrénées-Atlantiques'},
    '79': {'region': 'Nouvelle-Aquitaine', 'name': 'Deux-Sèvres'},
    '86': {'region': 'Nouvelle-Aquitaine', 'name': 'Vienne'},
    '87': {'region': 'Nouvelle-Aquitaine', 'name': 'Haute-Vienne'},
    # Occitanie
    '09': {'region': 'Occitanie', 'name': 'Ariège'},
    '11': {'region': 'Occitanie', 'name': 'Aude'},
    '12': {'region': 'Occitanie', 'name': 'Aveyron'},
    '30': {'region': 'Occitanie', 'name': 'Gard'},
    '31': {'region': 'Occitanie', 'name': 'Haute-Garonne'},
    '32': {'region': 'Occitanie', 'name': 'Gers'},
    '34': {'region': 'Occitanie', 'name': 'Hérault'},
    '46': {'region': 'Occitanie', 'name': 'Lot'},
    '48': {'region': 'Occitanie', 'name': 'Lozère'},
    '65': {'region': 'Occitanie', 'name': 'Hautes-Pyrénées'},
    '66': {'region': 'Occitanie', 'name': 'Pyrénées-Orientales'},
    '81': {'region': 'Occitanie', 'name': 'Tarn'},
    '82': {'region': 'Occitanie', 'name': 'Tarn-et-Garonne'},
    # PACA
    '04': {'region': "Provence-Alpes-Côte d'Azur", 'name': 'Alpes-de-Haute-Provence'},
    '05': {'region': "Provence-Alpes-Côte d'Azur", 'name': 'Hautes-Alpes'},
    '06': {'region': "Provence-Alpes-Côte d'Azur", 'name': 'Alpes-Maritimes'},
    '13': {'region': "Provence-Alpes-Côte d'Azur", 'name': 'Bouches-du-Rhône'},
    '83': {'region': "Provence-Alpes-Côte d'Azur", 'name': 'Var'},
    '84': {'region': "Provence-Alpes-Côte d'Azur", 'name': 'Vaucluse'},
    # Hauts-de-France
    '02': {'region': 'Hauts-de-France', 'name': 'Aisne'},
    '59': {'region': 'Hauts-de-France', 'name': 'Nord'},
    '60': {'region': 'Hauts-de-France', 'name': 'Oise'},
    '62': {'region': 'Hauts-de-France', 'name': 'Pas-de-Calais'},
    '80': {'region': 'Hauts-de-France', 'name': 'Somme'},
    # Normandie
    '14': {'region': 'Normandie', 'name': 'Calvados'},
    '27': {'region': 'Normandie', 'name': 'Eure'},
    '50': {'region': 'Normandie', 'name': 'Manche'},
    '61': {'region': 'Normandie', 'name': 'Orne'},
    '76': {'region': 'Normandie', 'name': 'Seine-Maritime'},
    # Bretagne
    '22': {'region': 'Bretagne', 'name': "Côtes-d'Armor"},
    '29': {'region': 'Bretagne', 'name': 'Finistère'},
    '35': {'region': 'Bretagne', 'name': 'Ille-et-Vilaine'},
    '56': {'region': 'Bretagne', 'name': 'Morbihan'},
    # Pays de la Loire
    '44': {'region': 'Pays de la Loire', 'name': 'Loire-Atlantique'},
    '49': {'region': 'Pays de la Loire', 'name': 'Maine-et-Loire'},
    '53': {'region': 'Pays de la Loire', 'name': 'Mayenne'},
    '72': {'region': 'Pays de la Loire', 'name': 'Sarthe'},
    '85': {'region': 'Pays de la Loire', 'name': 'Vendée'},
    # Centre-Val de Loire
    '18': {'region': 'Centre-Val de Loire', 'name': 'Cher'},
    '28': {'region': 'Centre-Val de Loire', 'name': 'Eure-et-Loir'},
    '36': {'region': 'Centre-Val de Loire', 'name': 'Indre'},
    '37': {'region': 'Centre-Val de Loire', 'name': 'Indre-et-Loire'},
    '41': {'region': 'Centre-Val de Loire', 'name': 'Loir-et-Cher'},
    '45': {'region': 'Centre-Val de Loire', 'name': 'Loiret'},
    # Bourgogne-Franche-Comté
    '21': {'region': 'Bourgogne-Franche-Comté', 'name': 'Côte-d\'Or'},
    '25': {'region': 'Bourgogne-Franche-Comté', 'name': 'Doubs'},
    '39': {'region': 'Bourgogne-Franche-Comté', 'name': 'Jura'},
    '58': {'region': 'Bourgogne-Franche-Comté', 'name': 'Nièvre'},
    '70': {'region': 'Bourgogne-Franche-Comté', 'name': 'Haute-Saône'},
    '71': {'region': 'Bourgogne-Franche-Comté', 'name': 'Saône-et-Loire'},
    '89': {'region': 'Bourgogne-Franche-Comté', 'name': 'Yonne'},
    '90': {'region': 'Bourgogne-Franche-Comté', 'name': 'Territoire de Belfort'},
    # Corse
    '2A': {'region': 'Corse', 'name': 'Corse-du-Sud'},
    '2B': {'region': 'Corse', 'name': 'Haute-Corse'},
}

def get_dept_info(dept_code):
    """Retourne les infos complètes d'un département"""
    info = DEPT_TO_REGION.get(dept_code, {})
    return {
        'code': dept_code,
        'name': info.get('name', dept_code),
        'region': info.get('region', 'France')
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
        
        print(f"🔍 Requête reçue: search={search}, dept={dept}, min={min_budget}, max={max_budget}")
        
        # Construire la requête BOAMP
        where = '(objet LIKE "%informatique%" OR objet LIKE "%IT%" OR objet LIKE "%cloud%" OR objet LIKE "%cyber%" OR objet LIKE "%logiciel%" OR objet LIKE "%serveur%" OR objet LIKE "%réseau%")'
        
        if search:
            where = f'(objet LIKE "%{search}%")'
        
        # Ne PAS filtrer par département dans la requête API
        # On va filtrer côté serveur après avoir reçu les résultats
        
        params = {
            'where': where,
            'limit': 100,
            'offset': 0
        }
        
        print(f"🔍 Requête BOAMP: {where}")
        if dept:
            print(f"📍 Filtre département côté serveur: {dept}")
        
        # Appeler l'API BOAMP
        response = requests.get(BOAMP_API, params=params, timeout=30)
        
        if response.status_code != 200:
            error_msg = f'Erreur API BOAMP: HTTP {response.status_code}'
            print(f"❌ {error_msg}")
            return jsonify({
                'error': True,
                'message': error_msg
            }), 500
        
        data = response.json()
        print(f"✅ Réponse BOAMP: {len(data.get('results', []))} résultats")
        
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
                
                # Filtrer par département côté serveur
                if dept and dept_code != dept:
                    continue
                
                dept_info = get_dept_info(dept_code)
                
                results.append({
                    'id': fields.get('idweb', item.get('id', 'N/A')),
                    'title': fields.get('objet', 'Sans titre'),
                    'client': fields.get('denominationsociale') or fields.get('nomentite') or fields.get('denomination') or 'Non spécifié',
                    'budget': budget,
                    'deadline': fields.get('datelimitereponse', 'N/A'),
                    'dept': dept_info['code'],
                    'deptName': dept_info['name'],
                    'region': dept_info['region'],
                    'commune': fields.get('commune', ''),
                    'url': f"https://www.boamp.fr/avis/detail/{fields.get('idweb', item.get('id', ''))}",
                    'source': 'BOAMP',
                    'publishDate': fields.get('dateparution', '')
                })
                
            except Exception as e:
                print(f"  ⚠️ Item ignoré: {e}")
                continue
        
        print(f"✅ {len(results)} AO après filtres")
        
        return jsonify({
            'total': len(results),
            'results': results
        })
        
    except requests.exceptions.Timeout:
        print("❌ Timeout API BOAMP")
        return jsonify({
            'error': True,
            'message': "L'API BOAMP met trop de temps à répondre"
        }), 504
        
    except Exception as e:
        print(f"❌ Erreur serveur: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': True,
            'message': f"Erreur serveur: {str(e)}"
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
    # Railway définit automatiquement PORT
    port = int(os.environ.get('PORT', 8080))
    print(f"🚀 Démarrage sur le port {port}")
    app.run(host='0.0.0.0', port=port)
