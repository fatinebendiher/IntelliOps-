from src.contrat import Analyse, Evenement, Notification

CANAUX = {
    "CRITICAL": "TEAMS",
    "HIGH": "TEAMS",
    "MEDIUM": "EMAIL",
    "LOW": "DASHBOARD",
}

REPONSES_OUI = ("o", "oui", "y", "yes")


def choisir_canal(criticite: str) -> str:
    if criticite not in CANAUX:
        raise ValueError(f"Criticité inconnue : {criticite}")
    return CANAUX[criticite]


def rediger(evt: Evenement, analyse: Analyse) -> str:
    lignes = [
        f"[{analyse.criticite}] Service : {evt.component}",
        f"Incident : {evt.message}",
        f"Cause probable : {analyse.cause_probable}",
        f"Action : {analyse.action_recommandee}",
        f"Sources : {', '.join(analyse.sources)}",
    ]
    return "\n".join(lignes)


def notifier(evt: Evenement, analyse: Analyse, journal: list) -> Notification:
    notif = Notification(
        event_id=evt.id,
        canal=choisir_canal(analyse.criticite),
        destinataire="equipe-ops",
        message=rediger(evt, analyse),
    )
    journal.append(notif)
    evt.status = "NOTIFIED"
    return notif


def demander_validation(analyse: Analyse, reponse: str) -> bool:
    if not analyse.sensible:
        return True
    return reponse.strip().lower() in REPONSES_OUI