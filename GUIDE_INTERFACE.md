# Guide d'Utilisation - Interface Simplifiée

## 🚀 Lancement Rapide

### Windows
Double-cliquez sur `run_app.bat` ou exécutez dans un terminal:
```bash
streamlit run app.py
```

### Linux/Mac
```bash
streamlit run app.py
```

L'interface s'ouvrira automatiquement dans votre navigateur à l'adresse: `http://localhost:8501`

---

## 📋 Utilisation en 3 Étapes Simples

### ✅ Étape 1: Sélectionner un Audit

1. **Liste déroulante des audits disponibles**
   - Tous les audits de `db/audit_system.db` sont affichés
   - Format: `#ID - Client (Type) - Date`
   - Exemple: `#1 - Nexoryx Bank (Pentest Réseau) - 2024-01-15`

2. **Choisissez un audit**
   - L'audit se charge automatiquement
   - Message de confirmation: `✅ Audit chargé: [Client] - [X] vulnérabilités`

### ✏️ Étape 2: Modifier les Informations (Optionnel)

Tous les champs de la base de données sont pré-remplis et modifiables:

**Informations principales:**
- Nom du client
- Type d'audit
- Auditeur
- Date de l'audit
- Périmètre

**Vulnérabilités:**
- Affichage automatique de toutes les vulnérabilités
- Statistiques par sévérité: 🔴 Critiques, 🟠 Élevées, 🟡 Moyennes, 🟢 Faibles
- Détails consultables dans l'expander

### 📥 Étape 3: Générer le Rapport

**3 options de génération:**

1. **📄 Générer PDF** - Format professionnel pour présentation
2. **�� Générer DOCX** - Format éditable pour modifications
3. **📚 Générer PDF + DOCX** - Les deux formats

