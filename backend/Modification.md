1. Quand on a un job offer, logiquement c'est l'agent analyser qui va faire un sorte résumé du job offer et ensuite transmettre aux agents. Avec ce résumé on recupère le rag context en bdd. Et ces informations clés sont reranked par le service de reranking. Ensuite on passe tout à l'agent.
2. Pour les config llm en gros on peux donnée top_pn top_k et temperature... mais aussi d'autres paramètres mais rien est obligatoire.
3. job_application_crew.py peux pas etre plus lissible plusieur fichier même d'autre dossier.
4. config.py récupère les variables d'environnement ?
5. schemas.py peut être divisé en plusieurs fichiers.

IMPORTANT: Je préfère plein de petit fichiers plutôt que de gros fichiers.
