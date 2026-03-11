# 🚀 Déploiement AOFinder sur Railway

## 📦 Fichiers nécessaires

Tu as maintenant 5 fichiers :

```
📁 Ton projet/
  ├── app.py              ← Backend Flask
  ├── index.html          ← Frontend
  ├── requirements.txt    ← Dépendances Python
  ├── Procfile            ← Configuration Railway
  └── runtime.txt         ← Version Python
```

---

## 🚂 Déploiement Railway (5 minutes)

### Étape 1 : Créer un repo GitHub

1. Va sur https://github.com
2. Clique sur **"New repository"**
3. Nom : `aofinder`
4. ✅ Public
5. **Create repository**

### Étape 2 : Upload les fichiers

#### Option A : Via GitHub Web

1. Clique sur **"uploading an existing file"**
2. Glisse les 5 fichiers
3. Commit

#### Option B : Via Git (si installé)

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/TON_USERNAME/aofinder.git
git push -u origin main
```

### Étape 3 : Déployer sur Railway

1. Va sur https://railway.app
2. Clique **"New Project"**
3. Choisis **"Deploy from GitHub repo"**
4. Sélectionne `aofinder`
5. Railway détecte automatiquement Python !

✅ **C'est tout !** Railway :
- Installe les dépendances
- Lance le serveur
- Te donne une URL : `https://aofinder-production.up.railway.app`

---

## 🌐 Résultat

Railway te donne une URL comme :
```
https://aofinder-production-xxxx.up.railway.app
```

Cette URL :
- ✅ Fonctionne partout
- ✅ Pas de CORS
- ✅ 100 AO BOAMP réels
- ✅ Gratuit (500h/mois)

---

## 🎯 Test

Ouvre l'URL Railway → Tu vois AOFinder avec les AO !

---

## 🔧 Mise à jour

Pour changer le code :

1. Modifie les fichiers sur GitHub
2. Railway redéploie automatiquement

---

## 💰 Coût

- **Gratuit** : 500h/mois (largement suffisant)
- Si tu dépasses : 5$/mois

---

## ✅ Checklist

- [ ] 5 fichiers uploadés sur GitHub
- [ ] Repo lié à Railway
- [ ] Déployé avec succès
- [ ] URL fonctionne
- [ ] Les AO s'affichent

---

**C'est beaucoup plus simple que GitHub Pages + proxy séparé !** 🎉
