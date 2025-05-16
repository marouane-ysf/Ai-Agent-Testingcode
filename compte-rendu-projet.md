# Compte Rendu de Projet : Système Multi-Agents pour la Gestion Contractuelle avec Azure AI

## Introduction

Ce document présente un compte rendu détaillé du projet AirbusAgenticCM_BYOUC, développé dans le cadre de l'incubation Agentic AI. Ce projet vise à améliorer la gestion contractuelle à travers une plateforme intelligente et interactive, propulsée par un système d'agents IA orchestrés. Le projet a été conçu à l'aide des services Azure AI, de la bibliothèque Semantic Kernel, et d'une interface utilisateur développée en Streamlit.

Il s'inscrit dans un contexte d'innovation autour de la rédaction, la comparaison, l'analyse de qualité, la négociation, et le routage intelligent des contrats, dans une logique multi-agent spécialisée.

<!-- INSÉRER IMAGE 1: Vue d'ensemble de l'application -->
![Figure 1: Interface utilisateur principale développée avec Streamlit](inserer_image1.png)

## Objectifs du Projet

- **Automatiser les processus contractuels** : de la rédaction à la négociation
- **Offrir une orchestration intelligente** des agents IA spécialisés
- **Fournir une interface intuitive** et accessible aux utilisateurs non techniques
- **Réduire le temps de traitement** et les erreurs humaines dans les contrats
- **Favoriser la standardisation** et la qualité contractuelle

## Technologies Utilisées

- **Azure AI Services** : pour l'exécution et l'hébergement des agents IA (GPT-4o)
- **Semantic Kernel** : pour la coordination, la mémoire et le routage des agents
- **Streamlit** : pour le développement de l'interface utilisateur Web
- **Python** : langage principal de développement
- **PyMuPDF** : pour la gestion avancée des PDF
- **OCR (Tesseract)** : pour extraire le texte des documents scannés

<!-- INSÉRER IMAGE 2: Architecture technique -->
![Figure 2: Architecture technique du système](inserer_image2.png)

## Architecture Technique

L'analyse du code source révèle une architecture modulaire qui s'appuie sur:

- **Azure AI Project Client** pour la communication avec les agents Azure AI
- **DefaultAzureCredential** pour l'authentification sécurisée
- **Gestion asynchrone** des requêtes aux agents via asyncio
- **Architecture thread-based** pour garantir la persistance des conversations
- **Système de mémoire contextuelle** pour maintenir la cohérence des échanges

### Configuration du Projet

Le projet utilise plusieurs configurations clés:
- Connection string Azure AI: `francecentral.api.azureml.ms;3c6f1086-c5db-419a-b2e5-ba0f8a344217;test;contractassistant`
- Modèle déployé: `gpt-4o`
- Base de données PostgreSQL hébergée sur Azure

## Présentation de l'Interface Utilisateur

L'application Web a été développée sous Streamlit. Elle permet à l'utilisateur de sélectionner le mode d'interaction souhaité:

- **Orchestration Intelligente** - Routage automatique vers les agents appropriés
- **Mode Séquentiel Multi-Agent** - Définition manuelle de l'ordre d'exécution des agents
- **Mode Agent Unique** - Interaction directe avec un agent spécifique
- **Mode Debug** - Visualisation détaillée des échanges entre agents
- **Mode Contextuel** - Activation/désactivation de la mémoire de conversation

