import importlib.util
import os
import tempfile
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from io import BytesIO
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / "scripts" / "api_get.py"
spec = importlib.util.spec_from_file_location("api_get", SCRIPT)
api_get = importlib.util.module_from_spec(spec)
spec.loader.exec_module(api_get)

launcher_path = SCRIPT.with_name("run_api_get.py")
launcher_spec = importlib.util.spec_from_file_location("run_api_get", launcher_path)
launcher = importlib.util.module_from_spec(launcher_spec)
launcher_spec.loader.exec_module(launcher)


class ClientTests(unittest.TestCase):
    def test_allows_expected_and_rejects_writes_or_ambiguous_paths(self):
        self.assertTrue(api_get.is_allowed("/v1/admissions/user/me"))
        self.assertTrue(api_get.is_allowed("/v1/assignment/task/123"))
        self.assertTrue(api_get.is_allowed("/v1/registry/asset/my-lesson"))
        for path in (
            "/v1/assignment/task/123/deliver", "/v1/assignment/task/abc",
            "/v1/registry/asset/me/extra", "/v1/admissions/user/me?x=1",
            "/v1/registry/asset/%2e%2e", "https://evil.example/v1/admissions/user/me",
        ):
            self.assertFalse(api_get.is_allowed(path), path)

    @patch.dict(os.environ, {}, clear=True)
    def test_missing_credential_stops_before_network(self):
        with patch.object(api_get.sys, "argv", [str(SCRIPT), "/v1/admissions/user/me"]), \
             patch.object(api_get, "build_opener") as network, \
             patch.object(api_get, "print") as output:
            self.assertEqual(api_get.main(), 2)
            network.assert_not_called()
            self.assertNotIn("Token", " ".join(str(c) for c in output.call_args_list))

    @patch.dict(os.environ, {"TOKEN_4GEEKS": "dummy-test-token"}, clear=True)
    def test_uses_get_and_suppresses_body_without_live_network(self):
        captured = {}
        class Response:
            headers = type("Headers", (), {"get_content_charset": lambda self: "utf-8"})()
            def __enter__(self): return self
            def __exit__(self, *args): return False
            def geturl(self): return "https://breathecode.herokuapp.com/v1/admissions/user/me"
            def read(self, n): return b'{"private":"response"}'
        def fake_open(request, timeout):
            captured["method"] = request.get_method()
            captured["auth"] = request.get_header("Authorization")
            captured["timeout"] = timeout
            return Response()
        with patch.object(api_get.sys, "argv", [str(SCRIPT), "/v1/admissions/user/me"]), \
             patch.object(api_get, "build_opener") as opener_factory, \
             patch.object(api_get, "print") as output:
            opener_factory.return_value.open.side_effect = fake_open
            self.assertEqual(api_get.main(), 0)
        self.assertEqual(captured["method"], "GET")
        self.assertEqual(captured["auth"], "Token dummy-test-token")
        self.assertNotIn("private", " ".join(str(c) for c in output.call_args_list))

    @patch.dict(os.environ, {"TOKEN_4GEEKS": "dummy-test-token", "FOURGEEKS_API_OUTPUT_JSON": "1"}, clear=True)
    def test_opt_in_json_output_is_exact_body_without_success_banner(self):
        class Response:
            headers = type("Headers", (), {"get_content_charset": lambda self: "utf-8"})()
            def __enter__(self): return self
            def __exit__(self, *args): return False
            def geturl(self): return "https://breathecode.herokuapp.com/v1/assignment/user/me/task?task_type=PROJECT"
            def read(self, n): return b'{"count":0,"results":[]}'
        with patch.object(api_get.sys, "argv", [str(SCRIPT), "/v1/assignment/user/me/task", "--param", "task_type=PROJECT"]), \
             patch.object(api_get, "build_opener") as opener_factory, \
             patch.object(api_get.sys, "stdout") as stdout, \
             patch.object(api_get, "print") as output:
            opener_factory.return_value.open.return_value = Response()
            self.assertEqual(api_get.main(), 0)
        stdout.write.assert_any_call('{"count":0,"results":[]}')
        output.assert_not_called()

    @patch.dict(os.environ, {"TOKEN_4GEEKS": "dummy-test-token"}, clear=True)
    def test_http_body_is_not_printed(self):
        err = HTTPError("https://breathecode.herokuapp.com", 401, "Unauthorized", {}, BytesIO(b"sensitive"))
        with patch.object(api_get.sys, "argv", [str(SCRIPT), "/v1/admissions/user/me"]), \
             patch.object(api_get, "build_opener") as opener_factory, \
             patch.object(api_get, "print") as output:
            opener_factory.return_value.open.side_effect = err
            self.assertEqual(api_get.main(), 1)
        self.assertNotIn("sensitive", " ".join(str(c) for c in output.call_args_list))

    def test_launcher_reads_named_value_and_enforces_file_permissions(self):
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8") as handle:
            handle.write("UNRELATED=ignored\nexport TOKEN_4GEEKS=fixture-value\n")
            handle.flush()
            os.chmod(handle.name, 0o600)
            self.assertEqual(launcher.read_token(Path(handle.name)), "fixture-value")
            os.chmod(handle.name, 0o644)
            with self.assertRaises(ValueError):
                launcher.read_token(Path(handle.name))

    def test_redirects_are_disabled(self):
        class NoRedirect(api_get.HTTPRedirectHandler):
            def redirect_request(self, req, fp, code, msg, headers, newurl):
                return None
        handler = NoRedirect()
        request = api_get.Request("https://breathecode.herokuapp.com/v1/admissions/user/me", method="GET")
        self.assertIsNone(handler.redirect_request(request, None, 302, "Found", {}, "https://other.invalid"))


if __name__ == "__main__":
    unittest.main()
