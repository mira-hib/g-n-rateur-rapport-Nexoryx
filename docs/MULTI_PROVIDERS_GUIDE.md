# Guide Multi-Providers IA

Le système supporte maintenant **4 providers IA** différents : OpenAI, Google Gemini, Anthropic Claude, et Zephyr (via HuggingFace).

## Providers Supportés

### 1. OpenAI (GPT-4, GPT-4 Turbo)
- **Meilleur pour** : Qualité générale, raisonnement complexe
- **Modèles disponibles** :
  - `gpt-4o` (recommandé) - Dernière version optimisée
  - `gpt-4-turbo` - Rapide et performant
  - `gpt-3.5-turbo` - Économique

### 2. Google Gemini
- **Meilleur pour** : Multimodal, longues conversations
- **Modèles disponibles** :
  - `gemini-1.5-pro` (recommandé) - Haute qualité
  - `gemini-1.5-flash` - Rapide et économique
  - `gemini-pro` - Version précédente

### 3. Anthropic Claude
- **Meilleur pour** : Raisonnement approfondi, sécurité
- **Modèles disponibles** :
  - `claude-3-5-sonnet-20241022` (recommandé) - Meilleur équilibre
  - `claude-3-opus-20240229` - Qualité maximale
  - `claude-3-sonnet-20240229` - Économique

### 4. Zephyr (HuggingFace)
- **Meilleur pour** : Open-source, confidentialité
- **Modèles disponibles** :
  - `HuggingFaceH4/zephyr-7b-beta` (recommandé)
  - `HuggingFaceH4/zephyr-7b-alpha`

---

## Configuration

### Étape 1 : Choisir le Provider

Éditez votre fichier `.env` et définissez le provider :

```env
AI_PROVIDER=openai  # ou gemini, claude, zephyr
```

### Étape 2 : Configurer la Clé API

Ajoutez la clé API correspondante au provider choisi :

#### Pour OpenAI :
```env
AI_PROVIDER=openai
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o
```

#### Pour Google Gemini :
```env
AI_PROVIDER=gemini
GEMINI_API_KEY=...
GEMINI_MODEL=gemini-1.5-pro
```

#### Pour Anthropic Claude :
```env
AI_PROVIDER=claude
ANTHROPIC_API_KEY=sk-ant-...
CLAUDE_MODEL=claude-3-5-sonnet-20241022
```

#### Pour Zephyr (HuggingFace) :
```env
AI_PROVIDER=zephyr
HUGGINGFACE_API_KEY=hf_...
ZEPHYR_MODEL=HuggingFaceH4/zephyr-7b-beta
```

### Étape 3 : Paramètres Optionnels

```env
# Température (0.0 = déterministe, 1.0 = créatif)
TEMPERATURE=0.3

# Nombre maximum de tokens
MAX_TOKENS=16000

# Activer l'enrichissement IA
ENABLE_ENRICHMENT=true

# Activer la validation automatique
ENABLE_VALIDATION=true
```

---

## Obtenir les Clés API

### OpenAI
1. Créer un compte sur https://platform.openai.com/
2. Aller dans **API keys**
3. Créer une nouvelle clé
4. Format : `sk-...`

### Google Gemini
1. Aller sur https://makersuite.google.com/app/apikey
2. Créer une clé API
3. Copier la clé

### Anthropic Claude
1. Créer un compte sur https://console.anthropic.com/
2. Aller dans **API keys**
3. Créer une nouvelle clé
4. Format : `sk-ant-...`

### HuggingFace (Zephyr)
1. Créer un compte sur https://huggingface.co/
2. Aller dans **Settings > Access Tokens**
3. Créer un token avec accès "Read"
4. Format : `hf_...`

---

## Comparaison des Providers

| Provider | Qualité | Vitesse | Coût | Open-Source |
|----------|---------|---------|------|-------------|
| **OpenAI GPT-4** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | $$ | ❌ |
| **Gemini Pro** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | $ | ❌ |
| **Claude 3.5** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | $$ | ❌ |
| **Zephyr** | ⭐⭐⭐ | ⭐⭐⭐ | Gratuit | ✅ |

---

## Exemples de Configuration

### Configuration pour Production (GPT-4)

```env
# Provider
AI_PROVIDER=openai
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o

# Paramètres
TEMPERATURE=0.3
MAX_TOKENS=16000
ENABLE_ENRICHMENT=true
ENABLE_VALIDATION=true
MAX_ITERATIONS=3
MIN_VALIDATION_SCORE=75.0
```

