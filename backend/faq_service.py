# faq_service.py

import json
from pathlib import Path
import re
from typing import List, Dict, Optional

class FAQService:
    """
    A service to load and search through the FAQ dataset.
    """
    def __init__(self, faqs_path: str = "data/faqs.json"):
        """
        Initializes the FAQService by loading the FAQ data from a JSON file.

        Args:
            faqs_path: The file path to the FAQs JSON file.
        """
        self.faqs = self._load_faqs(faqs_path)
        # Simple set of common English stopwords.
        self.stopwords = set([
            "i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your",
            "he", "him", "his", "she", "her", "it", "its", "they", "them", "their",
            "what", "which", "who", "whom", "this", "that", "these", "those", "am",
            "is", "are", "was", "were", "be", "been", "a", "an", "the", "and", "but",
            "if", "or", "because", "as", "until", "while", "of", "at", "by", "for",
            "with", "about", "to", "from", "in", "out", "on", "off", "how", "do"
        ])

    def _load_faqs(self, faqs_path: str) -> List[Dict]:
        """Loads FAQs from the specified JSON file."""
        try:
            path = Path(faqs_path)
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data.get("faqs", [])
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading FAQs: {e}")
            return []

    def _preprocess_text(self, text: str) -> set:
        """
        Preprocesses text for searching by:
        1. Converting to lowercase.
        2. Removing punctuation.
        3. Splitting into words (tokenizing).
        4. Removing stopwords.
        """
        text = text.lower()
        text = re.sub(r'[^\w\s]', '', text)
        words = set(text.split())
        return words - self.stopwords

    def search_faqs(self, query: str, top_k: int = 2, min_score: int = 1) -> Optional[str]:
        """
        Searches FAQs using a simple keyword matching algorithm.

        Args:
            query: The user's search query.
            top_k: The number of top matching FAQs to return.
            min_score: The minimum score for an FAQ to be considered a match.

        Returns:
            A formatted string of the best matching FAQs or None if no match is found.
        """
        if not self.faqs:
            return None

        query_words = self._preprocess_text(query)
        scored_faqs = []

        for faq in self.faqs:
            question_words = self._preprocess_text(faq["question"])
            # Score is the number of overlapping words
            score = len(query_words.intersection(question_words))
            if score >= min_score:
                scored_faqs.append({"faq": faq, "score": score})

        if not scored_faqs:
            return None

        # Sort by score in descending order
        scored_faqs.sort(key=lambda x: x["score"], reverse=True)

        # Get the top_k results
        top_faqs = scored_faqs[:top_k]

        # Format the context string
        context = "\n".join([
            f"Q: {item['faq']['question']}\nA: {item['faq']['answer']}"
            for item in top_faqs
        ])

        return context

# Create a single instance to be used across the application
faq_service = FAQService()
