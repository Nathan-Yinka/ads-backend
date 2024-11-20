from django.utils.timezone import now, timedelta
from .models import Game, Product,generate_unique_rating_no
import random


class PlayGameService:
    """
    Service to handle the logic for playing a game and assigning the next game.
    """

    def __init__(self, user, total_number_can_play, wallet):
        self.user = user
        self.total_number_can_play = total_number_can_play
        self.wallet = wallet

    def check_can_user_play(self):
        """
        Check if the user is eligible to play a game.
        Returns a tuple: (can_play: bool, message: str)
        """
        if self.wallet.on_hold != 0:
            return False, "You have a pending transaction, please clear it to proceed."
        if self.wallet.balance < 100:
            return False, "You need a minimum of 100 USD balnce to play a game."
        if Game.count_games_played_today(self.user) >= self.total_number_can_play:
            return False, "You have reached the maximum number of games you can play for today."
        return True, ""

    def get_active_game(self):
        """
        Retrieve the user's active game.
        Returns a tuple: (game: Game or None, error: str)
        """
        special_game = Game.objects.filter(user=self.user, played=False,special_product=True).first()
        if special_game:
            return special_game,""
        active_game = Game.objects.filter(user=self.user, played=False).first()
        if active_game:
            return active_game, ""

        # If no active game exists, try to assign a new one
        return self.assign_next_game()

    def mark_game_as_played(self, game, rating_score, comment):
        """
        Mark the current active game as played and update it with a rating and comment.
        """
        
        game.played = True
        game.rating_score = rating_score
        game.comment = comment
        game.save()

    def assign_next_game(self):
        """
        Assign the next game for the user with one or two products they haven't played today.
        Set the game amount and commission based on the selected products.
        Returns a tuple: (game: Game or None, message: str)
        """
        start_of_day = now().replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)

        # Get all products the user has played today
        played_products_today = Game.objects.filter(
            user=self.user,
            created_at__gte=start_of_day,
            created_at__lt=end_of_day
        ).values_list('products__id', flat=True)

        # Get products the user hasn't played today
        available_products = Product.objects.exclude(id__in=played_products_today)

        if not available_products.exists():
            return None, "No new games available for you."

        # Randomly select 1 or 2 products
        product_count = random.choice([1, 2])
        selected_products = available_products[:product_count]

        # Calculate the total amount and commission
        total_amount = sum(product.price for product in selected_products)
        commission_percentage = 10  # Example: 10%
        commission = (total_amount * commission_percentage) / 100

        # Create a new game instance
        new_game = Game.objects.create(
            user=self.user,
            played=False,
            amount=total_amount,
            commission=commission,
            rating_no=generate_unique_rating_no()
        )

        # Associate the selected products with the new game
        new_game.products.set(selected_products)
        new_game.save()

        return new_game, ""

    def play_game(self, rating_score, comment):
        """
        Main method to mark the active game as played and assign the next game.
        Returns a tuple: (game: Game or None, message: str)
        """
        # Check if the user is eligible to play
        can_play, message = self.check_can_user_play()
        if not can_play:
            return None, message

        # Retrieve the active game or assign a new one
        active_game, error = self.get_active_game()
        if error:
            return None, error

        # Mark the current active game as played with rating and comment
        self.mark_game_as_played(active_game, rating_score, comment)

        # Assign the next game
        next_game, error = self.get_active_game()
        if error:
            return None, error

        return next_game, "Game played successfully!"
