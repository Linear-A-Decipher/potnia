import re
from typing import Tuple, List
from .data import read_data


class Mapper:
    syllabograms:Tuple[str] = []
    logograms:Tuple[str] = []
    
    def __init__(self):
        self.syllabograms_dict = read_data(*self.syllabograms)
        self.logograms_dict = read_data(*self.syllabograms)
        self.unicode_to_transliteration_dict = read_data(*self.syllabograms, *self.logograms)
        self.transliteration_to_unicode_dict = {v: k for k, v in self.unicode_to_transliteration_dict.items()}

    def tokenize_linear_b(self, text:str) -> List[str]:
        """
        Tokenizes Linear B text into individual elements, including words, special characters, and preserving spaces.
        
        Parameters:
        text (str): A string containing Linear B text to be tokenized.
        
        Returns:
        list: A list of tokens extracted from the text.
        """
        # Normalize spaces and remove specific patterns
        text = text.replace('\u00a0', ' ').replace('\u0323', '')
        
        # List of patterns and their replacements
        patterns = [
            (r'(?<=\S)\?', ' ?'),  # Ensure '?' is separated when it follows a character
            (r'\b({})\s([mf])\b'.format('|'.join(['BOS', 'SUS', 'OVIS', 'CAP', 'EQU'])), r'\1\2'),  # Combine terms with 'm' or 'f'
            (r'\](?=[^\s])', r']-'),  # Pre-process ']' and '[' for special handling
            (r'(?<=[^\s])\[', r'-['),
            (r'\* (\d+)', r'*\1'),  # Combine '*' with the following numeral
            (r'\+ ([^\s]+)', r'+\1'),  # Combine '+' with surrounding ideograms
            (r'([^\s]) \+', r'\1+'),  # Ensure '+' is properly attached
            (r'([^\s]+) VAS', r'\1VAS'),  # Attach 'VAS' properly
            # Ignore or modify specific patterns
            *[(rf'\b{term}\s?\.', term + '.') for term in ['vac', 'vest', 'l', 's', 'lat', 'inf', 'mut', 'sup', 'i']],  # Refactored for brevity
        ]

        # Apply each pattern replacement in order
        for pattern, replacement in patterns:
            text = re.sub(pattern, replacement, text)

        # Space handling
        space_placeholder = "\uE000"  # Placeholder for spaces
        text = re.sub(r' ', space_placeholder, text)

        # Tokenize based on special characters and space placeholder
        special_chars_pattern = r'(\[|\]|\,|\'|\u27e6|\u27e7|-|' + re.escape(space_placeholder) + ')'
        tokens = re.split(special_chars_pattern, text)

        # Replace placeholder with actual space and filter empty tokens
        tokenized = [tok if tok != space_placeholder else " " for tok in tokens if tok and tok!="-"]

        return tokenized if tokenized else [""]

    def tokenize_unicode(self, text:str) -> List[str]:
        words = ['-'.join(word) for word in text.split()]
        text = ' '.join(words)

        return list(text)

    def tokenize_transliteration(self, text:str) -> List[str]:
        return re.findall(r'[^\s-]+|\s+', text)

    def to_transliteration(self, text:str) -> str:
        return "".join([self.unicode_to_transliteration_dict.get(token, token) for token in self.tokenize_unicode(text)])

    def to_unicode(self, text:str) -> str:
        return "".join([self.transliteration_to_unicode_dict.get(token, token) for token in self.tokenize_transliteration(text)])

    def __call__(self, text:str) -> str:
        return self.to_unicode(text)