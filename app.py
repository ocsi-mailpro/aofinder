from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import requests
import os

app = Flask(__name__, static_folder='.')
CORS(app)

BOAMP_API = 'https://boamp-datadila.opendatasoft.com/api/explore/v2.1/catalog/datasets/boamp/records'

# TOUS les départements français
DEPTS = {
    '01': {'region': 'Auvergne-Rhône-Alpes', 'name': 'Ain'}, '02': {'region': 'Hauts-de-France', 'name': 'Aisne'},
    '03': {'region': 'Auvergne-Rhône-Alpes', 'name': 'Allier'}, '04': {'region': "PACA", 'name': 'Alpes-de-Haute-Provence'},
    '05': {'region': "PACA", 'name': 'Hautes-Alpes'}, '06': {'region': "PACA", 'name': 'Alpes-Maritimes'},
    '07': {'region': 'Auvergne-Rhône-Alpes', 'name': 'Ardèche'}, '08': {'region': 'Grand Est', 'name': 'Ardennes'},
    '09': {'region': 'Occitanie', 'name': 'Ariège'}, '10': {'region': 'Grand Est', 'name': 'Aube'},
    '11': {'region': 'Occitanie', 'name': 'Aude'}, '12': {'region': 'Occitanie', 'name': 'Aveyron'},
    '13': {'region': "PACA", 'name': 'Bouches-du-Rhône'}, '14': {'region': 'Normandie', 'name': 'Calvados'},
    '15': {'region': 'Auvergne-Rhône-Alpes', 'name': 'Cantal'}, '16': {'region': 'Nouvelle-Aquitaine', 'name': 'Charente'},
    '17': {'region': 'Nouvelle-Aquitaine', 'name': 'Charente-Maritime'}, '18': {'region': 'Centre-Val de Loire', 'name': 'Cher'},
    '19': {'region': 'Nouvelle-Aquitaine', 'name': 'Corrèze'}, '21': {'region': 'Bourgogne-Franche-Comté', 'name': "Côte-d'Or"},
    '22': {'region': 'Bretagne', 'name': "Côtes-d'Armor"}, '23': {'region': 'Nouvelle-Aquitaine', 'name': 'Creuse'},
    '24': {'region': 'Nouvelle-Aquitaine', 'name': 'Dordogne'}, '25': {'region': 'Bourgogne-Franche-Comté', 'name': 'Doubs'},
    '26': {'region': 'Auvergne-Rhône-Alpes', 'name': 'Drôme'}, '27': {'region': 'Normandie', 'name': 'Eure'},
    '28': {'region': 'Centre-Val de Loire', 'name': 'Eure-et-Loir'}, '29': {'region': 'Bretagne', 'name': 'Finistère'},
    '30': {'region': 'Occitanie', 'name': 'Gard'}, '31': {'region': 'Occitanie', 'name': 'Haute-Garonne'},
    '32': {'region': 'Occitanie', 'name': 'Gers'}, '33': {'region': 'Nouvelle-Aquitaine', 'name': 'Gironde'},
    '34': {'region': 'Occitanie', 'name': 'Hérault'}, '35': {'region': 'Bretagne', 'name': 'Ille-et-Vilaine'},
    '36': {'region': 'Centre-Val de Loire', 'name': 'Indre'}, '37': {'region': 'Centre-Val de Loire', 'name': 'Indre-et-Loire'},
    '38': {'region': 'Auvergne-Rhône-Alpes', 'name': 'Isère'}, '39': {'region': 'Bourgogne-Franche-Comté', 'name': 'Jura'},
    '40': {'region': 'Nouvelle-Aquitaine', 'name': 'Landes'}, '41': {'region': 'Centre-Val de Loire', 'name': 'Loir-et-Cher'},
    '42': {'region': 'Auvergne-Rhône-Alpes', 'name': 'Loire'}, '43': {'region': 'Auvergne-Rhône-Alpes', 'name': 'Haute-Loire'},
    '44': {'region': 'Pays de la Loire', 'name': 'Loire-Atlantique'}, '45': {'region': 'Centre-Val de Loire', 'name': 'Loiret'},
    '46': {'region': 'Occitanie', 'name': 'Lot'}, '47': {'region': 'Nouvelle-Aquitaine', 'name': 'Lot-et-Garonne'},
    '48': {'region': 'Occitanie', 'name': 'Lozère'}, '49': {'region': 'Pays de la Loire', 'name': 'Maine-et-Loire'},
    '50': {'region': 'Normandie', 'name': 'Manche'}, '51': {'region': 'Grand Est', 'name': 'Marne'},
    '52': {'region': 'Grand Est', 'name': 'Haute-Marne'}, '53': {'region': 'Pays de la Loire', 'name': 'Mayenne'},
    '54': {'region': 'Grand Est', 'name': 'Meurthe-et-Moselle'}, '55': {'region': 'Grand Est', 'name': 'Meuse'},
    '56': {'region': 'Bretagne', 'name': 'Morbihan'}, '57': {'region': 'Grand Est', 'name': 'Moselle'},
    '58': {'region': 'Bourgogne-Franche-Comté', 'name': 'Nièvre'}, '59': {'region': 'Hauts-de-France', 'name': 'Nord'},
    '60': {'region': 'Hauts-de-France', 'name': 'Oise'}, '61': {'region': 'Normandie', 'name': 'Orne'},
    '62': {'region': 'Hauts-de-France', 'name': 'Pas-de-Calais'}, '63': {'region': 'Auvergne-Rhône-Alpes', 'name': 'Puy-de-Dôme'},
    '64': {'region': 'Nouvelle-Aquitaine', 'name': 'Pyrénées-Atlantiques'}, '65': {'region': 'Occitanie', 'name': 'Hautes-Pyrénées'},
    '66': {'region': 'Occitanie', 'name': 'Pyrénées-Orientales'}, '67': {'region': 'Grand Est', 'name': 'Bas-Rhin'},
    '68': {'region': 'Grand Est', 'name': 'Haut-Rhin'}, '69': {'region': 'Auvergne-Rhône-Alpes', 'name': 'Rhône'},
    '70': {'region': 'Bourgogne-Franche-Comté', 'name': 'Haute-Saône'}, '71': {'region': 'Bourgogne-Franche-Comté', 'name': 'Saône-et-Loire'},
    '72': {'region': 'Pays de la Loire', 'name': 'Sarthe'}, '73': {'region': 'Auvergne-Rhône-Alpes', 'name': 'Savoie'},
    '74': {'region': 'Auvergne-Rhône-Alpes', 'name': 'Haute-Savoie'}, '75': {'region': 'Île-de-France', 'name': 'Paris'},
    '76': {'region': 'Normandie', 'name': 'Seine-Maritime'}, '77': {'region': 'Île-de-France', 'name': 'Seine-et-Marne'},
    '78': {'region': 'Île-de-France', 'name': 'Yvelines'}, '79': {'region': 'Nouvelle-Aquitaine', 'name': 'Deux-Sèvres'},
    '80': {'region': 'Hauts-de-France', 'name': 'Somme'}, '81': {'region': 'Occitanie', 'name': 'Tarn'},
    '82': {'region': 'Occitanie', 'name': 'Tarn-et-Garonne'}, '83': {'region': "PACA", 'name': 'Var'},
    '84': {'region': "PACA", 'name': 'Vaucluse'}, '85': {'region': 'Pays de la Loire', 'name': 'Vendée'},
    '86': {'region': 'Nouvelle-Aquitaine', 'name': 'Vienne'}, '87': {'region': 'Nouvelle-Aquitaine', 'name': 'Haute-Vienne'},
    '88': {'region': 'Grand Est', 'name': 'Vosges'}, '89': {'region': 'Bourgogne-Franche-Comté', 'name': 'Yonne'},
    '90': {'region': 'Bourgogne-Franche-Comté', 'name': 'Territoire de Belfort'}, '91': {'region': 'Île-de-France', 'name': 'Essonne'},
    '92': {'region': 'Île-de-France', 'name': 'Hauts-de-Seine'}, '93': {'region': 'Île-de-France', 'name': 'Seine-Saint-Denis'},
    '94': {'region': 'Île-de-France', 'name': 'Val-de-Marne'}, '95': {'region': 'Île-de-France', 'name': "Val-d'Oise"},
}

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/api/ao')
def get_ao():
    try:
        search = request.args.get('search', '')
        dept_filter = request.args.get('dept', '')
        min_b = int(request.args.get('min') or 0)
        max_b = int(request.args.get('max') or 999999999)
        
        print(f"\n{'='*70}")
        print(f"🔍 REQUÊTE : search='{search}', dept='{dept_filter}', min={min_b}, max={max_b}")
        
        # Requête BOAMP
        where = '(objet LIKE "%informatique%" OR objet LIKE "%IT%" OR objet LIKE "%cloud%" OR objet LIKE "%numérique%")'
        if search:
            where = f'(objet LIKE "%{search}%")'
        
        print(f"📡 BOAMP query: {where}")
        
        resp = requests.get(BOAMP_API, params={'where': where, 'limit': 100}, timeout=30)
        
        if resp.status_code != 200:
            print(f"❌ HTTP {resp.status_code}")
            return jsonify({'error': True, 'message': f'HTTP {resp.status_code}'}), 500
        
        data = resp.json()
        total = len(data.get('results', []))
        print(f"✅ {total} résultats BOAMP")
        
        # Analyse départements
        depts_count = {}
        for item in data.get('results', []):
            d = item.get('fields', {}).get('departement', '')
            depts_count[d] = depts_count.get(d, 0) + 1
        
        print(f"📊 Depts: {dict(sorted(depts_count.items()))}")
        
        # Traitement
        results = []
        
        for item in data.get('results', []):
            try:
                f = item.get('fields', {})
                titre = f.get('objet', '')
                if not titre:
                    continue
                
                # Budget
                budget = 0
                m = f.get('montant') or f.get('valeurestimee') or ''
                if m:
                    try:
                        budget = int(float(str(m).replace(' ', '').replace(',', '.')))
                    except:
                        pass
                
                if budget < min_b or budget > max_b:
                    continue
                
                # Département
                dept = f.get('departement', '')
                
                # Filtre département
                if dept_filter and dept != dept_filter:
                    continue
                
                dinfo = DEPTS.get(dept, {'region': 'France', 'name': dept or 'N/A'})
                
                results.append({
                    'id': f.get('idweb', 'N/A'),
                    'title': titre,
                    'client': f.get('denominationsociale') or f.get('nomentite') or 'Non spécifié',
                    'budget': budget,
                    'deadline': f.get('datelimitereponse', 'N/A'),
                    'dept': dept,
                    'deptName': dinfo['name'],
                    'region': dinfo['region'],
                    'commune': f.get('commune', ''),
                    'url': f"https://www.boamp.fr/avis/detail/{f.get('idweb', '')}",
                    'source': 'BOAMP',
                    'publishDate': f.get('dateparution', '')
                })
            except Exception as e:
                print(f"⚠️ Item skip: {e}")
        
        print(f"✅ {len(results)} AO retournés")
        if dept_filter and not results:
            print(f"⚠️ AUCUN AO pour dept '{dept_filter}' (disponibles: {list(depts_count.keys())})")
        print(f"{'='*70}\n")
        
        return jsonify({'total': len(results), 'results': results})
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': True, 'message': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
