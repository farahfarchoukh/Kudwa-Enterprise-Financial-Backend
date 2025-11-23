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
        candidates = []
        def find_lists(data):
            if isinstance(data, list):
                if len(data) > 0 and isinstance(data[0], dict):
                    candidates.append(data)
                for item in data:
                    if isinstance(item, (dict, list)):
                        find_lists(item)
            elif isinstance(data, dict):
                for key, value in data.items():
                    find_lists(value)

        find_lists(raw_json)
        
        # Flatten all found lists into one big stream of potential data
        all_items = [item for sublist in candidates for item in sublist]
        
        if not all_items and isinstance(raw_json, dict):
            all_items = [raw_json]

        results = []
        for i in all_items:
            if not isinstance(i, dict): continue
            
            i_low = {k.lower(): v for k, v in i.items() if isinstance(v, (str, int, float))}
            
            # --- THE FIX: STRICT FILTERING ---
            # 1. Extract Amount
            try:
                val_str = i_low.get("amount", i_low.get("value", "0"))
                if val_str == "": val_str = "0"
                amt = float(val_str)
            except (ValueError, TypeError):
                continue # Skip text rows like "Total Income"

            # 2. DISCARD ZEROS
            # This prevents empty cells from polluting the DB
            if abs(amt) < 0.01:
                continue

            # 3. Determine Type
            r_type = i_low.get("type", "Unknown")
            # Heuristic: if category implies expense, flip sign
            # (In P&L reports, headers aren't always available per row in this flattening strategy)
            
            # 4. Date Parsing (Defaulting to Q1 2024 for the demo)
            date_str = i_low.get("date", i_low.get("timestamp", "2024-01-15"))
            try:
                dt = datetime.strptime(date_str, "%Y-%m-%d").date()
            except:
                dt = datetime(2024, 1, 15).date()

            results.append(TransactionDTO(
                date=dt,
                description=i_low.get("description", i_low.get("memo", "Financial Entry")),
                amount=amt,
                category=i_low.get("category", "Uncategorized"),
                type=r_type,
                raw_data=json.dumps(i)
            ))
        return results