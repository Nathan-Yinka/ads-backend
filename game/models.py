import random
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.timezone import now, timedelta

User = get_user_model()


def generate_unique_rating_no():
    """
    Generate a unique 11-digit number for rating_no.
    """
    while True:
        rating_no = ''.join([str(random.randint(0, 9)) for _ in range(11)])
        if not Product.objects.filter(rating_no=rating_no).exists():
            return rating_no


class Product(models.Model):
    name = models.CharField(max_length=255, unique=True) 
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    image = models.ImageField(upload_to='product_images/')
    rating_no = models.CharField(max_length=11, unique=True, editable=False, blank=True)  # Unique 11-digit number
    date_created = models.DateTimeField(auto_now_add=True)  # Corrected typo from `auto_add_now`

    def save(self, *args, **kwargs):
        # Generate unique rating_no if not already set
        if not self.rating_no:
            self.rating_no = generate_unique_rating_no()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name



class Game(models.Model):
    products = models.ManyToManyField('Product', related_name="games")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="games")  
    rating_score = models.PositiveIntegerField(blank=True,null=True)  
    comment = models.TextField(max_length=500, blank=True,null=True) 
    created_at = models.DateTimeField(auto_now_add=True)  
    updated_at = models.DateTimeField(auto_now=True) 
    played = models.BooleanField(default=False)
    amount = models.DecimalField(max_digits=10, decimal_places=2,blank=True,null=True)
    commission = models.DecimalField(max_digits=10, decimal_places=2,blank=True,null=True)
    special_product = models.BooleanField(default=False)
    rating_no = models.CharField(max_length=11, unique=True, blank=True)  # Unique 11-digit number
    
    class Meta:
        ordering = ['-created_at']  # Default ordering by creation date (most recent first)

    # def save(self, *args, **kwargs):
    #     """
    #     Override save method to ensure that a user can review a product only once per day.
    #     """
    #     # Calculate the start and end of the current day
    #     start_of_day = now().replace(hour=0, minute=0, second=0, microsecond=0)
    #     end_of_day = start_of_day + timedelta(days=1)

    #     # Check if a review by this user for this product exists today
    #     existing_review = Game.objects.filter(
    #         product=self.product,
    #         user=self.user,
    #         created_at__gte=start_of_day,
    #         created_at__lt=end_of_day
    #     ).exists()

    #     if existing_review:
    #         raise ValueError("You can only review this product once per day.")

    #     super().save(*args, **kwargs)
        
    def save(self, *args, **kwargs):
        """
        Override save method to enforce a maximum of 3 products per game.
        """
        super().save(*args, **kwargs)
        if not self.rating_no:
            self.rating_no = generate_unique_rating_no()
        if self.products.count() > 3:
            raise ValueError("A game cannot have more than 3 products.")

    @classmethod
    def count_games_played_today(cls, user):
        """
        Count the number of games a user has played today.
        """
        # Calculate the start and end of the current day
        start_of_day = now().replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)

        # Count games played by the user today
        return cls.objects.filter(
            user=user,
            played=True,  # Ensure we only count played games
            created_at__gte=start_of_day,
            created_at__lt=end_of_day
        ).count()

    def __str__(self):
        return f"Game Review: {self.product.name} by {self.user.username}"


# class UserGame(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_game')
#     number
#     is_reviewed = models.BooleanField(default=False)

#     class Meta:
#         unique_together = ('user', 'game')