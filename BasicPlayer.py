from Player import Player
from GameState import GameState
from Card import Card
from secrets import randbelow, choice
import copy
import logging
from typing import List, Optional
import operator


class BasicPlayer(Player):

    BID_THRESHOLD = 7

    def make_move(self, game_state: GameState):

        card = None
        valid_plays = game_state.get_valid_plays(self.hand)
        if len(game_state.trick_cards) == 0:
            # It's my lead, I can play anything I want.
            card = self.get_biggest_trump(game_state.trumps)
            if card is None:
                # lead biggest off suit
                card = self.get_biggest_non_trump(game_state.trumps)

        elif len(game_state.trick_cards) == 1:
            # I'm the second player to play. I need to determine if I can beat the
            # previous player's card.
            opponent_card = game_state.played_cards[-1]

        else:
            # I'm the last person. Determine if my partner is already winning
            current_winner = game_state.calc_winner()
            # @ todo, this should be fixed, its not always going to be that player id and team id are connected.
            current_winner_team_id = current_winner.get_total_value(game_state.trumps, game_state.lead_card) % 2

            # My partner has already won the trick, toss something stupid
            if current_winner_team_id == self.team_id:

                card = self.find_lowest_card(game_state.trumps)

            # The other team is winning the trick. Determine if I can win
            card = self.winning_card(game_state.trumps, game_state.trick_cards)
            if card is None:
                # No way to win, toss something stupid
                card = self.find_lowest_card(game_state.trumps)

        self.hand.remove(card)
        return card

    def make_bid_rnd_1(self, top_card: Card) -> int:
        """
        Determine if we should order up.

        :param top_card The top card on the deck during bidding.
        :return: True if the player orders it up / assists False if they pass
        """

        hand_strength = self.calc_hand_strength(top_card)
        if hand_strength >= BasicPlayer.BID_THRESHOLD:
            return Player.ORDER_UP

        return Player.PASS

    def is_loaner(self, game_state: GameState) -> bool:
        """
        Determine if the player wants to go alone or not.

        In this basic strategy the player always relies on their partner, and never goes alone.

        :param game_state: The GameState object
        :return: True of he player will go alone. False otherwise.
        """
        return False

    def make_bid_rnd_2(self, top_card: Card) -> int:
        """
        Determine if the  player should call trump or not.

        If the player cannot make a hand tht is better than or equal to 7 points they will pass. Otherwise, they
        will announce trump.

        :param top_card: The top card of the deck during bidding.
        :return: The suit that the player wants to bid on. Card.SUIT_NOSUIT if they wish to pass.
        """
        suits = copy.copy(Card.SUITS)  # a little slow, but readable. Necessary so we don't all modify the same list.
        invalid_suit = top_card.get_suit()
        suits.remove(invalid_suit)

        strongest_suit = 0
        best_suit = Card.SUIT_NOSUIT
        for suit in suits:
            hand_strength = self.calc_hand_strength(Card(suit, 10))  # The value doesn't matter.
            if hand_strength > strongest_suit:
                best_suit = suit
                strongest_suit = hand_strength

        if strongest_suit >= BasicPlayer.BID_THRESHOLD:
            return best_suit
        else:
            return Card.SUIT_NOSUIT

    def discard(self, trump_suit: int) -> Card:
        """
        The dealer will be required to discard if he has a card ordered up.
        This function decides what to discard.

        :attention unit tests written.

        :note It's safe to use self.hand here since in the case of discard we have yet to set the lead card. Therefore,
        the player could reasonably be able to discard ny card they decided.

        :param trump_suit: The suit of the card determined to be trump.
        :return: The discarded card.
        """
        idx = None
        voidable_suits = self.find_voidable_suits(trump_suit, self.hand)
        if len(voidable_suits) > 0:
            lowest_card = min(filter(lambda a: a.get_suit(trump_suit) in voidable_suits, self.hand),
                            key=lambda c: c.get_total_value(trump_suit, Card.SUIT_NOSUIT))

        else:
            lowest_card = self.find_lowest_card(trump_suit, Card.SUIT_NOSUIT, self.hand)

        self.hand.remove(lowest_card)
        return lowest_card

    def count_suit(self, suit: int, trump_suit: int=Card.SUIT_NOSUIT) -> int:
        """
        Count the number of cards given a particular suit.

        If the trump suit is set, then the left bower will be treated as a member of that suit. If set to
        the default value of Card.SUIT_NOSUIT this function will usethe raw suit.

        :attention unit tests written

        :param suit: The card suit you want to count
        :param trump_suit:  The current trump suit.
        :return: The number of cards of the provided suit in the player's hand.
        """

        count = 0
        for card in self.hand:
            if card.get_suit(trump_suit) == suit:
                count += 1
        return count

    def would_have_right_bower(self, top_card: Card) -> bool:
        """
        Determine if the player would have the right bower, given that the top card would be picked up.

        This function should only be used in bidding. It tries to determine that if the player ordered up the top card,
        that they would now have a right bower in their hand.

        :attention unit tests written

        :param top_card: The top card during bidding.
        :return: True if the player would have the right bower. False if the player would not have the right bower,
        including the situation where the player would have the left bower. For that information call
        would_have_left_bower()
        """
        for card in self.hand:
            if card.value == Card.JACK and top_card._suit == card._suit:
                return True
        return False

    def would_have_left_bower(self, top_card: Card) -> bool:
        """
        Determine if the player would have the left bower, given that the top card is picked up.

        This function should only be used in bidding. It tries to determine that if the player ordered up the top card,
        that they would now have a left bower in their hand.

        :attention unit tests written.

        :param top_card: The top card on the deck, used in bidding.
        :return: True if the player would have the left bower. False otherwise, including the situation where the player
        would have the right bower. For that information call would_have_right_bower().
        """
        for card in self.hand:
            # Note: card.suit is used here since this is only used in bidding, and therefore the trump card is not set.
            if card.value == Card.JACK and Card.get_matching(top_card._suit) == card._suit:
                return True
        return False

    def has_card(self, value: int, suit: int, trump_suit: int=Card.SUIT_NOSUIT) -> bool:
        """
        Determine if there is a particular card in the player's hand.

        :attention unit tests written.

        :param value: The value desired. This is the straight value, irrespective of the trump suit.
        :param suit: This is the suit of the card. if trump_suit is provided, this is the effective suit of the card.
        Otherwise, it's the raw suit of the card.
        :param trump_suit: The current trump suit. Take care when using this parameter, the left and right bower will
        look the same.

        :return: True of the player has the card in his hand that matches. False otherwise.
        """
        for card in self.hand:
            if card.value == value and card.get_suit(trump_suit) == suit:
                return True
        return False

    def num_offsuit_aces(self, avoid_suit: int, hand: List[Card]) -> int:
        """
        Calculate the number of off-suit aces that exist in our hand.

        :attention - Unit tests written

        :param avoid_suit: The suit we wish to not count. Typically trump or something.
        :param hand: A list of cards that the player could play.

        :return: The number of offsuit aces in our hand.
        """
        count = sum(1 for c in filter(lambda c: c.get_raw_suit() != avoid_suit and c.value == Card.ACE, hand))

        return count

    def calc_hand_strength(self, potential_trump: Card) -> int:
        """
        Hand strength system found at: https://www.thespruce.com/how-to-bid-in-euchre-411487
        Other systems exist that I may implement in the future.

        :attention unit tests written

        :param potential_trump: The potential trump card.
        :return: The value of the hand as an integer.
        """
        hand_strength = 0

        if self.would_have_right_bower(potential_trump):
            hand_strength += 3
        if self.would_have_left_bower(potential_trump):
            hand_strength += 3

        top_card_suit = potential_trump.get_raw_suit()
        if self.has_card(Card.ACE, top_card_suit):
            hand_strength += 2
        if self.has_card(Card.KING, top_card_suit):
            hand_strength += 2
        if self.has_card(Card.QUEEN, top_card_suit):
            hand_strength += 2
        if self.has_card(Card.JACK, top_card_suit):
            hand_strength += 2
        if self.has_card(10, top_card_suit):
            hand_strength += 1
        if self.has_card(9, top_card_suit):
            hand_strength += 1

        offsuit_aces = self.num_offsuit_aces(top_card_suit, self.hand)
        hand_strength += offsuit_aces
        return hand_strength

    def find_voidable_suits(self, trump_suit: int, hand: List[Card]) -> List[int]:
        """
        Find any suits which could be voided (only one card remains)

        :attention tests written

        :param trump_suit: The current trump suit, this suit will not be reported.
        :param hand: A list of cards the player can play.

        :return: A list of integers containing the suits which can be voided
        """
        suit_count = [0 for _ in range(4)]
        for card in hand:
            suit_count[card.get_suit(trump_suit)] += 1

        voidable_suits = list()
        for suit, count in enumerate(suit_count):
            if count == 1 and suit != trump_suit:
                voidable_suits.append(suit)

        return voidable_suits

    def find_lowest_card(self, trump_suit: int, lead_suit: int, hand: List[Card]) -> Optional[Card]:
        """
        Get the lowest card possible.

        :attention unit tests written

        :param trump_suit: The suit to not pick from (usually because it's trump).
        :param lead_suit: The suit that was lead. Card.SUIT_NOSUIT if it hasn't been set.
        :return: A card that is the lowest in my hand. None if a non-avoid suit card can be found.
        """
        try:
            card = min(filter(lambda a: a.get_suit(lead_suit) != trump_suit, hand),
                       key=lambda c: c.get_total_value(trump_suit, lead_suit))
        except ValueError:
            return None

        return card

    def get_biggest_trump(self, trump_suit: int, lead_card_suit: int, hand: List[Card]) -> Optional[Card]:
        """
        Get the biggest trump-suited card in my hand.

        :attention tests written

        :param trump_suit: The trumpian suit.
        :param lead_card_suit: The lead card's suit.
        :param hand: The hand.
        :return: None if there are no trump cards. The biggest trump card if one exists.
        """
        try:
            card = max(filter(lambda a: a.get_suit(trump_suit) == trump_suit, hand),
                       key=lambda c: c.get_total_value(trump_suit, lead_card_suit))
        except ValueError as ex:
            return None

        return card

    def get_trump_cards(self, trump_suit: int, hand: List[Card]):
        """
        Return all of the card sin my hand that are trumps.

        :note The hand list may be the entire self.hand, or the caller may provide a reduced list of cards,
        possibly passed through game_state.get_valid_cards().

        :attention tests written

        :param trump_suit: The trump suit.
        :param hand: A hand.
        :return: A list of cards.
        """
        cards = [card for card in hand if card.get_suit(trump_suit) == trump_suit]
        return cards

    def get_biggest_non_trump(self, trump_suit: int, lead_card: Card, hand: List[Card]) -> Optional[Card]:
        """
        Get the biggest non-trump card.

        Note that the hand parameter can (or should be) a reduced list of cards provided by
        game_state.get_valid_cards().

        TODO: This function might not work if lead_card can't be set. We may need to re-work this or Card.get_suit
        to account for a lead_card of None.

        :attention tests written

        :param trump_suit: The trump suit
        :param lead_card: The card that was lead.
        :param hand: The players hand. This may be a restricted list of playable cards.
        :return: The biggest non-trump suit. In case of a tie, the first one encountered is returned.
        """
        try:
            card = max(
                filter(lambda a: a.get_suit(trump_suit) != trump_suit, hand),
                key=lambda c: c.get_total_value(trump_suit, lead_card.get_suit(trump_suit)))
        except ValueError as ex:
            return None

        return card

    def smallest_winning_card(self, trump_suit: int, tricks_played: List[Card], hand: List[Card]) -> Optional[Card]:
        """
        Get the smallest winning card.

        :param trump_suit: the trump suit.
        :param tricks_played: The tricks that have already been played,

        :return: None if there is no card that will win, or there is no lead card. Otherwise, the smallest card that can win the trick otherwise.
        """
        if len(tricks_played) == 0:
            return None

        lead_card = tricks_played[0]

        lead_card_suit = tricks_played[0].get_suit(trump_suit)
        lead_card_value = tricks_played[0].get_total_value(trump_suit, lead_card_suit)

        winning_cards =filter(lambda a: a.get_total_value(trump_suit, lead_card_suit) > lead_card_value, hand)
        try:
            smallest_card = min(
                winning_cards,
                key=lambda c: c.get_total_value(trump_suit, lead_card_suit))

        except ValueError as ex:
            return None

        return smallest_card

