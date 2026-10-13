
import unittest

from src.analyse import analyser, classer, est_doublon, rechercher_runbook
from src.contrat import RUNBOOKS, Evenement


def evt(
    event_type="LOG",
    severity="LOW",
    message="ok",
    component="backend",
):
    return Evenement(
        "EVT-00001",
        "2026-10-05T10:00:00Z",
        "DOCKER",
        component,
        "production",
        event_type,
        severity,
        message,
    )


class TestAnalyse(unittest.TestCase):

    def test_doublon(self):
        vus = set()

        self.assertFalse(est_doublon(evt(message="a"), vus))
        self.assertTrue(est_doublon(evt(message="a"), vus))

    def test_pas_doublon_si_message_different(self):
        vus = set()

        self.assertFalse(est_doublon(evt(message="a"), vus))
        self.assertFalse(est_doublon(evt(message="b"), vus))

    def test_rechercher_runbook_trouve(self):
        evenement = evt(message="Erreur OOMKilled sur backend")

        resultat = rechercher_runbook(evenement, RUNBOOKS)

        self.assertEqual(resultat, RUNBOOKS["OOMKilled"])

    def test_rechercher_runbook_sans_resultat(self):
        evenement = evt(message="Message sans mot-cle connu")

        self.assertIsNone(rechercher_runbook(evenement, RUNBOOKS))

    def test_rechercher_runbook_ignore_la_casse(self):
        evenement = evt(message="erreur oomkilled")

        self.assertEqual(
            rechercher_runbook(evenement, RUNBOOKS),
            RUNBOOKS["OOMKilled"],
        )

    def test_classer_redemarrages_critiques(self):
        evenement = evt(
            event_type="CONTAINER_RESTART",
            severity="HIGH",
            message="OOMKilled restarts=14",
        )

        self.assertEqual(classer(evenement), "CRITICAL")

    def test_classer_redemarrages_moderes(self):
        evenement = evt(
            event_type="CONTAINER_RESTART",
            severity="HIGH",
            message="restarts=3",
        )

        self.assertEqual(classer(evenement), "MEDIUM")

    def test_classer_vulnerabilite_critique(self):
        evenement = evt(
            event_type="VULNERABILITY",
            severity="CRITICAL",
            message="CVE-2026-1234",
        )

        self.assertEqual(classer(evenement), "HIGH")

    def test_classer_conserve_severite(self):
        evenement = evt(severity="LOW")

        self.assertEqual(classer(evenement), "LOW")

    def test_analyser(self):
        evenement = evt(
            event_type="CONTAINER_RESTART",
            severity="HIGH",
            message="OOMKilled restarts=14",
        )

        resultat = analyser(evenement, RUNBOOKS)

        self.assertEqual(resultat.event_id, evenement.id)
        self.assertEqual(resultat.criticite, "CRITICAL")
        self.assertEqual(
            resultat.cause_probable,
            RUNBOOKS["OOMKilled"],
        )
        self.assertEqual(
            resultat.action_recommandee,
            "Redémarrer backend",
        )
        self.assertTrue(resultat.sensible)
        self.assertEqual(resultat.sources, ["DOCKER"])
        self.assertEqual(evenement.status, "ANALYSED")


if __name__ == "__main__":
    unittest.main()