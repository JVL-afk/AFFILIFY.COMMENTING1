# dolphin_integration.py - THE AI BRAIN (Redirected to Gemini)

import asyncio
from typing import Dict, Optional, List
from logger_system import affilify_logger

class DolphinX1Assistant:
    """
    Dolphin-X1-Llama-3.1 Interface (Legacy)
    Now redirected to Gemini 2.5 Flash for superior performance.
    """
    
    def __init__(self):
        self.model = "gemini-2.5-flash"
        affilify_logger.main_logger.info("🚀 DolphinX1 interface redirected to Gemini 2.5 Flash")
    
    async def generate_code(self, task: str, context: Dict, html_snippet: str = None) -> Optional[str]:
        from gemini_brain import gemini_assistant
        if not gemini_assistant:
            return None
        return await gemini_assistant.generate_code(task, context, html_snippet)
    
    async def analyze_error(self, error_log: str, page_state: Dict) -> Dict:
        from gemini_brain import gemini_assistant
        if not gemini_assistant:
            return {}
        return await gemini_assistant.analyze_error(error_log, page_state)
    
    async def optimize_timing(self, success_data: List[Dict], failure_data: List[Dict]) -> Dict:
        from gemini_brain import gemini_assistant
        if not gemini_assistant:
            return {}
        return await gemini_assistant.optimize_timing(success_data, failure_data)
    
    async def generate_selector_alternatives(self, failed_selector: str, html_context: str) -> List[str]:
        from gemini_brain import gemini_assistant
        if not gemini_assistant:
            return []
        return await gemini_assistant.generate_selector_alternatives(failed_selector, html_context)

# Global instance
dolphin = DolphinX1Assistant()
