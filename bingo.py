import json
from os import path
import random

VOCABULARY = "vocabulary.json"
PATTERNS = "patterns.json"
DEFAULT_NAME = "2024"
CONFIG_PATH = "bingo_configs"


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

    @property
    def free_space(self):
        return self.patterns["free_space"]

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

    def render_single_pattern(self, pattern: str):
        result = self.render_pattern_set([pattern])
        return result[0]

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
        all_str = "---".join(pattern_choices)
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
    return path.join(CONFIG_PATH, config_name, file_name)


def build_tileset(patterns: Patterns, vocab: Vocabulary, n=25) -> list[str]:
    pattern_choices = patterns.select_patters(n)
    rendered_patterns = vocab.render_pattern_set(pattern_choices)
    return rendered_patterns


def generate_default_tileset(n=25):
    vocab = Vocabulary(DEFAULT_NAME)
    patterns = Patterns(DEFAULT_NAME)
    return build_tileset(patterns, vocab, n)


def generate_default_bingo_board(n=5):
    vocab = Vocabulary(DEFAULT_NAME)
    patterns = Patterns(DEFAULT_NAME)
    return generate_bingo_board(patterns, vocab, n)


def generate_bingo_board(
        patterns: Patterns,
        vocab: Vocabulary,
        n=5,
        free_space=True,
) -> list[list[str]]:
    n_tiles = n**2
    if free_space:
        n_tiles -= 1
    tileset = build_tileset(patterns, vocab, n_tiles)

    if free_space:
        center = len(tileset) / 2
        insert_at(
            tileset,
            vocab.render_single_pattern(patterns.free_space),
            center,
        )
    return compose_bingo_board(tileset, n)


def insert_at(data: list, item, index: int):
    """
    Takes a list, an insex, and a item to be added to the list.
    Adds the item to the list at the given index, pushing each
    element of the list at or after that index forward one spot.
    """
    if not isinstance(index, int):
        index = int(index)
    current = item
    next = item
    breakpoint()
    for i in range(index, len(data), 1):
        next = data[i]
        data[i] = current
        current = next
    data.append(next)




def compose_bingo_board(tileset: list[str], n) -> list[list[str]]:
    board = []
    col_number = 0
    row_number = 0
    for tile in tileset:
        if col_number == n:
            col_number = 0
            row_number += 1

        if col_number == 0:
            board.append([])

        board[row_number].append(tile)
        col_number += 1
    return board



def cmd_bingo(n=5) -> str:
    """
    returns a string of a bingo board to as a string
    bingo board is a square of length N tiles
    """
    bingo_board = generate_default_tileset(n**2)
    max_len = get_max_length(bingo_board)
    output = ""
    tile_count = 0
    line_divider_length = ((max_len + 1) * n)
    for word in bingo_board:
        if tile_count == n:
            tile_count = 0
            output += "|\n" + ("-" * line_divider_length) + "\n|"
        else:
            tile_count += 1

        adjusted_word = ("{:<%d}" % max_len).format(word)
        output += adjusted_word
    return output

def get_max_length(bingo_board: list[str]) -> int:
    """
    Takes a list of strings, and returns the max string length of
    any string in the list.
    """
    return max([len(s) for s in bingo_board])


def main():
    print(generate_default_bingo_board())


if __name__ == "__main__":
    main()