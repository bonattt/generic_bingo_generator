import json
from os import path
import random

VOCABULARY = "vocabulary.json"
PATTERNS = "patterns.json"
DEFAULT_NAME = "2024"


class BingoError(Exception):
    pass


class Patterns:

    DEFAULT_WEIGHT = 1

    def __init__(self, config_name: str):
        with open(config_path(config_name, PATTERNS), "r") as f:
            self.json_data = json.loads(f.read())

    @property
    def patterns(self):
        return self.json_data["patterns"]

    @property
    def weights(self):
        return self.json_data.get("weights")

    def get_total_weights(self):
        total = 0
        for _, weight in self.weights.items():
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
        total = self.get_total_weights()
        while total * multiplier > n:
            multiplier += 1

        result = []
        for key, pattern in self.patterns.items():
            for _ in range(self.get_weight(key) * multiplier):
                result.append(pattern)
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
        # n = len(pattern_choices)
        word_query_count = self.get_word_query_count(pattern_choices)
        word_query_results = self.query_words(word_query_count)
        results = []
        for pattern in pattern_choices:
            category_list = self.get_choice_categories(pattern)
            choices = {}
            for c in category_list:
                if c in choices:
                    print("ERROR: duplicate catagory!!")
                choices[c] = word_query_results[c].pop()
            results.append(pattern % choices)
        return results  # TODO ---

    def get_choice_categories(self, pattern: str) -> list[str]:
        result = []
        for item in pattern.split("%")[1:]:
            if not item.startswith("(") and item.endswith(")s"):
                print(f"ERROR: {item}")
                continue
            i = item.index(")s")
            category = item[1:i]
            result.append(category)
        return result


    def get_word_query_count(self, pattern_choices: list[str]) -> list[str]:
        # print("pattern_choices:", pattern_choices)
        all_str = "---".join(pattern_choices)
        # print("all_str:", all_str)
        print("split:", all_str.split("%("))
        print("=" * 25)
        word_queries = {}
        for s in all_str.split("%"):
            if not s.startswith("("):
                # not an actual choice
                continue
            i = s.index(")s")
            choice_category = s[1:i]
            if choice_category in word_queries:
                word_queries[choice_category] += 1
            else:
                word_queries[choice_category] = 1
        return word_queries

    def query_words(self, word_query_count) -> dict[str, list[str]]:
        result = {}
        for category, count in word_query_count.items():
            try:
                target_vocab = list(self.json_data[category])
                while len(target_vocab) < count:
                    target_vocab = target_vocab + list(self.json_data[category])
                result[category] = random.sample(target_vocab, count)
            except KeyError:
                raise BingoError(f"missing category '{category}'")

        return result


def config_path(config_name: str, file_name: str) -> str:
    return path.join("configs", config_name, file_name)


def build_tileset(patterns: Patterns, vocab: Vocabulary, n=25) -> list[str]:
    pattern_choices = patterns.select_patters(n)
    rendered_patterns = vocab.render_pattern_set(pattern_choices)
    return rendered_patterns


def cmd_print_bingo(bingo_tiles: list[str]):
    """
    prints a bingo board to stdout
    """





def main():
    vocab = Vocabulary(DEFAULT_NAME)
    pattern = Patterns(DEFAULT_NAME)
    # print("vocab:", vocab.json_data)
    # print("=" * 25)
    # print("patterns:", pattern.json_data)
    # print("=" * 25)
    print("result:", build_tileset(pattern, vocab))


if __name__ == "__main__":
    main()