<!-- INSÉRER IMAGE 3: Interface de sélection des modes -->
![Figure 3: Sélection des modes d'interaction](inserer_image3.png)

L'interface comprend également:
- Sélection de fichiers avec support OCR pour documents scannés
- Visualisation des réponses détaillées par agent
- Export des documents générés en PDF, DOCX et TXT
- Système de chat avec historique de conversation

## Agents Développés

Chaque agent possède une spécialisation et est identifié par un ID unique dans Azure AI:

### Router Agent (🧭)
- **ID**: `asst_FIys1BSmTCrwb89yPJjm3nJT`
- **Fonction**: Orchestration intelligente et routage dynamique
- **Analyse des intentions utilisateur** pour sélectionner les agents appropriés
- Le code implémente une méthode de fallback par heuristique en cas d'échec du routeur

### Drafter Agent (📝)
- **ID**: `asst_DtIhmMy60VKN54VtDLZ6ZXH2`
- **Fonction**: Rédaction des contrats selon les besoins exprimés
- **Personnalisation des templates**
- Support pour l'export en multiples formats

### Quality Agent (🔍)
- **ID**: `asst_yH6mO6GgScy8bp8Yk7W4KAVB`
- **Fonction**: Vérification de la qualité, des risques et des écarts contractuels
- **Détection d'anomalies** dans les clauses
- Analyse préliminaire systématique pour enrichir le contexte des autres agents

### Compare Agent (⚖️)
- **ID**: `asst_yIJSEoeNKVNd2sp8veCtOds1`
- **Fonction**: Comparaison technique des contrats
- **Mise en forme tabulaire des différences**
- Analyse différentielle des clauses et conditions

### Market Comparison Agent (📊)
- **ID**: `asst_wWiLQYkWIwVQm7MT7glmXau9`
- **Fonction**: Analyse comparative par rapport aux standards du marché
- **Génération d'indicateurs concurrentiels**
- Benchmark automatique des clauses

### Negotiation Agent (🤝)
- **ID**: `asst_cObIfs9XofRuqJ1RUBF46dW7`
- **Fonction**: Analyse des clauses négociables
- **Propositions de compromis et alternatives**
- Coaching de négociation contextualisé

<!-- INSÉRER IMAGE 4: Schéma des agents et leurs spécialisations -->
![Figure 4: Architecture des agents avec Azure AI et Semantic Kernel](inserer_image4.png)

## Modes de Fonctionnement

### 1. Orchestration Intelligente

Ce mode repose sur le Router Agent, qui choisit automatiquement les agents pertinents en fonction de l'intention de l'utilisateur.

L'implémentation technique comprend:
- Analyse de requête via le Router Agent
- Sélection heuristique en cas d'échec du routeur (détection de mots-clés)
- Parallélisation des appels aux agents sélectionnés
- Fusion intelligente des réponses

```python
# Extrait du code d'orchestration:
async def determine_appropriate_agents(client, query):
    # Utilisation primaire du Router Agent
    router_thread = await client.agents.create_thread()
    router_thread_id = router_thread.id
    
    # Si le router échoue, utilisation d'heuristiques
    heuristic_agents, heuristic_reason = heuristic_agent_selection(query)
    
    # Exécution et analyse de la réponse
    # ...
```

<!-- INSÉRER IMAGE 5: Schéma du mode Orchestration Intelligente -->
![Figure 5: Schéma d'architecture du mode Orchestration Intelligente](inserer_image5.png)

### 2. Mode Séquentiel

Dans ce mode, l'utilisateur choisit l'ordre des agents. L'implémentation technique comprend:
- Définition manuelle de la séquence d'agents via l'interface
- Conservation du contexte entre les agents
- Passage enrichi des informations d'un agent à l'autre

```python
# Extrait du code pour le mode séquentiel:
async def run_sequential_pipeline(query):
    # ...
    for i, agent_key in enumerate(sequence):
        response = await execute_agent(
            client,
            AGENT_IDS[agent_key],
            agent_info,
            current_input
        )
        responses[agent_key] = response
        current_input = f"Tenant compte de la réponse précédente: {response}\n\nQuestion initiale: {query}"
    # ...
```

<!-- INSÉRER IMAGE 6: Schéma du mode Séquentiel -->
![Figure 6: Schéma d'architecture du mode Séquentiel](inserer_image6.png)

### 3. Mode Agent Unique

Permet d'accéder directement à un agent donné. L'implémentation inclut:
- Sélection directe via boutons dans l'interface
- Support complet du mode contextuel
- Accès aux fonctionnalités avancées de chaque agent

### 4. Mode Debug

Affiche toutes les étapes, les messages envoyés aux agents, les réponses reçues et les erreurs éventuelles. Implémenté avec:
- Affichage des threads actifs et leurs identifiants
- Visualisation des réponses brutes du routeur
- Indication de la méthode de sélection (routeur ou heuristique)

<!-- INSÉRER IMAGE 7: Capture d'écran du Mode Debug -->
![Figure 7: Capture d'écran du Mode Debug avec contexte activé](inserer_image7.png)

### 5. Mode Contexte (Mémoire Active)

Active une mémoire de conversation permettant aux agents de rappeler les interactions précédentes:
- Persistence des identifiants de threads par agent
- Construction automatique d'un contexte enrichi
- Transmission de l'historique synthétisé aux agents

```python
# Extrait du code pour le mode contextuel:
if st.session_state.get("context_mode", True) and "messages" in st.session_state:
    context_messages = st.session_state.messages[-3:]
    history = "\n\nHistorique de conversation:\n"
    for msg in context_messages:
        if msg["role"] == "user":
            history += f"Question: {msg['content']}\n"
        else:
            resp = msg["content"]
            if len(resp) > 200:
                resp = resp[:200] + "..."
            history += f"Réponse précédente: {resp}\n"
```

## Fonctionnalités Avancées

### Traitement de Documents

Le système intègre des capacités avancées de traitement documentaire:
- **OCR intégré** pour les documents scannés (via PyMuPDF)
- **Analyse multi-documents** pour comparaison simultanée
- **Export multi-format** (PDF, DOCX, TXT) avec mise en forme préservée

```python
# Extrait du code pour la génération de PDF:
def generate_pdf_with_fitz(title, content):
    doc = fitz.open()
    page = doc.new_page()
    # Configuration de formatage avancée
    # ...
    # Gestion Unicode complète
    # ...
```

<!-- INSÉRER IMAGE 8: Capture d'écran de l'interface de traitement de documents -->
![Figure 8: Interface de traitement de documents avec OCR](inserer_image8.png)

### Sélection Heuristique d'Agents

Une fonctionnalité clé de robustesse est le système de fallback heuristique:
- Détection de mots-clés par domaine d'expertise
- Analyse des patterns linguistiques par expressions régulières
- Logique de décision pondérée pour les cas ambigus

```python
def heuristic_agent_selection(query):
    keywords = {
        "quality": ['analys', 'évalue', 'qualité', 'risque', ...],
        "drafter": ['rédige', 'rédaction', 'écri', 'ébauche', ...],
        # ...
    }
    patterns = {
        "drafter": r'(rédige[rz]?|écri[rstvez]+|prépar[ez]+)\s+([uneod]+\s+)?(ébauche|contrat|document|proposition)',
        # ...
    }
```

## Exemples de Résultats

<!-- INSÉRER IMAGE 9: Exemple de contrat généré -->
![Figure 9: Exemple de contrat généré par le système](inserer_image9.png)

<!-- INSÉRER IMAGE 10: Exemple de comparaison de contrats -->
![Figure 10: Exemple de comparaison de contrats (output tabulaire)](inserer_image10.png)

## Problèmes à Résoudre

L'analyse du code révèle certains défis techniques:

1. **Orchestration Intelligente**
   - Fonctionne partiellement, avec un fallback heuristique nécessaire
   - Nécessite une meilleure détection d'intention pour les cas complexes

2. **Mode Séquentiel**
   - Fonctionne bien, mais ne permet pas la réutilisation du même agent plusieurs fois
   - Liaison contextuelle parfois inconsistante entre agents

3. **Gestion des Ressources**
   - Création excessive de threads dans certains scénarios
   - Manque d'optimisation pour les requêtes répétitives

4. **Traitement de Documents Complexes**
   - OCR parfois fragile sur certains formats
   - Besoin d'amélioration pour les structures tabulaires

## Perspectives

### Améliorations Techniques

L'analyse du code suggère plusieurs axes d'amélioration:

1. **Optimisation de l'Orchestration**
   - Amélioration du routeur avec un système d'apprentissage continu
   - Cache intelligent pour les patterns de requêtes fréquents

2. **Enrichissement du Mode Séquentiel**
   - Support de réutilisation d'agents dans la séquence
   - Boucles conditionnelles entre agents

3. **Infrastructure**
   - Persistance améliorée des sessions
   - Intégration complète avec Azure AI Studio
   - Optimisation de la base de données PostgreSQL

4. **Fonctionnalités Utilisateur**
   - Workflow hybride humain-IA
   - Support multilingue complet
   - Tableaux de bord analytiques
   - Intégration avec SharePoint, SAP et autres GED

<!-- INSÉRER IMAGE 11: Architecture future proposée -->
![Figure 11: Architecture future proposée pour l'évolution du système](inserer_image11.png)

## Cas d'Usage

Les cas d'usage identifiés sont:

1. **Rédaction Contractuelle**
   - Génération assistée de contrats sur mesure
   - Adaptation de templates existants à de nouveaux besoins

2. **Analyse de Risques**
   - Détection automatique de clauses problématiques
   - Évaluation comparative des risques contractuels

3. **Comparaison Multi-Documents**
   - Analyse différentielle de contrats fournisseurs
   - Identification de standards et d'écarts

4. **Assistance à la Négociation**
   - Simulation de scénarios de négociation
   - Conseil tactique sur les marges de manœuvre

## Équipe Projet

- Etienne TRONC – Lead Engineer
- Marouane YOUSSOUFI – 
- Fernando Delfin ALBARRAN RAMIREZ – Engineer
- Marie LINIERES – Engineer
- Kelly ESQUERRE – Engineer
- Akhli Riouffreyt – Ingénieur Mécanique

## Conclusion

L'analyse approfondie du code source confirme que le système multi-agents développé représente une avancée significative dans le domaine de la gestion contractuelle. L'architecture technique est robuste, avec une excellente séparation des responsabilités et un design modulaire permettant une évolution future.

Les points forts identifiés sont:
- Architecture multi-agents hautement spécialisée
- Interface utilisateur intuitive et responsive
- Traitement documentaire avancé avec OCR
- Système de fallback heuristique pour garantir la robustesse

Les axes d'amélioration principaux concernent l'optimisation de l'orchestration intelligente et l'enrichissement du mode séquentiel pour des cas d'usage plus complexes. L'intégration avec des systèmes tiers (GED, workflow hybride) constitue également une évolution naturelle prometteuse.

Le projet est bien positionné pour des cas d'usage industriels réels à grande échelle, avec une architecture technique permettant une montée en charge progressive.