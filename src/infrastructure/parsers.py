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
        # Finds the first list of dictionaries anywhere in the JSON tree
        def find_list(data):
            if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
                return data
            if isinstance(data, dict):
                for key, value in data.items():
                    result = find_list(value)
                    if result: return result
            return []

        items = find_list(raw_json)
        
        # Fallback if absolutely nothing found, try to treat root as 1 item
        if not items and isinstance(raw_json, dict):
            items = [raw_json]

        results = []
        for i in items:
            # Normalize keys
            i_low = {k.lower(): v for k, v in i.items() if isinstance(v, (str, int, float, bool))}
            
            # Skip empty/wrapper objects
            if not i_low: continue

            # Amount Logic
            amt = float(i_low.get("amount", i_low.get("value", 0)))
            r_type = i_low.get("type", "Unknown")
            category = i_low.get("category", i_low.get("account", "Uncategorized"))
            
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
                category=category,
                type=r_type,
                raw_data=json.dumps(i)
            ))
        return results

class RootfiParser(QuickBooksParser):
    # Reuse the smart logic above, it handles both structures now
    pass

class ParserFactory:
    @staticmethod
    def get_parser(source: str) -> ParserStrategy:
        # Return the smart parser for both
        return QuickBooksParser()