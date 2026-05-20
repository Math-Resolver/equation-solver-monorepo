from pathlib import Path
import sys
import unittest
from unittest.mock import patch, AsyncMock

APP_ROOT = Path(__file__).resolve().parents[1]
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

from domain.equations.history.persistence import (
    schedule_history_persistence,
    save_equation_history,
)


class HistoryPersistenceTests(unittest.IsolatedAsyncioTestCase):

    async def test_schedule_chama_save_uma_vez(self) -> None:
        with patch(
            "domain.equations.history.persistence.save_equation_history",
            new_callable=AsyncMock,
        ) as mock_save:
            await schedule_history_persistence(
                username="rene",
                equation="2x+3=7",
                result="x=2",
                steps=[],
                created_at="2026-05-20",
            )

            mock_save.assert_called_once()

    async def test_schedule_passa_dados_corretos_para_save(self) -> None:
        with patch(
            "domain.equations.history.persistence.save_equation_history",
            new_callable=AsyncMock,
        ) as mock_save:
            await schedule_history_persistence(
                username="rene",
                equation="2x+3=7",
                result="x=2",
                steps=[],
                created_at="2026-05-20",
            )

            mock_save.assert_called_once_with(
                username="rene",
                equation="2x+3=7",
                result="x=2",
                steps=[],
                created_at="2026-05-20",
            )

    async def test_save_usa_upsert_com_chave_composta(self) -> None:
        with patch(
            "domain.equations.history.persistence.collection"
        ) as mock_collection:
            mock_collection.update_one = AsyncMock()

            await save_equation_history(
                username="rene",
                equation="2x+3=7",
                result="x=2",
                steps=[],
                created_at="2026-05-20",
            )

            args, kwargs = mock_collection.update_one.call_args
            filtro = args[0]

            self.assertIn("username", filtro)
            self.assertIn("equation", filtro)
            self.assertIn("createdAt", filtro)
            self.assertEqual(filtro["username"], "rene")
            self.assertEqual(filtro["equation"], "2x+3=7")
            self.assertEqual(filtro["createdAt"], "2026-05-20")
            self.assertTrue(kwargs.get("upsert"))


if __name__ == "__main__":
    unittest.main()