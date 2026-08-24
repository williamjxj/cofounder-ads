import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from engine import supabase_store as store  # noqa: E402


class TableMappingTest(unittest.TestCase):
    def test_maps_csv_names_to_supabase_tables(self):
        self.assertEqual(store.table_for(Path("ledger.csv")), "ads_ledger")
        self.assertEqual(store.table_for(Path("/any/dir/ledger.csv")), "ads_ledger")
        self.assertEqual(store.table_for(Path("crm.csv")), "ads_crm")

    def test_unknown_file_raises(self):
        with self.assertRaises(ValueError):
            store.table_for(Path("other.csv"))


class EnvLoadingTest(unittest.TestCase):
    def tearDown(self):
        for key in ("SUPABASE_URL", "SUPABASE_SECRET_KEY", "ADS_TEST_VAR"):
            os.environ.pop(key, None)

    def _write_env(self, content: str) -> Path:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        path = Path(tmp.name) / ".env"
        path.write_text(content, encoding="utf-8")
        return path

    def test_loads_keys_and_strips_quotes(self):
        path = self._write_env(
            '# comment\nADS_TEST_VAR="hello world"\nSUPABASE_URL=https://x.supabase.co\n'
        )
        store.load_env_file(path)
        self.assertEqual(os.environ.get("ADS_TEST_VAR"), "hello world")
        self.assertEqual(os.environ.get("SUPABASE_URL"), "https://x.supabase.co")

    def test_does_not_override_existing_environment(self):
        os.environ["ADS_TEST_VAR"] = "existing"
        path = self._write_env("ADS_TEST_VAR=new\n")
        store.load_env_file(path)
        self.assertEqual(os.environ["ADS_TEST_VAR"], "existing")

    def test_enabled_requires_url_and_secret(self):
        self.assertFalse(store.enabled())
        os.environ["SUPABASE_URL"] = "https://x.supabase.co"
        self.assertFalse(store.enabled())
        os.environ["SUPABASE_SECRET_KEY"] = "secret"
        self.assertTrue(store.enabled())


if __name__ == "__main__":
    unittest.main()
