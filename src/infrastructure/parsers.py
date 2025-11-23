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

        # Smart Heuristic: Find the list!
        items = []
        if isinstance(raw_json, list):
            items = raw_json
        elif isinstance(raw_json, dict):
            # Look for the first key that contains a list (common in JSON exports)
            for key, value in raw_json.items():
                if isinstance(value, list) and len(value) > 0:
                    items = value
                    break
            # If no list found, maybe the dict itself is one record?
            if not items:
                items = [raw_json]

        results = []
        for i in items:
            if not isinstance(i, dict): continue # Skip weird data
            
            # Normalize keys to lowercase
            i_low = {k.lower(): v for k, v in i.items()}
            
            # Extract fields with fallbacks
            amt = float(i_low.get("amount", i_low.get("value", 0)))
            r_type = i_low.get("type", "Unknown")
            
            # Flip sign for expenses if positive
            if "expense" in r_type.lower() and amt > 0:
                amt = -amt

            # Date parsing (try multiple formats)
            date_str = i_low.get("date", i_low.get("timestamp", "2024-01-01"))
            try:
                dt = datetime.strptime(date_str, "%Y-%m-%d").date()
            except:
                dt = datetime.now().date() # Fallback

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
    # Reuse the smart logic above, it handles both structures now
    pass

class ParserFactory:
    @staticmethod
    def get_parser(source: str) -> ParserStrategy:
        # Return the smart parser for both
        return QuickBooksParser()