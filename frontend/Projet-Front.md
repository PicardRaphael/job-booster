# AGENT-FRONTEND.md — Next.js 15 + TypeScript + Tailwind + shadcn/ui (Version FR)

## 🎯 Objectif

UI pour assister la candidature.

- Input : offre d’emploi (textarea ou upload `.md`).
- Checkbox : choix **unique** entre Email, LinkedIn ou Lettre (pas les 3).
- Envoi de l’offre + choix vers l’API backend.
- Résultat affiché selon sélection.

---

## ⚙️ Stack

- **Framework** : Next.js 15 (App Router, TypeScript strict).
- **UI** : TailwindCSS + shadcn/ui.
- **Data** : TanStack Query (React Query) pour fetch/cache.
- **Validation** : Zod.
- **Déploiement** : Vercel.

---

## 📂 Arborescence

```
frontend/app/
  (features)/
    offer/
      components/
        OfferTextarea.tsx
        OfferUploader.tsx
        OutputSelector.tsx
        AnalyzeButton.tsx
      hooks/
        useGenerate.ts
      types/
        offer.ts
      page.tsx              # page principale input offre
    result/
      components/
        ResultCard.tsx
        SourceList.tsx
      page.tsx              # affichage du résultat
  lib/
    api.ts                  # wrapper fetch backend
    queryClient.ts
    ui/
      Section.tsx
      PageTitle.tsx
  styles/
    globals.css
```

---

## 🧩 Composants

- **OfferTextarea** : zone pour coller l’offre en texte brut.
- **OfferUploader** : uploader fichier `.md` (analyse côté backend, pas PDF).
- **OutputSelector** : radio/checkbox unique (Email / LinkedIn / Lettre).
- **AnalyzeButton** : déclenche génération.
- **ResultCard** : affiche le texte généré.
- **SourceList** : passages Qdrant utilisés.

---

## 🔄 Flux UI

1. L’utilisateur colle son offre ou upload un `.md`.
2. Il choisit **un seul output** (radio group : Email OU LinkedIn OU Lettre).
3. Clic sur **Analyser** → POST `/generate` avec :

   ```json
   {
     "offer_analysis": {...},
     "output": "email"
   }
   ```

4. API renvoie `GenerateResponse` → affichage `ResultCard`.

---

## ⚙️ Hooks

```ts
// hooks/useGenerate.ts
export const useGenerate = () => {
  return useMutation(async (body: GenerateRequest) => {
    const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    if (!res.ok) throw new Error('Erreur API');
    return res.json() as Promise<GenerateResponse>;
  });
};
```

---

## ✅ UX

- Utilisation de shadcn/ui : `Card`, `Button`, `Textarea`, `RadioGroup`.
- Tailwind pour responsive, lisible.
- Indiquer "⚠️ Un seul choix possible" dans `OutputSelector`.
- Affichage clair du résultat (texte brut copiable, sans emoji si contexte `informations.md`).

---

## 📊 Sécurité & Qualité

- Pas de clés exposées (env côté backend).
- Validation côté client avec Zod.
- Composants testés avec testing-library/react.
- CI/CD Vercel + ESLint + Prettier.
