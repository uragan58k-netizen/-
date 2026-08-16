# -*- coding: utf-8 -*-
from aiogram import Router

from .main_menu import router as main_menu_router
from .deal_flow import router as deal_flow_router

router = Router(name="root")
router.include_router(main_menu_router)
router.include_router(deal_flow_router)

__all__ = ["router"]
