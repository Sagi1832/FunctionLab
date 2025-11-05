from typing import Dict, Any


def drop_outer_ranges(mono_map: Dict[Any, Any]) -> Dict[Any, Any]:
    """Remove the first and last entries from an ordered mapping."""
    if len(mono_map) < 3:
        return mono_map   
    items = list(mono_map.items())  
    trimmed_items = items[1:-1]
    
    return dict(trimmed_items)


def is_empty_or_trivial(mono_map: Dict[Any, Any]) -> bool:
    """Check if there's nothing meaningful to show after trimming."""
    return len(mono_map) <= 2
