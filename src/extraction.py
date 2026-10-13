
import re
from datetime import datetime

from src.contrat import Evenement, SEVERITES



def masquer_secrets(texte: str) -> str:
    """
    Masque les valeurs des champs sensibles :
    password, passwd, token, secret et api_key.
    """
    pattern = (
        r"\b(password|passwd|token|secret|api_key)(\s*[=:]\s*)"
        r"('[^']*'|\"[^\"]*\"|[^\s,;]+)"
    )

    return re.sub(
        pattern,
        lambda match: match.group(1) + match.group(2) + "[SECRET]",
        texte,
        flags=re.IGNORECASE,
    )


def normaliser_docker(
    ligne: str,
    numero: int,
    environment: str = "production",
) -> Evenement:
    """
    Convertit une ligne de log Docker en Evenement.
    Format :
    AAAA-MM-JJ HH:MM:SS NIVEAU composant message...
    """
    champs = ligne.split(maxsplit=4)

    if len(champs) < 5:
        raise ValueError("La ligne Docker doit contenir au moins 5 champs.")

    date_str, heure, niveau, component, message = champs

    try:
        dt = datetime.strptime(
            f"{date_str} {heure}",
            "%Y-%m-%d %H:%M:%S",
        )
    except ValueError as exc:
        raise ValueError("Date ou heure Docker invalide.") from exc

    timestamp = dt.strftime("%Y-%m-%dT%H:%M:%SZ")

    niveau = niveau.upper()
    if niveau == "ERROR":
        severity = "HIGH"
    elif niveau == "WARN":
        severity = "MEDIUM"
    elif niveau == "INFO":
        severity = "LOW"
    else:
        severity = "LOW"

    event_type = (
        "CONTAINER_RESTART"
        if "restarts=" in message
        else "LOG"
    )

    return Evenement(
        id=f"EVT-{numero:05d}",
        timestamp=timestamp,
        source="DOCKER",
        component=component,
        environment=environment,
        event_type=event_type,
        severity=severity,
        message=masquer_secrets(message),
    )


def normaliser_trivy(
    rapport: dict,
    numero: int,
    environment: str = "production",
) -> Evenement:
    """Convertit un rapport Trivy en Evenement."""
    cles = [
        "Target",
        "VulnerabilityID",
        "PkgName",
        "InstalledVersion",
        "Severity",
        "Timestamp",
    ]

    for cle in cles:
        if cle not in rapport:
            raise ValueError(f"Clé manquante dans le rapport : {cle}")

    severity = str(rapport["Severity"]).upper()
    if severity not in SEVERITES:
        severity = "LOW"

    return Evenement(
        id=f"EVT-{numero:05d}",
        timestamp=rapport["Timestamp"],
        source="TRIVY",
        component=rapport["Target"],
        environment=environment,
        event_type="VULNERABILITY",
        severity=severity,
        message=(
            f"Vulnérabilité {rapport['VulnerabilityID']} détectée "
            f"dans {rapport['PkgName']} {rapport['InstalledVersion']}."
        ),
    )

