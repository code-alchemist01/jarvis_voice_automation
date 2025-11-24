"""
Calculator features
"""
import re
import math


def calculate(expression):
    """Calculate a mathematical expression"""
    try:
        # Clean the expression
        expression = expression.lower()
        
        # Replace Turkish words with operators
        replacements = {
            'artı': '+',
            'eksi': '-',
            'çarpı': '*',
            'bölü': '/',
            'kere': '*',
            'plus': '+',
            'minus': '-',
            'times': '*',
            'multiply': '*',
            'divided by': '/',
            'divide': '/',
            'kaç': '',
            'edir': '',
            'eder': '',
            'eşittir': '',
            'equals': '',
            'is': '',
            'what is': '',
            'ne': '',
            'kaçtır': '',
            ' ': ''
        }
        
        for turkish, operator in replacements.items():
            expression = expression.replace(turkish, operator)
        
        # Extract numbers and operators
        # Simple pattern matching for basic operations
        patterns = [
            (r'(\d+)\+(\d+)', lambda m: str(int(m.group(1)) + int(m.group(2)))),
            (r'(\d+)-(\d+)', lambda m: str(int(m.group(1)) - int(m.group(2)))),
            (r'(\d+)\*(\d+)', lambda m: str(int(m.group(1)) * int(m.group(2)))),
            (r'(\d+)/(\d+)', lambda m: str(int(m.group(1)) / int(m.group(2)))),
        ]
        
        # Try to evaluate directly if it's a valid Python expression
        # Remove any non-numeric, non-operator characters
        clean_expr = re.sub(r'[^0-9+\-*/().]', '', expression)
        
        if clean_expr:
            try:
                # Use eval with limited scope for safety
                result = eval(clean_expr, {"__builtins__": {}, "math": math}, {})
                return True, f"Sonuç: {result}"
            except:
                pass
        
        # Try pattern matching
        for pattern, func in patterns:
            match = re.search(pattern, expression)
            if match:
                result = func(match)
                return True, f"Sonuç: {result}"
        
        return False, "Hesaplama yapılamadı. Lütfen daha basit bir ifade deneyin."
    
    except Exception as e:
        return False, f"Hata: {str(e)}"


def simple_calculate(text):
    """Simple calculator that extracts numbers and operations from natural language"""
    try:
        # Extract numbers
        numbers = re.findall(r'\d+', text)
        if len(numbers) < 2:
            return False, "En az iki sayı gerekiyor"
        
        num1 = int(numbers[0])
        num2 = int(numbers[1])
        
        # Determine operation
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['artı', 'plus', 'topla', 'add']):
            result = num1 + num2
            return True, f"{num1} artı {num2} eşittir {result}"
        elif any(word in text_lower for word in ['eksi', 'minus', 'çıkar', 'subtract']):
            result = num1 - num2
            return True, f"{num1} eksi {num2} eşittir {result}"
        elif any(word in text_lower for word in ['çarpı', 'kere', 'times', 'multiply', 'çarp']):
            result = num1 * num2
            return True, f"{num1} çarpı {num2} eşittir {result}"
        elif any(word in text_lower for word in ['bölü', 'divide', 'böl']):
            if num2 == 0:
                return False, "Sıfıra bölme yapılamaz"
            result = num1 / num2
            return True, f"{num1} bölü {num2} eşittir {result}"
        else:
            # Default to addition
            result = num1 + num2
            return True, f"{num1} artı {num2} eşittir {result}"
    
    except Exception as e:
        return False, f"Hata: {str(e)}"

