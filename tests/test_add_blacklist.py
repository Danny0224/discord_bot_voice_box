"""Run: python -m unittest discover -s tests -v
Expected failures document unresolved PR bugs; remove decorators after fixes.
No Discord dependency or live state files are used.
"""
import importlib.util
import io
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch


class AddBlacklistTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        source = Path(__file__).resolve().parents[1] / "class_box.py"
        copied = Path(self.temp.name) / "class_box.py"
        shutil.copyfile(source, copied)
        spec = importlib.util.spec_from_file_location("isolated_class_box", copied)
        self.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.module)
        self.box = self.module.app_box(1, 100)

    def read(self):
        return self.module.load_data()

    def test_add_persists_and_reload_sees_member(self):
        data = self.read()
        data["200"] = {"blacklist": [9], "owner": 2}
        self.module.save_data(data)
        self.box.add_blacklist(42)
        self.assertEqual(self.read()["100"]["blacklist"], [42])
        self.assertEqual(self.box.blacklist, [42])
        self.assertEqual(self.module.box_id(100).blacklist, [42])
        self.assertEqual(self.read()["200"], data["200"])

    def test_deleted_room_does_not_write_or_change_instance(self):
        self.module.save_data({})
        before = Path(self.module.json_path).read_bytes()
        with patch.object(self.module, "save_data") as save, redirect_stdout(io.StringIO()) as output:
            self.box.add_blacklist(42)
        save.assert_not_called()
        self.assertEqual(Path(self.module.json_path).read_bytes(), before)
        self.assertEqual(self.box.blacklist, [])
        self.assertIn("語音房不存在", output.getvalue())

    def test_none_root_does_not_write(self):
        with patch.object(self.module, "load_data", return_value=None), patch.object(self.module, "save_data") as save, redirect_stdout(io.StringIO()):
            self.box.add_blacklist(42)
        save.assert_not_called()
        self.assertEqual(self.box.blacklist, [])

    def test_save_error_does_not_update_instance(self):
        before = Path(self.module.json_path).read_bytes()
        with patch.object(self.module, "save_data", side_effect=OSError("disk failure")):
            with self.assertRaises(OSError):
                self.box.add_blacklist(42)
        self.assertEqual(self.box.blacklist, [])
        self.assertEqual(Path(self.module.json_path).read_bytes(), before)

    @unittest.expectedFailure
    def test_missing_box_id_can_be_used_without_exception(self):
        missing = self.module.box_id(999)
        with patch.object(self.module, "save_data") as save, redirect_stdout(io.StringIO()):
            missing.add_blacklist(42)
        save.assert_not_called()

    @unittest.expectedFailure
    def test_missing_blacklist_initializes_empty_list(self):
        data = self.read()
        del data["100"]["blacklist"]
        self.module.save_data(data)
        self.box.add_blacklist(42)
        self.assertEqual(self.read()["100"]["blacklist"], [42])

    @unittest.expectedFailure
    def test_null_blacklist_initializes_empty_list(self):
        data = self.read()
        data["100"]["blacklist"] = None
        self.module.save_data(data)
        self.box.add_blacklist(42)
        self.assertEqual(self.read()["100"]["blacklist"], [42])

    @unittest.expectedFailure
    def test_repeated_add_is_idempotent(self):
        self.box.add_blacklist(42)
        self.box.add_blacklist(42)
        self.assertEqual(self.read()["100"]["blacklist"], [42])
        self.assertEqual(self.box.blacklist, [42])

    @unittest.expectedFailure
    def test_serialization_error_preserves_existing_file(self):
        before = Path(self.module.json_path).read_bytes()
        with patch.object(self.module.json, "dump", side_effect=OSError("write failure")):
            with self.assertRaises(OSError):
                self.box.add_blacklist(42)
        self.assertEqual(Path(self.module.json_path).read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
