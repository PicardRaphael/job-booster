# 📘 Règles de génération – Raphaël Picard

## [RULESET: GLOBAL]

### Moi

[Prénom Nom] = Raphaël Picard
[Email] = raphaelpicard@outlook.fr
[Téléphone] = 06.50.93.15.73
[Adresse] = 60 impasse durnerin
[Code Postal, Ville] = 69430 Marchampt

### Objectif

Ce document définit les règles de rédaction à appliquer pour tous les contenus générés dans le cadre d’une candidature (lettre de motivation, email de motivation, message LinkedIn).

### Ton & style

- Toujours écrire en **français professionnel**.
- Ton **direct, factuel, sans émotion ni emphase**.
- Éliminer les éléments suivants :

- Émojis
- Exclamations
- Formules de politesse molles (“Bien à vous”, “Cordialement”, etc.)

- Formulation **précise, assertive, sans remplissage ni flatterie**.
- Pas d’ornement stylistique.
- Aucune répétition.
- Langage sobre, tourné vers la compétence.

### Contenu obligatoire

- Mentionner **React** ET **IA** (même si le poste n’est orienté que sur l’un des deux).
- Si une compétence manque par rapport à l’annonce → indiquer être **prêt à monter en compétence**.
- Ne jamais inventer de compétence ni d’expérience.
- Chaque texte doit être **personnalisé** avec les variables dynamiques suivantes :

- `{{poste}}` : titre du poste visé
- `{{entreprise}}` : nom de l’entreprise
- `{{prenom}}` : prénom du destinataire
- `{{nom}}` : nom du destinataire
- `{{source}}` : site ou plateforme de l’annonce
- `{{signature}}` : bloc signature professionnel de Raphaël Picard

---

## [RULESET: LETTER]

### Structure

1.  **Objet clair et percutant**
    → Exemple :`📌 Objet : Candidature – Développeur Fullstack React / IA – {{entreprise}}`
2.  **Introduction engageante**

    - Une phrase d’ouverture :
      “Passionné par le développement web et fort de 8 ans d’expérience, je suis très intéressé par l’opportunité de rejoindre {{entreprise}} en tant que {{poste}}.”

3.  **Pourquoi moi ?**
    Format à puces courtes.
    Exemple :

    - Maîtrise de React / Next.js / TypeScript / Node.js.
    - Pratique avancée de l’IA (RAG, LangChain, agents, automatisation).
    - Culture de la qualité (tests, Clean Architecture, CI/CD).
    - Expérience en équipe Agile et mentoring.

4.  **Conclusion dynamique**

    - “Je serais ravi d’échanger avec vous pour discuter plus en détail de ma candidature.”

5.  **Signature**
    Utiliser la variable `{{signature}}`.

### Exigences

- Maximum : 4 paragraphes.
- Longueur totale : 1 page.
- Doit pouvoir être collée directement dans un formulaire ou email.

---

## [RULESET: EMAIL]

### Structure

1.  **Objet clair et percutant**
    `Objet : Candidature – Développeur Fullstack React / IA – {{entreprise}}`
2.  **Corps du message**
    Exemple complet :

    ```
    Bonjour {{prenom}},

    Suite à votre offre pour le poste de {{poste}}, je vous propose ma candidature. Développeur fullstack avec 8 ans d’expérience sur React, Node.js et l’intégration de l’IA (RAG, LangChain, agents, automatisation), je conçois des applications web sur-mesure et performantes.

    Votre environnement technique correspond pleinement à mes expertises et à ma volonté de contribuer à des projets innovants autour de l’IA.

    Je reste disponible pour un échange à votre convenance.

    {{signature}}
    ```

3.  **Contraintes**

    - Longueur : 6 à 8 lignes maximum.
    - Doit être lisible sans pièce jointe.
    - Aucune phrase superflue ou de politesse générique.

---

## [RULESET: LINKEDIN]

### Structure

- Message court, direct, contextuel.
- Objectif : initier un contact ou postuler à une offre.

#### Cas 1 — Recruteur / RH

```
Bonjour {{prenom}},
Je vous contacte concernant le poste de {{poste}} chez {{entreprise}}.
Développeur fullstack (React / Node.js) avec une forte appétence pour l’IA, je vous joins mon CV et reste disponible pour un échange rapide.
Dans l’attente de votre réponse, à très vite.
```

#### Cas 2 — CTO / profil technique

```
Bonjour {{prenom}},
Je vous contacte au sujet du poste de {{poste}}.
Je travaille sur des architectures React / Node.js et j’intègre l’IA dans mes projets (agents, RAG, automatisation).
Disponible pour échanger plus en détail sur vos besoins techniques.
```

#### Cas 3 — Réseau / Connexion non-recrutement

```
Bonjour {{prenom}},
Développeur fullstack spécialisé dans l’intégration de l’IA dans les applications web, je suis toujours curieux d’échanger autour des projets tech et innovation.
Toujours partant pour connecter entre passionnés de tech & IA.
```

---

## [RULESET: SIGNATURE]

```
Raphaël Picard
Développeur Fullstack – React / Node.js / IA
📧 raphaelpicard@outlook.fr | 📞 06.50.93.15.73
💼 https://www.raphaelpicard.com/
🔗 https://www.linkedin.com/in/raphael-picard/
👨‍💻 https://github.com/PicardRaphael
```

---

## [RULESET: CHECKLIST]

Avant validation d’un texte :

- ✅ Mentionne React et IA.
- ✅ Aucun émoji.
- ✅ Pas de superlatifs inutiles.
- ✅ Une seule idée par phrase.
- ✅ Ton professionnel et concis.
- ✅ Respect de la structure du ruleset correspondant.
