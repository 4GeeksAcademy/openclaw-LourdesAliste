import importlib.util
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "show_progress.py"
spec = importlib.util.spec_from_file_location("show_progress", SCRIPT)
mod = importlib.util.module_from_spec(spec)
assert spec.loader
spec.loader.exec_module(mod)


class ProgressTests(unittest.TestCase):
    def test_pagination_required_and_complete(self):
        pages = [
            {"count": 2, "next": "next", "results": [{"id": 1}]},
            {"count": 2, "next": None, "results": [{"id": 2}]},
        ]
        original = mod.call_api
        calls = []
        def fake(path, params=None):
            calls.append(params)
            return pages.pop(0), None
        mod.call_api = fake
        try:
            tasks, complete, error = mod.get_tasks()
        finally:
            mod.call_api = original
        self.assertEqual(len(tasks), 2)
        self.assertTrue(complete)
        self.assertIsNone(error)
        self.assertIn("task_type=PROJECT,EXERCISE,LESSON,QUIZ", calls[0])

    def test_task_percent_unknown_cohort_quiz_and_reviews(self):
        tasks = [
            {"task_type": "QUIZ", "task_status": "DONE"},
            {"task_type": "QUIZ", "task_status": "PENDING"},
            {"task_type": "PROJECT", "task_status": "DONE", "revision_status": "PENDING"},
            {"task_type": "PROJECT", "task_status": "DONE", "revision_status": "APPROVED", "cohort": {"name": "A", "id": 3}},
            {"task_type": "PROJECT", "task_status": "MYSTERY", "revision_status": "REJECTED", "cohort": {"name": "A", "id": 3}},
        ]
        output = "\n".join(mod.render_tasks(tasks, True, None))
        self.assertIn("QUIZ: PENDING 1, DONE 1; entregadas 50.0% (1/2)", output)
        self.assertIn("Cohorte no disponible", output)
        self.assertIn("Revisión de proyectos (indicadores independientes): PENDING 1", output)
        self.assertIn("APPROVED 1", output)
        self.assertIn("REJECTED 1", output)
        self.assertIn("estados ausentes/desconocidos 1", output)
        self.assertIn("Total global", output)

    def test_activity_denial_is_explicit_and_does_not_infer_events(self):
        text = "\n".join(mod.render_activity())
        self.assertIn("HTTP 403", text)
        self.assertIn("No se muestran recuentos", text)
        self.assertIn("no se puede inferir de las tareas", text)
        self.assertIn("no representa un porcentaje", text)

    def test_only_task_cohorts_are_rendered(self):
        text = "\n".join(mod.render_tasks([
            {"task_type": "QUIZ", "task_status": "DONE", "cohort": {"name": "A"}},
        ], True, None))
        self.assertIn("### A", text)
        self.assertNotIn("Cohorte sin tareas", text)
        self.assertIn("no enumera cohortes sin tareas", text)

    def test_zero_known_task_status(self):
        self.assertEqual(mod.pct(0, 0), "Avance no disponible")


if __name__ == "__main__":
    unittest.main()
