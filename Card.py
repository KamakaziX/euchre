class Card(object):

    LEAD_BONUS = 100
    TRUMP_BONUS = 500
    LEFT_BOWER_BONUS = 1000
    RIGHT_BOWER_BONUS = 2000


    SUIT_NOSUIT = -1
    SUIT_SPADES = 0
    SUIT_HEARTS = 1
    SUIT_CLUBS = 2
    SUIT_DIAMONDS = 3

    COLOR_BLACK = 0  # Detrmined as SUIT_SPADES % 2 == 0 and SUIT_CLUBS % 2 == 0
    COLOR_RED = 1  # Determined as SUIT_SPADES % 2 == 1 and SUIT_CLUBS % 2 == 1

    ACE = 14
    KING = 13
    QUEEN = 12
    JACK = 11

    SUITS = [SUIT_SPADES, SUIT_HEARTS, SUIT_CLUBS, SUIT_DIAMONDS]
    VALUES = [9, 10, JACK, QUEEN, KING, ACE]

    def __init__(self, suit=None, value=None):
        if value < 9 or value > Card.ACE:
            raise ValueError("Card value cannot be larger than and ACE (9-13 Inclusive).")
        if suit < Card.SUIT_NOSUIT or suit > Card.SUIT_DIAMONDS:
            raise ValueError("Card Suit must be between 0 and 3 (inclusive)")

        self._suit = suit
        self.value = value

    def get_value(self) -> int:
        return self.value

    def get_total_value(self, trump_suit: int, lead_suit: int):
        color = self.get_color(self._suit)
        trump_color = self.get_color(trump_suit)

        ret_val = self.value

        # Player followed suit, but it is not a trump suit.
        if self._suit == lead_suit and trump_suit != lead_suit:
            ret_val += Card.LEAD_BONUS

        # Player does not have a bauer but does have a trump suit card.
        if self.value != Card.JACK and self._suit == trump_suit:
            ret_val += Card.TRUMP_BONUS

        # Player has a bauer
        if self.value == Card.JACK and color == trump_color:
            # we have a jack and a bauer.
            if self._suit == trump_suit:
                ret_val += Card.RIGHT_BOWER_BONUS
            if self._suit != trump_suit:
                ret_val += Card.LEFT_BOWER_BONUS

        return ret_val


    def get_color(self, suit: int) -> int:
        """
        Determine the color of the suit.

        This will also appropriately assign the trump suit to the left bower if this card
        is the left bower.

        The return values map to the constants Card.COLOR_BLACK and Card.COLOR_RED
        :param: trump_suit If set we will check against the trump suit to determine if our card is the left bower
        :return: 0 if the suit is black 1 if the suit is red.
        """
        return suit % 2

    def get_suit(self, trump_suit=None) -> int:
        if trump_suit is not None and self.value == Card.JACK:
            matching_suit = self.get_matching(trump_suit)
            if self._suit == matching_suit:
                return trump_suit
        return self._suit

    def get_raw_suit(self):
        return self._suit

    def set_value(self, new_val: int):
        self.value = new_val

    def set_suit(self, new_suit: int):
        self._suit = new_suit

    def get_value_str(self) -> str:
        if self.value == None:
            return "None"

        elif self.value == 9:
            return "9"

        elif self.value == 10:
            return "10"

        elif self.value == Card.JACK:
            return "J"

        elif self.value == Card.QUEEN:
            return "Q"

        elif self.value == Card.KING:
            return "K"

        elif self.value == Card.ACE:
            return "A"

        return "Unk"

    @staticmethod
    def get_matching(suit):
        """
        Get the matching suit of the card.

        For example if the paramter suit is spades, this will return clubs, if clubs, it will return spades.
        The matching suit is always the other suit of the same color.

        :param suit: The suit you would like the matching suit of.

        :return: The matching suit of the same color.
        """
        if suit == Card.SUIT_CLUBS:
            return Card.SUIT_SPADES

        if suit == Card.SUIT_SPADES:
            return Card.SUIT_CLUBS

        if suit == Card.SUIT_HEARTS:
            return Card.SUIT_DIAMONDS

        if suit == Card.SUIT_DIAMONDS:
            return Card.SUIT_HEARTS

    def get_suit_str(self, short: bool=False) -> str:
        if (short):
            return self.suit_str(self._suit)
        else:
            return self.suit_str_long(self._suit)

    @staticmethod
    def suit_str(suit: int) -> str:
        if suit == Card.SUIT_SPADES:
            return "S"
        elif suit == Card.SUIT_DIAMONDS:
            return "D"
        elif suit == Card.SUIT_CLUBS:
            return "C"
        elif suit == Card.SUIT_HEARTS:
            return "H"

        return "Unk"

    @staticmethod
    def suit_str_long(suit: int) -> str:
        if suit == Card.SUIT_SPADES:
            return "SPADES"
        elif suit == Card.SUIT_DIAMONDS:
            return "DIAMONDS"
        elif suit == Card.SUIT_CLUBS:
            return "CLUBS"
        elif suit == Card.SUIT_HEARTS:
            return "HEARTS"

    def __repr__(self):
        return "{}{}".format(self.get_value_str(), self.get_suit_str(short=True))