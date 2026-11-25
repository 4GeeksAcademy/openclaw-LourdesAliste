from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import show_pending_work as skill


class PendingWorkTests(unittest.TestCase):
    def test_extract_page_shapes(self):
        self.assertEqual(skill.extract_page([{"id": 1}]), ([{"id": 1}], None, False))
        self.assertEqual(skill.extract_page({"count": 2, "next": "?offset=1", "results": [{"id": 1}]}),
                         ([{"id": 1}], 2, True))
        with self.assertRaises(ValueError):
            skill.extract_page({"results": []})

    def test_fetch_all_pages_preserves_order_and_requests_unfiltered_status(self):
        payloads = [
            {"count": 3, "next": "?offset=2", "results": [{"id": 1}, {"id": 2}]},
            {"count": 3, "next": None, "results": [{"id": 3}]},
        ]
        with patch.object(skill, "call_api", side_effect=[(x, None) for x in payloads]) as call:
            tasks, initial, error = skill.get_all_tasks()
        self.assertEqual([x["id"] for x in tasks], [1, 2, 3])
        self.assertFalse(initial)
        self.assertIsNone(error)
        self.assertEqual(call.call_count, 2)
        self.assertTrue(all(not any(p.startswith("task_status=") for p in args[0][1]) for args in call.call_args_list))
        self.assertIn("task_type=PROJECT,EXERCISE,LESSON", call.call_args.args[1])

    def test_later_page_error_is_incomplete_not_initial(self):
        with patch.object(skill, "call_api", side_effect=[
            ({"count": 2, "next": "?offset=1", "results": [{"id": 1}]}, None),
            (None, "API request failed with HTTP 503; response body suppressed."),
        ]):
            tasks, initial, error = skill.get_all_tasks()
        self.assertEqual(tasks, [{"id": 1}])
        self.assertFalse(initial)
        self.assertIn("503", error)
        text = skill.render(tasks, True, initial, error)
        self.assertNotIn("No tienes tareas pendientes", text)
        self.assertIn("incompleto", text)

    def test_plain_list_not_assumed_complete(self):
        with patch.object(skill, "call_api", return_value=([{ "id": 1}], None)):
            tasks, initial, error = skill.get_all_tasks()
        self.assertEqual(len(tasks), 1)
        self.assertFalse(initial)
        self.assertIn("no verificable", error)

    def test_status_classification_independent_of_revision(self):
        self.assertTrue(skill.is_pending({"task_status": "PENDING", "revision_status": "APPROVED"}))
        self.assertFalse(skill.is_pending({"task_status": "DONE", "revision_status": "PENDING"}))
        self.assertTrue(skill.is_unknown_status({"revision_status": "PENDING"}))
        self.assertTrue(skill.is_unknown_status({"task_status": "FUTURE"}))
        self.assertTrue(skill.is_unknown_status({"task_status": "APPROVED"}))
        self.assertFalse(skill.is_unknown_status({"task_status": "DONE"}))

    def test_details_only_for_pending_and_failure_preserves_task(self):
        rows = [
            {"id": 1, "title": "Pending", "task_status": "PENDING", "task_type": "PROJECT"},
            {"id": 2, "task_status": "MYSTERY"},
            {"id": 3, "task_status": "DONE"},
        ]
        with patch.object(skill, "get_detail", return_value=(None, "HTTP 502")) as detail:
            text = skill.render(rows, False, False, None)
        detail.assert_called_once_with(1)
        self.assertIn("No se pudo obtener el detalle de esta tarea", text)
        self.assertIn("HTTP 502", text)
        self.assertIn("Estado no identificar", text)
        self.assertIn("MYSTERY", text)
        self.assertNotIn("### no identificada (ID: 3)", text)

    def test_missing_status_and_title_and_id_format(self):
        text = skill.render([{"task_status": None}], False, False, None)
        self.assertIn("### no identificada", text)
        self.assertIn("Estado: Sin estado", text)
        self.assertIn("no disponible", text)

    def test_full_success_empty_has_no_pending_message(self):
        self.assertEqual(skill.render([], False, False, None),
                         "## Resumen de tareas pendientes\nNo tienes tareas pendientes")

    def test_personal_and_telemetry_fields_are_not_rendered(self):
        task = {"id": 4, "title": "Pending", "task_status": "PENDING", "user": {"email": "private"},
                "assignment_telemetry": {"secret": "private"}}
        with patch.object(skill, "get_detail", return_value=({"user": {"email": "private"},
                                                                "assignment_telemetry": {"secret": "private"}}, None)):
            text = skill.render([task], False, False, None)
        self.assertNotIn("private", text)
        self.assertNotIn("assignment_telemetry", text)
        self.assertIn("no disponible", text)


if __name__ == "__main__":
    unittest.main()