**Le rapport généré contient:**
- Page de garde
- Résumé exécutif
- Contexte et périmètre
- Méthodologie
- Analyse globale (score de sécurité, matrices)
- Vulnérabilités détaillées (enrichies par l'IA)
- Plan d'action priorisé
- Conclusion

---

## 📊 Fonctionnalités

### 1️⃣ Configuration (Barre latérale)

**Provider IA**
- Sélectionnez le provider d'IA: OpenAI, Gemini, Claude ou Zephyr
- Choisissez le modèle approprié
- Configurez la température (0.0 = déterministe, 1.0 = créatif)
- Définissez le nombre max de tokens

**Fonctionnalités**
- ✅ **Enrichissement IA**: Active l'enrichissement automatique des sections
- ✅ **Validation automatique**: Active la validation du contenu généré

### 2️⃣ Page de Garde

Remplissez les informations de base:
- **Titre du rapport**: Titre principal
- **Nom du client**: Organisation auditée (obligatoire)
- **Type d'audit**: Nature de l'audit
- **Date de l'audit**: Date de réalisation
- **Auditeur**: Nom de l'auditeur principal
- **Version**: Numéro de version du rapport

### 3️⃣ Contexte et Périmètre

- **Description de l'environnement**: Infrastructure et contexte
- **Périmètre technique**: Systèmes et technologies auditées
- **Périmètre temporel**: Période de l'audit

### 4️⃣ Méthodologie

- **Type d'audit**: Approche méthodologique
- **Standards**: Sélectionnez les référentiels (OWASP, NIST, ISO 27001, etc.)
- **Outils**: Listez les outils utilisés (séparés par des virgules)
- **Phases**: Décrivez les phases (une par ligne)
- **Approche**: Description détaillée de la méthodologie

### 5️⃣ Vulnérabilités Détectées

**Ajouter une vulnérabilité:**
1. Cliquez sur "➕ Ajouter une vulnérabilité"
2. Remplissez les champs:
   - **Titre**: Nom de la vulnérabilité
   - **Catégorie**: Network, AppSec, IAM, Cloud, Governance, Forensic
   - **Sévérité**: CRITICAL, HIGH, MEDIUM, LOW
   - **Probabilité**: Probabilité d'exploitation
   - **Impact**: Impact de la vulnérabilité
   - **Priorité**: P0 (immédiat), P1 (court terme), P2 (moyen terme), P3 (long terme)
   - **Description technique**: Détails techniques
   - **Impact métier**: Conséquences business
   - **Preuves**: Éléments de preuve
   - **Recommandations**: Mesures correctives
3. Cliquez sur "➕ Ajouter cette vulnérabilité"

**Gérer les vulnérabilités:**
- Visualisez la liste des vulnérabilités ajoutées
- Supprimez une vulnérabilité avec le bouton 🗑️

### 6️⃣ Plan d'Action Priorisé

**Ajouter une action:**
1. Cliquez sur "➕ Ajouter une action"
2. Remplissez:
   - **Mesure**: Description de l'action à implémenter
   - **Priorité**: P0, P1, P2, P3
   - **Responsable**: Équipe ou personne responsable
   - **Échéance**: Délai (ex: J+30, J+90)
   - **Bénéfice**: Bénéfices attendus de cette action
3. Cliquez sur "➕ Ajouter cette action"

### 7️⃣ Conclusion

- **Résumé**: Synthèse globale de l'audit
- **Points positifs**: Éléments positifs identifiés (un par ligne)
- **Axes d'amélioration**: Points à améliorer (un par ligne)
- **Recommandations stratégiques**: Recommandations de haut niveau (une par ligne)
- **Prochaines étapes**: Actions à mener

### 8️⃣ Génération du Rapport

1. Vérifiez que tous les champs obligatoires sont remplis:
   - ✅ Nom du client
   - ✅ Au moins une vulnérabilité
2. Cliquez sur "🚀 Générer le Rapport"
3. Téléchargez les fichiers:
   - **📥 PDF**: Format imprimable
   - **📥 DOCX**: Format éditable

---

## 💡 Conseils d'Utilisation

### Priorités d'Actions
- **P0 (Immédiat)**: < 1 semaine - Vulnérabilités critiques
- **P1 (Court terme)**: < 1 mois - Vulnérabilités importantes
- **P2 (Moyen terme)**: 1-3 mois - Améliorations significatives
- **P3 (Long terme)**: > 3 mois - Optimisations et renforcements

### Sévérité des Vulnérabilités
- **CRITICAL**: Exploitation immédiate possible, impact majeur
- **HIGH**: Exploitation probable, impact significatif
- **MEDIUM**: Exploitation possible, impact modéré
- **LOW**: Exploitation difficile, impact mineur

### Catégories
- **Network**: Sécurité réseau et infrastructure
- **AppSec**: Sécurité applicative
- **IAM**: Gestion des identités et accès
- **Cloud**: Sécurité cloud
- **Governance**: Gouvernance et conformité
- **Forensic**: Investigation et analyse forensique

---

## 🔧 Dépannage

### L'interface ne se lance pas
1. Vérifiez que Streamlit est installé: `pip install streamlit`
2. Vérifiez les dépendances: `pip install -r requirements.txt`
3. Vérifiez que vous êtes dans le bon répertoire

### Erreur lors de la génération
1. Vérifiez que tous les champs obligatoires sont remplis
2. Vérifiez que le répertoire `generated_reports` existe
3. Consultez les logs d'erreur affichés

### Le PDF/DOCX ne s'affiche pas correctement
1. Vérifiez que les polices sont disponibles
2. Essayez de télécharger à nouveau le fichier
3. Ouvrez avec Adobe Reader (PDF) ou Microsoft Word (DOCX)

---

## 📞 Support

Pour toute question ou problème:
1. Consultez la documentation dans `README.md`
2. Vérifiez les logs dans `app.log`
3. Contactez le support technique

---

## 🎨 Personnalisation

L'interface peut être personnalisée en modifiant:
- **Couleurs**: Section CSS dans `app.py`
- **Logo**: Ajoutez votre logo dans le répertoire `assets/`
- **Styles PDF**: Modifiez `report/pdf_generator.py`

---

© 2024 Nexoryx - Générateur de Rapports d'Audit