### Configuration Économique (Gemini Flash)

```env
# Provider
AI_PROVIDER=gemini
GEMINI_API_KEY=...
GEMINI_MODEL=gemini-1.5-flash

# Paramètres
TEMPERATURE=0.3
MAX_TOKENS=8000
ENABLE_ENRICHMENT=true
ENABLE_VALIDATION=false  # Désactiver pour réduire les coûts
MAX_ITERATIONS=1
```

### Configuration Open-Source (Zephyr)

```env
# Provider
AI_PROVIDER=zephyr
HUGGINGFACE_API_KEY=hf_...
ZEPHYR_MODEL=HuggingFaceH4/zephyr-7b-beta

# Paramètres
TEMPERATURE=0.4
MAX_TOKENS=4000
ENABLE_ENRICHMENT=true
ENABLE_VALIDATION=false  # Zephyr peut être moins fiable pour la validation
MAX_ITERATIONS=1
```

### Configuration Qualité Maximale (Claude Opus)

```env
# Provider
AI_PROVIDER=claude
ANTHROPIC_API_KEY=sk-ant-...
CLAUDE_MODEL=claude-3-opus-20240229

# Paramètres
TEMPERATURE=0.2
MAX_TOKENS=16000
ENABLE_ENRICHMENT=true
ENABLE_VALIDATION=true
MAX_ITERATIONS=3
MIN_VALIDATION_SCORE=80.0
```

---

## Changer de Provider

Pour changer de provider, il suffit de :

1. Modifier `AI_PROVIDER` dans `.env`
2. S'assurer que la clé API correspondante est configurée
3. Redémarrer l'application

**Exemple** : Passer d'OpenAI à Gemini :

```bash
# Avant (.env)
AI_PROVIDER=openai
OPENAI_API_KEY=sk-...

# Après (.env)
AI_PROVIDER=gemini
GEMINI_API_KEY=...
```

---

## Validation de la Configuration

Le système valide automatiquement la configuration au démarrage :

```bash
python main.py --audit-id 1 --format pdf
```

Si la configuration est invalide, vous verrez :

```
[ERREUR] Configuration invalide: Clé API manquante pour le provider 'gemini'
   Provider configuré: gemini
   Modèle: gemini-1.5-pro

   Créez un fichier .env et configurez la clé API appropriée:
   - Pour OpenAI: OPENAI_API_KEY=sk-...
   - Pour Gemini: GEMINI_API_KEY=...
   - Pour Claude: ANTHROPIC_API_KEY=sk-ant-...
   - Pour Zephyr: HUGGINGFACE_API_KEY=hf_...

   Voir .env.example pour un modèle complet
```

---

## Dépannage

### Erreur : "Provider non supporté"

**Cause** : `AI_PROVIDER` contient une valeur invalide

**Solution** : Vérifier que `AI_PROVIDER` est l'un de : `openai`, `gemini`, `claude`, `zephyr`

### Erreur : "Clé API manquante"

**Cause** : La clé API du provider sélectionné n'est pas configurée

**Solution** : Ajouter la clé API appropriée dans `.env`

### Erreur : "Model not found"

**Cause** : Le nom du modèle est incorrect

**Solution** : Vérifier le nom du modèle dans la documentation du provider

### Performance lente avec Zephyr

**Cause** : Les modèles HuggingFace peuvent être plus lents

**Solution** :
- Réduire `MAX_TOKENS`
- Désactiver `ENABLE_VALIDATION`
- Utiliser un modèle plus petit

---

## Recommandations

### Pour la Production
- **Provider** : OpenAI GPT-4 ou Claude 3.5 Sonnet
- **Raison** : Meilleure qualité, fiabilité éprouvée

### Pour les Tests
- **Provider** : Google Gemini Flash
- **Raison** : Rapide et économique

### Pour la Confidentialité
- **Provider** : Zephyr (HuggingFace)
- **Raison** : Open-source, peut être hébergé localement

### Pour la Qualité Maximale
- **Provider** : Claude 3 Opus
- **Raison** : Meilleur raisonnement et analyse approfondie

---

## Support

Pour toute question sur la configuration multi-providers :

1. Consulter `.env.example` pour un exemple complet
2. Vérifier les logs d'erreur détaillés
3. Tester avec un provider différent
4. Contacter l'équipe technique

---

**Version** : 1.0.0
**Date** : 2025-12-03
