import pytest
import datetime
from unittest.mock import AsyncMock, MagicMock
from backend.app.services.fine_service import FineService

@pytest.mark.asyncio
async def test_calculate_delay_fine():
    fine_service = FineService()
    # Mock the fine database repository to return fixed rules for consistency
    fine_service.fine_repo = MagicMock()
    fine_service.fine_repo.get_active_rules = AsyncMock(return_value={
        "rules": {
            "0": 0.0,
            "1": 10.0,
            "2": 20.0,
            "3": 40.0,
            "4": 80.0
        }
    })
    
    # Test case 1: Applied on the same day (0 days delay) -> ₹0 fine
    absent_date = datetime.datetime(2026, 7, 5)
    applied_date = datetime.datetime(2026, 7, 5)
    fine = await fine_service.calculate_delay_fine(absent_date, applied_date)
    assert fine == 0.0
    
    # Test case 2: Applied with 2 days delay -> ₹20 fine
    applied_date_2 = datetime.datetime(2026, 7, 7)
    fine_2 = await fine_service.calculate_delay_fine(absent_date, applied_date_2)
    assert fine_2 == 20.0
    
    # Test case 3: Applied with 5 days delay -> progressive cap ₹80 + (5-4)*20 surcharge = ₹100
    applied_date_3 = datetime.datetime(2026, 7, 10)
    fine_3 = await fine_service.calculate_delay_fine(absent_date, applied_date_3)
    assert fine_3 == 100.0
