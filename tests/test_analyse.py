import unittest
from src.analyse import analyser, classer, est_doublon, rechercher_runbook
from src.contrat import RUNBOOKS, Evenement


def evt(event_type="LOG", severity="LOW", message="ok", component="backend"):
    return Evenement("EVT-00001", "2026-10-05T10:00:00Z", "DOCKER", component,
                     "production", event_type, severity, message)


class TestAnalyse(unittest.TestCase):
    def test_doublon(self):
        vus = set()
        self.assertFalse(est_doublon(evt(message="a"), vus))
        self.assertTrue(est_doublon(evt(message="a"), vus))

    def test_pas_doublon_si_message_different(self):
        vus = set()
        self.assertFalse(est_doublon(evt(message="a"), vus))
        self.assertFalse(est_doublon(evt(message="b"), vus))


if __name__ == "__main__":
    unittest.main()