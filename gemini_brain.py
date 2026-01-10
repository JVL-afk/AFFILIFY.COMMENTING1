# gemini_brain.py - THE AI BRAIN (Gemini 2.5 Flash Edition - Modern SDK)

from google import genai
from google.genai import types
import json
import asyncio
import os
from typing import Dict, Optional, List
from logger_system import log_ai, log_error, log_start, log_end, affilify_logger

class GeminiAssistant:
    """
    Gemini 2.5 Flash Integration using the modern google.genai SDK.
    Adaptive code generation & decision making.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            affilify_logger.main_logger.error("❌ GEMINI_API_KEY not found for GeminiAssistant")
            raise ValueError("GEMINI_API_KEY is required")
            
        self.client = genai.Client(api_key=self.api_key)
        self.model_name = 'gemini-2.5-flash'
        affilify_logger.main_logger.info(f"✅ Gemini Assistant initialized with {self.model_name} (Modern SDK)")
    
    async def generate_code(self, task: str, context: Dict, html_snippet: str = None) -> Optional[str]:
        """
        Generate Python code for specific task
        """
        start = log_start("Gemini_CodeGen", task=task)
        prompt = self._build_code_prompt(task, context, html_snippet)
        
        try:
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.2,
                    top_p=0.95,
                    top_k=40,
                    max_output_tokens=2048,
                )
            )
            
            code = response.text.strip()
            
            # Extract code block
            if '```python' in code:
                code = code.split('```python')[1].split('```')[0].strip()
            elif '```' in code:
                code = code.split('```')[1].split('```')[0].strip()
            
            log_ai('Gemini-Flash', {'task': task, 'context': context}, code[:200])
            log_end("Gemini_CodeGen", start, True, code_length=len(code))
            return code
            
        except Exception as e:
            log_error("Gemini_CodeGen_Error", str(e), context={'task': task})
            log_end("Gemini_CodeGen", start, False, error=str(e))
            return None
    
    def _build_code_prompt(self, task: str, context: Dict, html_snippet: str = None) -> str:
        prompt = f"""You are an expert Playwright automation engineer.

TASK: {task}

CONTEXT:
{json.dumps(context, indent=2)}

"""
        if html_snippet:
            prompt += f"""
HTML STRUCTURE (truncated):
```html
{html_snippet[:5000]}
```

"""
        prompt += """
REQUIREMENTS:
1. Generate ONLY executable Python code (no explanations)
2. Use Playwright async API
3. Include comprehensive error handling
4. Add detailed logging at each step
5. Use multiple selector fallbacks (CSS + XPath)
6. Implement human-like delays and behavior
7. Return success/failure boolean

CODE TEMPLATE:
```python
async def {task.lower().replace(' ', '_')}(page, **kwargs):
    from logger_system import log_start, log_end, log_error
    import random
    import asyncio
    
    start = log_start('{task}', **kwargs)
    
    try:
        # Your implementation here
        
        # Log each step
        # Use random delays
        # Multiple selectors
        
        log_end('{task}', start, True)
        return True
    except Exception as e:
        log_error('{task}', str(e))
        log_end('{task}', start, False, error=str(e))
        return False
```

Generate the complete function now:
"""
        return prompt

    async def analyze_system_health(self, prompt: str) -> Dict:
        """
        Analyze system health and return JSON
        """
        start = log_start("Gemini_HealthAnalysis")
        try:
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model=self.model_name,
                contents=prompt
            )
            
            text = response.text.strip()
            if '{' in text:
                json_str = text[text.find('{'):text.rfind('}')+1]
                analysis = json.loads(json_str)
                log_end("Gemini_HealthAnalysis", start, True)
                return analysis
            
            log_end("Gemini_HealthAnalysis", start, False, error="No JSON found")
            return {}
        except Exception as e:
            log_error("Gemini_HealthAnalysis_Error", str(e))
            log_end("Gemini_HealthAnalysis", start, False, error=str(e))
            return {}

    async def analyze_error(self, error_log: str, page_state: Dict) -> Dict:
        start = log_start("Gemini_ErrorAnalysis")
        prompt = f"""Analyze this error and provide actionable solutions.

ERROR LOG:
{error_log}

PAGE STATE:
{json.dumps(page_state, indent=2)}

Respond with JSON:
{{
    "error_type": "selector_failure|timeout|rate_limit|...",
    "root_cause": "...",
    "solutions": [
        {{"action": "...", "code": "..."}},
        {{"action": "...", "code": "..."}}
    ],
    "priority": "high|medium|low",
    "can_auto_fix": true|false
}}
"""
        try:
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model=self.model_name,
                contents=prompt
            )
            text = response.text.strip()
            if '{' in text:
                json_str = text[text.find('{'):text.rfind('}')+1]
                analysis = json.loads(json_str)
                log_end("Gemini_ErrorAnalysis", start, True)
                return analysis
            return {}
        except Exception as e:
            log_error("Gemini_ErrorAnalysis_Error", str(e))
            log_end("Gemini_ErrorAnalysis", start, False, error=str(e))
            return {}

    async def optimize_timing(self, success_data: List[Dict], failure_data: List[Dict]) -> Dict:
        prompt = f"""Analyze these operation logs and optimize timing parameters.
SUCCESSFUL OPERATIONS: {json.dumps(success_data[:20])}
FAILED OPERATIONS: {json.dumps(failure_data[:20])}
Respond with JSON containing optimized values.
"""
        try:
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model=self.model_name,
                contents=prompt
            )
            text = response.text.strip()
            if '{' in text:
                return json.loads(text[text.find('{'):text.rfind('}')+1])
            return {}
        except:
            return {}

    async def generate_selector_alternatives(self, failed_selector: str, html_context: str) -> List[str]:
        prompt = f"""Generate 5 alternative selectors for: {failed_selector}
HTML: {html_context[:2000]}
Respond with JSON array: ["sel1", "sel2", ...]
"""
        try:
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model=self.model_name,
                contents=prompt
            )
            text = response.text.strip()
            if '[' in text:
                return json.loads(text[text.find('['):text.rfind(']')+1])
            return []
        except:
            return []

# Global instance placeholder
gemini_assistant = None

def init_gemini_assistant(api_key: str):
    global gemini_assistant
    gemini_assistant = GeminiAssistant(api_key)
    return gemini_assistant
