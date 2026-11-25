import importlib.util
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPT = Path(__file__).parents[1] / "scripts" / "show_projects.py"
spec = importlib.util.spec_from_file_location("show_projects", SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class ProjectSkillTests(unittest.TestCase):
    def test_pagination_order_and_query(self):
        pages = [
            {"count": 3, "next": "?offset=2", "results": [{"id": 1}, {"id": 2}]},
            {"count": 3, "next": None, "results": [{"id": 3}]},
        ]
        calls = []
        def fake(path, params):
            calls.append((path, params))
            return pages.pop(0), None
        with patch.object(mod, "call_api", side_effect=fake):
            items, failed, error = mod.get_projects()
        self.assertEqual([x["id"] for x in items], [1, 2, 3])
        self.assertFalse(failed)
        self.assertIsNone(error)
        self.assertEqual(calls[0][1], ["task_type=PROJECT", "limit=100", "offset=0"])

    def test_classification_uses_both_states_without_guessing(self):
        self.assertEqual(mod.status_bucket({"task_status": "PENDING"}), "Pendientes")
        self.assertEqual(mod.status_bucket({"task_status": "DONE", "revision_status": "PENDING"}), "Entregados")
        self.assertEqual(mod.status_bucket({"task_status": "DONE", "revision_status": "APPROVED"}), "Aprobados")
        self.assertEqual(mod.status_bucket({"task_status": "DONE", "revision_status": "REJECTED"}), "Rechazados")
        self.assertEqual(mod.status_bucket({"task_status": "DONE", "revision_status": "IGNORED"}), "Entregados")
        self.assertEqual(mod.status_bucket({"task_status": "MYSTERY"}), "Estado no identificado: MYSTERY")
        self.assertEqual(mod.status_bucket({}), "Estado no identificado: sin valor")

    def test_empty_groups_only_when_list_complete(self):
        complete = mod.render([], True, False, None)
        self.assertEqual(complete.count("No hay proyectos en este estado"), 4)
        partial = mod.render([], False, False, "HTTP 503")
        self.assertNotIn("No hay proyectos en este estado", partial)
        self.assertIn("lista está incompleta", partial)

    def test_initial_failure_is_not_empty_state(self):
        text = mod.render([], False, True, "HTTP 401")
        self.assertIn("No se han podido recuperar los proyectos", text)
        self.assertNotIn("No hay proyectos en este estado", text)

    def test_detail_failure_preserves_list_data_without_user_or_telemetry(self):
        record = {"id": 10, "title": "Demo", "task_status": "DONE", "user": {"email": "private"}, "assignment_telemetry": {"x": 1}}
        with patch.object(mod, "detail", return_value=(None, "HTTP 404")):
            text = mod.render([record], True, False, None)
        self.assertIn("Demo", text)
        self.assertIn("No se pudo obtener el detalle", text)
        self.assertIn("HTTP 404", text)
        self.assertNotIn("private", text)
        self.assertNotIn("telemetry", text.lower())

    def test_later_page_failure_retains_prior_items(self):
        answers = [({"count": 2, "next": "?offset=1", "results": [{"id": 1, "title": "A"}]}, None), (None, "HTTP 503")]
        with patch.object(mod, "call_api", side_effect=answers):
            items, initial, error = mod.get_projects()
        self.assertEqual([x["title"] for x in items], ["A"])
        self.assertFalse(initial)
        self.assertEqual(error, "HTTP 503")


if __name__ == "__main__":
    unittest.main()
