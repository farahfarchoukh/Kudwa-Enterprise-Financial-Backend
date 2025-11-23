import json
from abc import ABC, abstractmethod
from typing import List, Any
from datetime import datetime
from src.domain.schemas import TransactionDTO

class ParserStrategy(ABC):
    @abstractmethod
    def parse(self, content: bytes) -> List[TransactionDTO]:
        pass

class QuickBooksParser(ParserStrategy):
    def parse(self, content: bytes) -> List[TransactionDTO]:
        try:
            raw_json = json.loads(content)
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON file")

        # --- RECURSIVE DEEP SEARCH ---
        # This function hunts for the largest list of objects in the file
        # ignoring metadata wrappers like "Header" or "Meta"
        candidates = []
        
        def find_lists(data):
            if isinstance(data, list):
                # If we found a list of dicts, it's a candidate
                if len(data) > 0 and isinstance(data[0], dict):
                    candidates.append(data)
                for item in data:
                    if isinstance(item, (dict, list)):
                        find_lists(item)
            elif isinstance(data, dict):
                for key, value in data.items():
                    find_lists(value)

        find_lists(raw_json)
        
        # Pick the longest list found (most likely the transactions)
        items = max(candidates, key=len) if candidates else []
        
        # Fallback: if no list found, maybe the root dict is the item
        if not items and isinstance(raw_json, dict):
            items = [raw_json]

        results = []
        for i in items:
            if not isinstance(i, dict): continue
            
            # Normalize keys
            i_low = {k.lower(): v for k, v in i.items() if isinstance(v, (str, int, float))}
            
            # Validation: Must have at least an amount or description to be valid
            if not i_low: continue

            # Robust Float Conversion
            try:
                val_str = i_low.get("amount", i_low.get("value", 0))
                amt = float(val_str)
            except (ValueError, TypeError):
                continue # Skip metadata rows (like "GAAP")

            r_type = i_low.get("type", "Unknown")
            
            # Flip sign for expenses
            if "expense" in r_type.lower() and amt > 0:
                amt = -amt

            # Date Parsing
            date_str = i_low.get("date", i_low.get("timestamp", "2024-01-01"))
            try:
                dt = datetime.strptime(date_str, "%Y-%m-%d").date()
            except:
                dt = datetime.now().date()

            results.append(TransactionDTO(
                date=dt,
                description=i_low.get("description", i_low.get("memo", "Unknown")),
                amount=amt,
                category=i_low.get("category", i_low.get("account", "Uncategorized")),
                type=r_type,
                raw_data=json.dumps(i)
            ))
        return results

class RootfiParser(QuickBooksParser):
    pass

class ParserFactory:
    @staticmethod
    def get_parser(source: str) -> ParserStrategy:
        return QuickBooksParser()