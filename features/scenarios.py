"""
Scenario management for predefined task sequences
"""
import json
from pathlib import Path
from datetime import datetime
from core.multi_step_processor import MultiStepProcessor
from core.command_processor import CommandProcessor
from utils.config import config

SCENARIOS_FILE = Path(__file__).parent.parent / "scenarios.json"


def load_scenarios():
    """Load scenarios from file"""
    try:
        if SCENARIOS_FILE.exists():
            with open(SCENARIOS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    except Exception as e:
        print(f"Error loading scenarios: {e}")
        return {}


def save_scenarios(scenarios):
    """Save scenarios to file"""
    try:
        with open(SCENARIOS_FILE, 'w', encoding='utf-8') as f:
            json.dump(scenarios, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving scenarios: {e}")


def create_scenario(name, tasks):
    """Create a new scenario"""
    try:
        scenarios = load_scenarios()
        scenarios[name.lower()] = {
            'name': name,
            'tasks': tasks,
            'created_at': datetime.now().isoformat()
        }
        save_scenarios(scenarios)
        return True, f"Senaryo oluşturuldu: {name}"
    except Exception as e:
        print(f"Error creating scenario: {e}")
        return False, f"Senaryo oluşturulurken hata oluştu: {str(e)}"


def run_scenario(name, command_processor=None):
    """Run a saved scenario"""
    try:
        scenarios = load_scenarios()
        scenario = scenarios.get(name.lower())
        
        if not scenario:
            return False, f"'{name}' adında senaryo bulunamadı"
        
        if not command_processor:
            from core.command_processor import CommandProcessor
            command_processor = CommandProcessor()
        
        multi_processor = MultiStepProcessor(command_processor)
        
        # Convert scenario tasks to task plan format
        task_plan = {
            'tasks': scenario['tasks']
        }
        
        success, message = multi_processor.execute_task_plan(task_plan)
        
        if success:
            return True, f"Senaryo çalıştırıldı: {name}"
        else:
            return False, f"Senaryo çalıştırılırken hata: {message}"
    except Exception as e:
        print(f"Error running scenario: {e}")
        return False, f"Senaryo çalıştırılırken hata oluştu: {str(e)}"


def list_scenarios():
    """List all saved scenarios"""
    try:
        scenarios = load_scenarios()
        
        if not scenarios:
            return True, "Kayıtlı senaryo bulunamadı"
        
        result = "Kayıtlı senaryolar:\n"
        for name, scenario in scenarios.items():
            task_count = len(scenario.get('tasks', []))
            result += f"- {scenario['name']} ({task_count} görev)\n"
        
        return True, result
    except Exception as e:
        print(f"Error listing scenarios: {e}")
        return False, f"Senaryolar listelenirken hata oluştu: {str(e)}"


def delete_scenario(name):
    """Delete a scenario"""
    try:
        scenarios = load_scenarios()
        
        if name.lower() not in scenarios:
            return False, f"'{name}' adında senaryo bulunamadı"
        
        del scenarios[name.lower()]
        save_scenarios(scenarios)
        
        return True, f"Senaryo silindi: {name}"
    except Exception as e:
        print(f"Error deleting scenario: {e}")
        return False, f"Senaryo silinirken hata oluştu: {str(e)}"


# Predefined scenarios
PREDEFINED_SCENARIOS = {
    'çalışma modu': {
        'name': 'Çalışma Modu',
        'tasks': [
            {'action': 'open_app', 'target': 'notepad', 'order': 1, 'depends_on': []},
            {'action': 'volume_down', 'target': '', 'order': 2, 'depends_on': []},
        ]
    },
    'uyku modu': {
        'name': 'Uyku Modu',
        'tasks': [
            {'action': 'pause_media', 'target': '', 'order': 1, 'depends_on': []},
            {'action': 'volume_down', 'target': '', 'order': 2, 'depends_on': []},
        ]
    },
}


def initialize_predefined_scenarios():
    """Initialize predefined scenarios if they don't exist"""
    try:
        scenarios = load_scenarios()
        for key, scenario in PREDEFINED_SCENARIOS.items():
            if key not in scenarios:
                scenarios[key] = scenario
        save_scenarios(scenarios)
    except Exception as e:
        print(f"Error initializing predefined scenarios: {e}")

