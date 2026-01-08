# dolphin_integration.py - THE AI BRAIN

import subprocess
import json
import asyncio
from typing import Dict, Optional, List
from logger_system import log_ai, log_error, log_start, log_end

class DolphinX1Assistant:
    """
    Dolphin-X1-Llama-3.1 Integration
    Adaptive code generation & decision making
    """
    
    def __init__(self):
        self.model = "dolphin-x1-llama-3.1:latest"
        self.setup_model()
    
    def setup_model(self):
        """
        Setup Dolphin-X1 via Ollama
        """
        start = log_start("DolphinX1_Setup", model=self.model)
        
        try:
            # Check if Ollama is installed
            result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, timeout=5)
            
            if 'dolphin-x1-llama-3.1' not in result.stdout:
                print("⚠️  Dolphin-X1 not found. Installing...")
                subprocess.run(['ollama', 'pull', self.model], check=True)
                print("✅ Dolphin-X1 installed successfully")
            
            log_end("DolphinX1_Setup", start, True, model_ready=True)
            
        except subprocess.CalledProcessError as e:
            log_error("DolphinX1_Setup", f"Failed to setup: {e}")
            log_end("DolphinX1_Setup", start, False, error=str(e))
    
    async def generate_code(self, task: str, context: Dict, html_snippet: str = None) -> Optional[str]:
        """
        Generate Python code for specific task
        
        Dolphin-X1's steerability makes it perfect for:
        - Dynamic selector generation
        - Error recovery code
        - Timing optimization
        - Pattern adaptation
        """
        start = log_start("DolphinX1_CodeGen", task=task)
        
        # Build comprehensive prompt
        prompt = self._build_code_prompt(task, context, html_snippet)
        
        try:
            # Run Dolphin-X1
            process = await asyncio.create_subprocess_exec(
                'ollama', 'run', self.model,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(prompt.encode()),
                timeout=45.0
            )
            
            code = stdout.decode().strip()
            
            # Extract code block
            if '```python' in code:
                code = code.split('```python')[1].split('```')[0].strip()
            elif '```' in code:
                code = code.split('```')[1].split('```')[0].strip()
            
            # Log AI decision
            log_ai('Dolphin-X1', {'task': task, 'context': context}, code[:200])
            
            log_end("DolphinX1_CodeGen", start, True, code_length=len(code))
            return code
            
        except asyncio.TimeoutError:
            log_error("DolphinX1_Timeout", "Code generation timeout", context={'task': task})
            log_end("DolphinX1_CodeGen", start, False, error="timeout")
            return None
        except Exception as e:
            log_error("DolphinX1_Error", str(e), context={'task': task})
            log_end("DolphinX1_CodeGen", start, False, error=str(e))
            return None
    
    def _build_code_prompt(self, task: str, context: Dict, html_snippet: str = None) -> str:
        """
        Build optimized prompt for Dolphin-X1
        """
        prompt = f"""You are an expert Playwright automation engineer.

TASK: {task}

CONTEXT:
{json.dumps(context, indent=2)}

"""
        
        if html_snippet:
            prompt += f"""
HTML STRUCTURE (truncated):
```html
{html_snippet[:3000]}
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
    
    async def analyze_error(self, error_log: str, page_state: Dict) -> Dict:
        """
        Analyze error and suggest fixes
        """
        start = log_start("DolphinX1_ErrorAnalysis", error_type=error_log[:100])
        
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

JSON Response:
"""
        
        try:
            process = await asyncio.create_subprocess_exec(
                'ollama', 'run', self.model,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(prompt.encode()),
                timeout=30.0
            )
            
            response = stdout.decode().strip()
            
            # Extract JSON
            if '{' in response:
                json_str = response[response.find('{'):response.rfind('}')+1]
                analysis = json.loads(json_str)
                
                log_ai('Dolphin-X1-ErrorAnalysis', error_log[:200], analysis)
                log_end("DolphinX1_ErrorAnalysis", start, True)
                
                return analysis
            
            log_end("DolphinX1_ErrorAnalysis", start, False, error="No JSON in response")
            return {}
            
        except Exception as e:
            log_error("DolphinX1_ErrorAnalysis", str(e))
            log_end("DolphinX1_ErrorAnalysis", start, False, error=str(e))
            return {}
    
    async def optimize_timing(self, success_data: List[Dict], failure_data: List[Dict]) -> Dict:
        """
        Analyze performance and optimize timing parameters
        """
        start = log_start("DolphinX1_TimingOptimization", 
                         successes=len(success_data), 
                         failures=len(failure_data))
        
        prompt = f"""Analyze these operation logs and optimize timing parameters.

SUCCESSFUL OPERATIONS ({len(success_data)}):
{json.dumps(success_data[:20], indent=2)}

FAILED OPERATIONS ({len(failure_data)}):
{json.dumps(failure_data[:20], indent=2)}

CURRENT TIMING PARAMETERS:
{{
    "video_watch_min": 15,
    "video_watch_max": 30,
    "scroll_delay_min": 1,
    "scroll_delay_max": 3,
    "typing_speed_base": 0.15,
    "action_delay_min": 2,
    "action_delay_max": 5
}}

Analyze patterns and recommend optimized parameters.
Respond with JSON containing optimized values and reasoning.

JSON Response:
"""
        
        try:
            process = await asyncio.create_subprocess_exec(
                'ollama', 'run', self.model,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(prompt.encode()),
                timeout=40.0
            )
            
            response = stdout.decode().strip()
            
            if '{' in response:
                json_str = response[response.find('{'):response.rfind('}')+1]
                recommendations = json.loads(json_str)
                
                log_ai('Dolphin-X1-TimingOpt', f"{len(success_data)} successes, {len(failure_data)} failures", recommendations)
                log_end("DolphinX1_TimingOptimization", start, True)
                
                return recommendations
            
            log_end("DolphinX1_TimingOptimization", start, False)
            return {}
            
        except Exception as e:
            log_error("DolphinX1_TimingOpt", str(e))
            log_end("DolphinX1_TimingOptimization", start, False, error=str(e))
            return {}
    
    async def generate_selector_alternatives(self, failed_selector: str, html_context: str) -> List[str]:
        """
        When selector fails, generate alternatives
        """
        start = log_start("DolphinX1_SelectorGen", failed=failed_selector)
        
        prompt = f"""Generate alternative selectors for this failed selector.

FAILED SELECTOR: {failed_selector}

HTML CONTEXT:
```html
{html_context[:2000]}
```

Generate 5 alternative selectors (mix of CSS and XPath) that could work.
Respond with JSON array: ["selector1", "selector2", ...]

JSON Response:
"""
        
        try:
            process = await asyncio.create_subprocess_exec(
                'ollama', 'run', self.model,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(prompt.encode()),
                timeout=20.0
            )
            
            response = stdout.decode().strip()
            
            if '[' in response:
                json_str = response[response.find('['):response.rfind(']')+1]
                selectors = json.loads(json_str)
                
                log_ai('Dolphin-X1-SelectorGen', failed_selector, selectors)
                log_end("DolphinX1_SelectorGen", start, True, alternatives=len(selectors))
                
                return selectors
            
            log_end("DolphinX1_SelectorGen", start, False)
            return []
            
        except Exception as e:
            log_error("DolphinX1_SelectorGen", str(e))
            log_end("DolphinX1_SelectorGen", start, False, error=str(e))
            return []


# Global instance
dolphin = DolphinX1Assistant()
