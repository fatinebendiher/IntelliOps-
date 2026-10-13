def choisir_canal(criticite: str) -> str:
    canaux = {"CRITICAL": "TEAMS", "HIGH": "TEAMS",
              "MEDIUM": "EMAIL", "LOW": "DASHBOARD"}
    if criticite not in canaux:
        raise ValueError(f"Criticité inconnue : {criticite}")
    return canaux[criticite]
    def rediger(evt: Evenement, analyse: Analyse) -> str:
    lignes = [
        f"[{analyse.criticite}] Service : {evt.component}",
        f"Incident : {evt.message}",
        f"Cause probable : {analyse.cause_probable}",
        f"Action : {analyse.action_recommandee}",
        f"Sources : {', '.join(analyse.sources)}",
    ]
    return "\n".join(lignes)