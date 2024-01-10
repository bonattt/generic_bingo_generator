import json
from os import path
import random

VOCABULARY = "vocabulary.json"
PATTERNS = "patterns.json"
DEFAULT_NAME = "2024"


class Patterns:

    DEFAULT_WEIGHT = 1

    def __init__(self, config_name: str):
        with open(config_path(config_name, VOCABULARY), "r") as f:
            self.json_data = json.loads(f.read())

    @property
    def patterns(self):
        return self.json_data["patterns"]

    @property
    def weights(self):
        return self.json_data.get("weights")

    def get_total_weights(self):
        total = 0
        for _, weight in self.weights:
            total += weight
        return total

    def get_weight(self, pattern_name: str) -> int:
        if not self.weights:
            return self.DEFAULT_WEIGHT
        return self.weights.get(pattern_name, self.DEFAULT_WEIGHT)

    def generate_weighted_pattern_set(self, n) -> list:
        """
        Returns a list of patterns, with duplicates proportional to
        the weight values for each pattern, and enough total items
        to equal or exceed n.
        """
        multiplier = 1
        # TODO --- better maths here
        total_weights = self.get_total_weights()  #
        while self.get_total_weights * multiplier > n:
            multiplier += 1

        result = []
        for key, pattern in self.patterns.items():
            for _ in range(self.get_weight(key) * multiplier):
                result.add(pattern)
        return result

    def select_patters(self, n):
        raw_pattern_set = self.generate_weighted_pattern_set(n)
        return random.sample(raw_pattern_set, n)


class Vocabulary:

    @classmethod
    def load_vocabulary(cls, config_name: str) -> dict:
        vocab = {}
        with open(config_path(config_name, VOCABULARY), "r") as f:
            raw_data = json.loads(f.read())
            for category, data in raw_data.items():
                if data.get("extends"):
                    if isinstance(data.get("extends"), str):
                        cls._extend_vocab_category(
                            vocab,
                            data["dictionary"],
                            data.get("extends"),
                        )
                    elif isinstance(data.get("extends"), list):
                        for ext in data.get("extends"):
                            cls._extend_vocab_category(
                                vocab,
                                data["dictionary"],
                                ext,
                            )
                    else:
                        print(f"WARNING: bad extends value '{data.get('extends')}'")
                cls._extend_vocab_category(
                    vocab,
                    data["dictionary"],
                    category
                )
        return vocab

    @classmethod
    def _extend_vocab_category(cls, vocab: dict, vocab_extension: set, category:str):
        if not isinstance(vocab_extension, set):
            vocab_extension = set(vocab_extension)

        if category in vocab:
            vocab[category] = vocab[category].union(vocab_extension)
        else:
            vocab[category] = vocab_extension

    def __init__(self, config_name: str):
        self.json_data = self.load_vocabulary(config_name)

    def render_pattern_set(self, pattern_choices: list[str]) -> list[str]:
        n = len(pattern_choices)

        return  # TODO ---


def config_path(config_name: str, file_name: str) -> str:
    return path.join("configs", config_name, file_name)


def build_tileset(patterns: Patterns, vocab: Vocabulary, n=25) -> list[str]:
    pattern_choices = patterns.select_patters(n)
    rendered_patterns = vocab.render_pattern_set(pattern_choices)




def main():
    print("vocab:", Vocabulary(DEFAULT_NAME).json_data)
    print("patterns:", Patterns(DEFAULT_NAME).json_data)


if __name__ == "__main__":
    main()