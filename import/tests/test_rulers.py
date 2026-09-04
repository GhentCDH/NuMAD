import unittest
from unittest.mock import Mock, patch

from numad_import.cli import get_or_create_rulers
from numad_import.model import Ruler
from numad_import.util import parse_ruler_names


class ParseRulerNamesTests(unittest.TestCase):
    def test_splits_semicolon_separated_names(self):
        self.assertEqual(
            parse_ruler_names("Vespasianus ; Titus"),
            ["Vespasianus", "Titus"],
        )

    def test_splits_semicolon_without_surrounding_spaces(self):
        self.assertEqual(
            parse_ruler_names("Augustus; Tiberius"),
            ["Augustus", "Tiberius"],
        )

    def test_splits_three_names(self):
        self.assertEqual(
            parse_ruler_names("Vespasianus ; Titus ; Domitianus"),
            ["Vespasianus", "Titus", "Domitianus"],
        )

    def test_splits_or_case_insensitively(self):
        self.assertEqual(
            parse_ruler_names("<Geta OR Severus Alexander>"),
            ["Geta", "Severus Alexander"],
        )

    def test_removes_sentinels_and_duplicates(self):
        self.assertEqual(parse_ruler_names("Titus ; <Titus>"), ["Titus"])
        self.assertEqual(parse_ruler_names("<type_to_rulers>"), [])
        self.assertEqual(parse_ruler_names(None), [])

    def test_does_not_split_hyphenated_values(self):
        self.assertEqual(len(parse_ruler_names("Nerva - Commodus")), 1)


class GetOrCreateRulersTests(unittest.TestCase):
    @patch("numad_import.cli.get_or_create")
    def test_multi_authority_rows_do_not_assign_aggregate_dates(self, get_or_create):
        get_or_create.side_effect = [
            Ruler(id=1, name="Vespasianus"),
            Ruler(id=2, name="Titus"),
        ]

        rulers = get_or_create_rulers(
            Mock(), {}, "Vespasianus ; Titus", "69", "81"
        )

        self.assertEqual([ruler.name for ruler in rulers], ["Vespasianus", "Titus"])
        for call in get_or_create.call_args_list:
            self.assertIsNone(call.kwargs["start_date"])
            self.assertIsNone(call.kwargs["end_date"])

    @patch("numad_import.cli.get_or_create")
    def test_standalone_row_fills_missing_dates(self, get_or_create):
        ruler = Ruler(id=1, name="Numerianus")
        get_or_create.return_value = ruler

        get_or_create_rulers(Mock(), {}, "Numerianus", "283", "284")

        self.assertEqual(ruler.start_date, 283)
        self.assertEqual(ruler.end_date, 284)


if __name__ == "__main__":
    unittest.main()
