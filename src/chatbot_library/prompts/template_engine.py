"""
Template engine for rendering prompt templates with context and variables.
"""

import re
import json
from typing import Dict, List, Any, Optional, Union, Callable
from dataclasses import dataclass, field
from datetime import datetime

from .template_manager import PromptTemplate, ThinkingTemplate
from ..utils.logging import get_logger


@dataclass
class TemplateContext:
    """Context object containing variables and data for template rendering."""
    
    variables: Dict[str, Any] = field(default_factory=dict)
    conversation_data: Optional[Dict[str, Any]] = None
    user_data: Optional[Dict[str, Any]] = None
    system_data: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_variable(self, name: str, value: Any) -> None:
        """Add or update a template variable."""
        self.variables[name] = value
    
    def get_variable(self, name: str, default: Any = None) -> Any:
        """Get a template variable with optional default."""
        return self.variables.get(name, default)
    
    def merge_context(self, other: 'TemplateContext') -> 'TemplateContext':
        """Merge with another context, other takes precedence."""
        merged = TemplateContext(
            variables={**self.variables, **other.variables},
            conversation_data=other.conversation_data or self.conversation_data,
            user_data=other.user_data or self.user_data,
            system_data=other.system_data or self.system_data,
            metadata={**self.metadata, **other.metadata}
        )
        return merged
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary."""
        return {
            'variables': self.variables,
            'conversation_data': self.conversation_data,
            'user_data': self.user_data,
            'system_data': self.system_data,
            'metadata': self.metadata
        }


class TemplateEngine:
    """Engine for rendering prompt templates with variables and functions."""
    
    def __init__(self):
        self.logger = get_logger(self.__class__.__name__.lower())
        self.custom_functions: Dict[str, Callable] = {}
        self._register_builtin_functions()
    
    def _register_builtin_functions(self):
        """Register built-in template functions."""
        self.custom_functions.update({
            'now': lambda: datetime.now().isoformat(),
            'today': lambda: datetime.now().strftime('%Y-%m-%d'),
            'time': lambda: datetime.now().strftime('%H:%M:%S'),
            'upper': lambda text: str(text).upper(),
            'lower': lambda text: str(text).lower(),
            'title': lambda text: str(text).title(),
            'len': lambda obj: len(obj) if hasattr(obj, '__len__') else 0,
            'join': lambda items, sep=', ': sep.join(str(item) for item in items),
            'truncate': lambda text, length=100: str(text)[:length] + '...' if len(str(text)) > length else str(text),
            'default': lambda value, default_val: default_val if value is None or value == '' else value,
            'format_list': self._format_list,
            'format_dict': self._format_dict,
            'conditional': self._conditional
        })
    
    def _format_list(self, items: List[Any], format_type: str = 'bullet') -> str:
        """Format a list into a string."""
        if not items:
            return ""
        
        if format_type == 'bullet':
            return '\n'.join(f"• {item}" for item in items)
        elif format_type == 'numbered':
            return '\n'.join(f"{i+1}. {item}" for i, item in enumerate(items))
        elif format_type == 'comma':
            return ', '.join(str(item) for item in items)
        else:
            return '\n'.join(str(item) for item in items)
    
    def _format_dict(self, data: Dict[str, Any], format_type: str = 'key_value') -> str:
        """Format a dictionary into a string."""
        if not data:
            return ""
        
        if format_type == 'key_value':
            return '\n'.join(f"{key}: {value}" for key, value in data.items())
        elif format_type == 'json':
            return json.dumps(data, indent=2)
        else:
            return str(data)
    
    def _conditional(self, condition: Any, true_value: Any, false_value: Any = '') -> Any:
        """Conditional function for templates."""
        return true_value if condition else false_value
    
    def register_function(self, name: str, func: Callable) -> None:
        """Register a custom template function."""
        self.custom_functions[name] = func
        self.logger.debug(f"Registered template function: {name}")
    
    def render_template(
        self, 
        template: Union[PromptTemplate, str], 
        context: Optional[TemplateContext] = None
    ) -> str:
        """Render a template with the given context."""
        if isinstance(template, PromptTemplate):
            template_str = template.template
        else:
            template_str = template
        
        if context is None:
            context = TemplateContext()
        
        # Create a combined context with all available data
        render_context = {
            **context.variables,
            **self.custom_functions
        }
        
        # Add conversation data if available
        if context.conversation_data:
            render_context['conversation'] = context.conversation_data
        
        if context.user_data:
            render_context['user'] = context.user_data
        
        if context.system_data:
            render_context['system'] = context.system_data
        
        # Render the template
        try:
            rendered = self._process_template(template_str, render_context)
            self.logger.debug("Template rendered successfully")
            return rendered
        except Exception as e:
            self.logger.error(f"Template rendering failed: {e}")
            return template_str  # Return original template on error
    
    def _process_template(self, template: str, context: Dict[str, Any]) -> str:
        """Process template with variable substitution and function calls."""
        # Handle simple variable substitution: {variable}
        template = self._substitute_variables(template, context)
        
        # Handle function calls: {function(args)}
        template = self._process_functions(template, context)
        
        # Handle conditional blocks: {if condition}...{endif}
        template = self._process_conditionals(template, context)
        
        # Handle loops: {for item in items}...{endfor}
        template = self._process_loops(template, context)
        
        return template
    
    def _substitute_variables(self, template: str, context: Dict[str, Any]) -> str:
        """Substitute simple variables in template."""
        # Pattern for {variable} or {object.property}
        pattern = r'\{([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)\}'
        
        def replace_var(match):
            var_path = match.group(1)
            try:
                value = self._get_nested_value(context, var_path)
                return str(value) if value is not None else match.group(0)
            except (KeyError, AttributeError, TypeError):
                return match.group(0)  # Keep original if variable not found
        
        return re.sub(pattern, replace_var, template)
    
    def _get_nested_value(self, obj: Any, path: str) -> Any:
        """Get nested value from object using dot notation."""
        parts = path.split('.')
        current = obj
        
        for part in parts:
            if isinstance(current, dict):
                current = current[part]
            else:
                current = getattr(current, part)
        
        return current
    
    def _process_functions(self, template: str, context: Dict[str, Any]) -> str:
        """Process function calls in template."""
        # Pattern for {function(args)}
        pattern = r'\{([a-zA-Z_][a-zA-Z0-9_]*)\(([^}]*)\)\}'
        
        def replace_func(match):
            func_name = match.group(1)
            args_str = match.group(2)
            
            if func_name not in self.custom_functions:
                return match.group(0)
            
            try:
                # Parse arguments (simplified - supports strings, numbers, variables)
                args = self._parse_function_args(args_str, context)
                result = self.custom_functions[func_name](*args)
                return str(result) if result is not None else ''
            except Exception as e:
                self.logger.warning(f"Function {func_name} failed: {e}")
                return match.group(0)
        
        return re.sub(pattern, replace_func, template)
    
    def _parse_function_args(self, args_str: str, context: Dict[str, Any]) -> List[Any]:
        """Parse function arguments from string."""
        if not args_str.strip():
            return []
        
        args = []
        # Simple parsing - split by comma, handle quoted strings and variables
        parts = [part.strip() for part in args_str.split(',')]
        
        for part in parts:
            if not part:
                continue
            
            # String literal
            if (part.startswith('"') and part.endswith('"')) or (part.startswith("'") and part.endswith("'")):
                args.append(part[1:-1])
            # Number
            elif part.isdigit() or (part.replace('.', '').isdigit() and part.count('.') <= 1):
                args.append(float(part) if '.' in part else int(part))
            # Boolean
            elif part.lower() in ('true', 'false'):
                args.append(part.lower() == 'true')
            # Variable
            else:
                try:
                    value = self._get_nested_value(context, part)
                    args.append(value)
                except:
                    args.append(part)  # Use as string if variable not found
        
        return args
    
    def _process_conditionals(self, template: str, context: Dict[str, Any]) -> str:
        """Process conditional blocks in template."""
        # Pattern for {if condition}...{endif}
        pattern = r'\{if\s+([^}]+)\}(.*?)\{endif\}'
        
        def replace_conditional(match):
            condition_str = match.group(1).strip()
            content = match.group(2)
            
            try:
                # Evaluate condition (simplified)
                condition = self._evaluate_condition(condition_str, context)
                return content if condition else ''
            except Exception as e:
                self.logger.warning(f"Conditional evaluation failed: {e}")
                return match.group(0)
        
        return re.sub(pattern, replace_conditional, template, flags=re.DOTALL)
    
    def _process_loops(self, template: str, context: Dict[str, Any]) -> str:
        """Process loop blocks in template."""
        # Pattern for {for item in items}...{endfor}
        pattern = r'\{for\s+(\w+)\s+in\s+(\w+)\}(.*?)\{endfor\}'
        
        def replace_loop(match):
            item_var = match.group(1)
            collection_var = match.group(2)
            content = match.group(3)
            
            try:
                collection = context.get(collection_var, [])
                if not isinstance(collection, (list, tuple)):
                    return ''
                
                results = []
                for item in collection:
                    # Create new context with loop variable
                    loop_context = {**context, item_var: item}
                    rendered_content = self._process_template(content, loop_context)
                    results.append(rendered_content)
                
                return ''.join(results)
            except Exception as e:
                self.logger.warning(f"Loop processing failed: {e}")
                return match.group(0)
        
        return re.sub(pattern, replace_loop, template, flags=re.DOTALL)
    
    def _evaluate_condition(self, condition_str: str, context: Dict[str, Any]) -> bool:
        """Evaluate a simple condition string."""
        # Simple condition evaluation (supports basic comparisons)
        condition_str = condition_str.strip()
        
        # Handle simple variable existence
        if condition_str in context:
            value = context[condition_str]
            return bool(value)
        
        # Handle simple comparisons (variable == value, variable != value, etc.)
        for op in ['==', '!=', '>', '<', '>=', '<=']:
            if op in condition_str:
                left, right = condition_str.split(op, 1)
                left_val = self._get_condition_value(left.strip(), context)
                right_val = self._get_condition_value(right.strip(), context)
                
                if op == '==':
                    return left_val == right_val
                elif op == '!=':
                    return left_val != right_val
                elif op == '>':
                    return left_val > right_val
                elif op == '<':
                    return left_val < right_val
                elif op == '>=':
                    return left_val >= right_val
                elif op == '<=':
                    return left_val <= right_val
        
        return False
    
    def _get_condition_value(self, value_str: str, context: Dict[str, Any]) -> Any:
        """Get value for condition evaluation."""
        value_str = value_str.strip()
        
        # String literal
        if (value_str.startswith('"') and value_str.endswith('"')) or (value_str.startswith("'") and value_str.endswith("'")):
            return value_str[1:-1]
        
        # Number
        if value_str.isdigit() or (value_str.replace('.', '').isdigit() and value_str.count('.') <= 1):
            return float(value_str) if '.' in value_str else int(value_str)
        
        # Boolean
        if value_str.lower() in ('true', 'false'):
            return value_str.lower() == 'true'
        
        # Variable
        return context.get(value_str, value_str)
    
    def validate_template(self, template: Union[PromptTemplate, str]) -> List[str]:
        """Validate template syntax and return any errors."""
        errors = []
        
        template_str = template.template if isinstance(template, PromptTemplate) else template
        
        # Check for unmatched braces
        open_braces = template_str.count('{')
        close_braces = template_str.count('}')
        if open_braces != close_braces:
            errors.append(f"Unmatched braces: {open_braces} opening, {close_braces} closing")
        
        # Check for unmatched conditional blocks
        if_count = len(re.findall(r'\{if\s+[^}]+\}', template_str))
        endif_count = len(re.findall(r'\{endif\}', template_str))
        if if_count != endif_count:
            errors.append(f"Unmatched if/endif blocks: {if_count} if, {endif_count} endif")
        
        # Check for unmatched loop blocks
        for_count = len(re.findall(r'\{for\s+\w+\s+in\s+\w+\}', template_str))
        endfor_count = len(re.findall(r'\{endfor\}', template_str))
        if for_count != endfor_count:
            errors.append(f"Unmatched for/endfor blocks: {for_count} for, {endfor_count} endfor")
        
        return errors
    
    def get_template_variables(self, template: Union[PromptTemplate, str]) -> List[str]:
        """Extract all variables used in a template."""
        template_str = template.template if isinstance(template, PromptTemplate) else template
        
        # Find variable references
        variables = set()
        
        # Simple variables: {variable}
        simple_vars = re.findall(r'\{([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)\}', template_str)
        variables.update(var.split('.')[0] for var in simple_vars)
        
        # Function arguments that are variables
        func_calls = re.findall(r'\{[a-zA-Z_][a-zA-Z0-9_]*\(([^}]*)\)\}', template_str)
        for args_str in func_calls:
            args = [arg.strip() for arg in args_str.split(',')]
            for arg in args:
                if arg and not (arg.startswith('"') or arg.startswith("'") or arg.isdigit() or arg.lower() in ('true', 'false')):
                    variables.add(arg.split('.')[0])
        
        # Loop variables
        loop_vars = re.findall(r'\{for\s+\w+\s+in\s+(\w+)\}', template_str)
        variables.update(loop_vars)
        
        # Conditional variables
        condition_vars = re.findall(r'\{if\s+([^}]+)\}', template_str)
        for condition in condition_vars:
            # Extract variable names from conditions
            words = re.findall(r'[a-zA-Z_][a-zA-Z0-9_]*', condition)
            variables.update(words)
        
        return sorted(list(variables))
    
    def render_thinking_prompt(
        self, 
        thinking_template: ThinkingTemplate, 
        base_prompt: str = "",
        context: Optional[TemplateContext] = None
    ) -> str:
        """Render a thinking mode prompt."""
        thinking_prompt = thinking_template.to_thinking_prompt()
        
        if base_prompt:
            combined_prompt = f"{thinking_prompt}\n\n{base_prompt}"
        else:
            combined_prompt = thinking_prompt
        
        # Apply any context variables
        if context:
            combined_prompt = self.render_template(combined_prompt, context)
        
        return combined_prompt