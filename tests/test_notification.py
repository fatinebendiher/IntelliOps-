import unittest

from src.contrat import Analyse, Evenement
from src.notification import (choisir_canal, demander_validation, notifier,
                              rediger)


def exemple(sensible=True, criticite="CRITICAL"):
    e = Evenement("EVT-00125", "2026-10-05T10:02:11Z", "DOCKER", "backend",
                  "production", "CONTAINER_RESTART", "HIGH",
                  "OOMKilled restarts=14")
    a = Analyse("EVT-00125", criticite, "Limite mémoire", "Redémarrer backend",
                sensible, ["DOCKER"])
    return e, a


class TestNotification(unittest.TestCase):
    def test_canaux(self):
        self.assertEqual(choisir_canal("CRITICAL"), "TEAMS")
        self.assertEqual(choisir_canal("HIGH"), "TEAMS")
        self.assertEqual(choisir_canal("MEDIUM"), "EMAIL")
        self.assertEqual(choisir_canal("LOW"), "DASHBOARD")

    def test_canal_invalide(self):
        with self.assertRaises(ValueError):
            choisir_canal("INCONNU")

    def test_rediger(self):
        e, a = exemple()
        lignes = rediger(e, a).split("\n")
        self.assertEqual(len(lignes), 5)
        self.assertEqual(lignes[0], "[CRITICAL] Service : backend")
        self.assertEqual(lignes[1], "Incident : OOMKilled restarts=14")
        self.assertEqual(lignes[2], "Cause probable : Limite mémoire")
        self.assertEqual(lignes[3], "Action : Redémarrer backend")
        self.assertEqual(lignes[4], "Sources : DOCKER")

    def test_rediger_plusieurs_sources(self):
        e, a = exemple()
        a.sources = ["DOCKER", "TRIVY"]
        self.assertEqual(rediger(e, a).split("\n")[4], "Sources : DOCKER, TRIVY")

    def test_notifier(self):
        e, a = exemple()
        journal = []
        n = notifier(e, a, journal)
        self.assertEqual(n.event_id, "EVT-00125")
        self.assertEqual(n.canal, "TEAMS")
        self.assertEqual(n.destinataire, "equipe-ops")
        self.assertEqual(n.message, rediger(e, a))
        self.assertEqual(journal, [n])
        self.assertEqual(e.status, "NOTIFIED")

    def test_validation_non_sensible(self):
        _, a = exemple(sensible=False)
        self.assertTrue(demander_validation(a, "n"))

    def test_validation_variantes(self):
        _, a = exemple()
        for rep in ("o", "OUI", " y ", "Yes", " OUI "):
            self.assertTrue(demander_validation(a, rep))
        for rep in ("n", "non", "", "peut-être"):
            self.assertFalse(demander_validation(a, rep))


if __name__ == "__main__":
    unittest.main()