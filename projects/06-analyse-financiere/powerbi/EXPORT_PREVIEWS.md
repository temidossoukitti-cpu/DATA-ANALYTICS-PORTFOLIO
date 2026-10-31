# Procédure d’export des aperçus

**État actuel :** les exports ne sont pas générés. Le dashboard doit d’abord être construit dans Power BI Desktop par Samuel; aucun PBIX/PBIP, PDF ou PNG de dashboard n’est revendiqué dans ce dépôt. Le dossier `preview/` reste vide à l’exception de son fichier de suivi.

Après construction et validation manuelle du rapport :

1. Noter le nom exact et la version de Power BI Desktop utilisée ainsi que la date d’export dans ce fichier.
2. Actualiser les sept requêtes en configurant le paramètre `DataFolder`, vérifier les relations et les filtres, puis enregistrer le fichier de travail de Samuel hors de ce dépôt ou selon son choix.
3. Dans Desktop, utiliser **Fichier → Exporter → PDF** et relire les quatre pages exportées avant de les partager. Nom prévu : `preview/06-analyse-financiere-dashboard.pdf`.
4. À partir du PDF relu, produire une image PNG par page à l’aide de Poppler (`pdftoppm`, largeur/résolution lisible), puis vérifier les quatre fichiers. Nommage : `preview/06-analyse-financiere-page-01-synthese.png`, `preview/06-analyse-financiere-page-02-rentabilite.png`, `preview/06-analyse-financiere-page-03-liquidite.png` et `preview/06-analyse-financiere-page-04-tresorerie.png`.
5. Ajouter ici la version exacte de Desktop, la date, le nom du PDF et la résolution de conversion des PNG; ne pas cocher la checklist avant vérification visuelle.

**Power BI Desktop :** non utilisé pour cette livraison; version à renseigner par Samuel lors du premier export.
