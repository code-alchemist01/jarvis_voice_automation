"""
Multi-step task processor for handling complex commands
"""
import json
from core.llm_client import LLMClient
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.command_processor import CommandProcessor


class MultiStepProcessor:
    """Process multi-step tasks using LLM for task planning"""
    
    def __init__(self, command_processor):
        self.command_processor = command_processor
        self.llm_client = LLMClient()
    
    def parse_multi_step_command(self, text):
        """Parse a multi-step command into task list"""
        try:
            if not self.llm_client.is_available():
                return None, "LLM kullanılamıyor. Çok adımlı görevler için LLM gerekli."
            
            prompt = f"""Kullanıcının komutunu analiz et ve görev listesine ayır.

Komut: "{text}"

Görevleri JSON formatında döndür:
{{
  "tasks": [
    {{
      "action": "komut_tipi",
      "target": "hedef",
      "parameters": {{}},
      "order": 1,
      "depends_on": []
    }}
  ]
}}

Örnekler:
- "Önce Notepad'i aç, sonra Calculator'ı aç" → 
  {{
    "tasks": [
      {{"action": "open_app", "target": "notepad", "order": 1, "depends_on": []}},
      {{"action": "open_app", "target": "calculator", "order": 2, "depends_on": [1]}}
    ]
  }}

- "Ses seviyesini artır ve ekran görüntüsü al" →
  {{
    "tasks": [
      {{"action": "volume_up", "target": "", "order": 1, "depends_on": []}},
      {{"action": "screenshot", "target": "", "order": 2, "depends_on": []}}
    ]
  }}

Sadece JSON döndür, başka açıklama yapma."""

            # Use LLM client's chat method
            messages = [
                {"role": "system", "content": "Sen bir görev planlama asistanısın. Kullanıcı komutlarını görev listesine ayırırsın."},
                {"role": "user", "content": prompt}
            ]
            
            success, content = self.llm_client.chat(messages)
            if not success:
                return None, content
            
            content = content.strip()
            
            # Try to extract JSON from response
            if '```json' in content:
                content = content.split('```json')[1].split('```')[0].strip()
            elif '```' in content:
                content = content.split('```')[1].split('```')[0].strip()
            
            try:
                task_plan = json.loads(content)
                return task_plan, None
            except json.JSONDecodeError:
                # Try to find JSON in the response
                import re
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    try:
                        task_plan = json.loads(json_match.group(0))
                        return task_plan, None
                    except:
                        pass
                return None, "Görev planı JSON formatında parse edilemedi"
        except Exception as e:
            print(f"Error parsing multi-step command: {e}")
            return None, f"Görev planlanırken hata oluştu: {str(e)}"
    
    def execute_task_plan(self, task_plan):
        """Execute a task plan"""
        try:
            tasks = task_plan.get('tasks', [])
            if not tasks:
                return False, "Görev bulunamadı"
            
            # Sort tasks by order
            tasks = sorted(tasks, key=lambda x: x.get('order', 0))
            
            results = []
            for task in tasks:
                action = task.get('action', '')
                target = task.get('target', '')
                parameters = task.get('parameters', {})
                
                # Check dependencies
                depends_on = task.get('depends_on', [])
                for dep in depends_on:
                    if dep < len(results):
                        if not results[dep - 1][0]:  # Previous task failed
                            return False, f"Bağımlı görev başarısız oldu: {task}"
                
                # Execute task
                # Map action to command
                command_text = self._task_to_command(action, target, parameters)
                success, message = self.command_processor.process_command(command_text, 'tr')
                
                results.append((success, message))
                
                if not success:
                    return False, f"Görev başarısız: {action} - {message}"
            
            return True, "Tüm görevler başarıyla tamamlandı"
        except Exception as e:
            print(f"Error executing task plan: {e}")
            return False, f"Görevler çalıştırılırken hata oluştu: {str(e)}"
    
    def _task_to_command(self, action, target, parameters):
        """Convert task to command text"""
        action_map = {
            'open_app': f"{target}'ı aç" if target else "uygulama aç",
            'volume_up': "ses seviyesini artır",
            'volume_down': "ses seviyesini azalt",
            'screenshot': "ekran görüntüsü al",
            'play_media': "müziği çal",
            'pause_media': "müziği durdur",
            'next_track': "sonraki şarkı",
            'previous_track': "önceki şarkı",
        }
        
        command = action_map.get(action, action)
        if target and action not in action_map:
            command = f"{command} {target}"
        
        return command
    
    def process_multi_step(self, text):
        """Process a multi-step command"""
        # Check if it's a multi-step command
        multi_step_keywords = ['önce', 'sonra', 've', 'ile', 'ardından', 'daha sonra']
        is_multi_step = any(keyword in text.lower() for keyword in multi_step_keywords)
        
        if not is_multi_step:
            return None, None  # Not a multi-step command
        
        # Parse and execute
        task_plan, error = self.parse_multi_step_command(text)
        if error:
            return False, error
        
        return self.execute_task_plan(task_plan)

