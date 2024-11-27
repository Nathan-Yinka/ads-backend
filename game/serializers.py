from rest_framework import serializers
from .models import Product,Game


class ProductSerializer(serializers.ModelSerializer):
    """
    Serializer for the Product model with custom validation.
    """

    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'price',
            'image',
            'rating_no',
            'date_created',
        ]
        read_only_fields = ['rating_no', 'date_created']

    def validate_price(self, value):
        """
        Ensure the price is a positive number.
        """
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than 0.")
        return value




class ProductList(serializers.ModelSerializer):
    """
    Serializer for listing products associated with a game.
    """
    class Meta:
        model = Product  # Fixed to reference the Product model
        fields = ['id', 'name', 'image', 'price', 'rating_no']


class GameSerializer:
    """
    Serializer container for games.
    """

    class PlayGameRequestSerializer(serializers.Serializer):
        """
        Serializer for the play game request payload.
        """
        rating_score = serializers.IntegerField(required=True)
        comment = serializers.CharField(required=False, allow_blank=True)




    class Retrieve(serializers.ModelSerializer):
        """
        Serializer for retrieving game details, including products and limits.
        """
        total_number_can_play = serializers.SerializerMethodField()
        current_number_count = serializers.SerializerMethodField()
        products = ProductList(many=True)  # Correctly reference ProductList serializer

        class Meta:
            model = Game
            fields = [
                'id', 
                'products', 
                'amount', 
                'commission', 
                'total_number_can_play', 
                'current_number_count', 
                'rating_score',
                'comment',
                'special_product',
                'created_at',
                'rating_no',
                'game_number',
                'pending',
            ]
            ref_name = "Game Retrieve" 
            extra_kwargs = {
            'rating_score': {'write_only': True},
            'comment': {'write_only': True},
        }
        
        def get_total_number_can_play(self, obj):
            """
            Retrieve the total number of games the user can play.
            This should be passed in the serializer context.
            """
            return self.context.get('total_number_can_play', 0)

        def get_current_number_count(self, obj):
            """
            Retrieve the current number of games played by the user today.
            This should be passed in the serializer context.
            """
            return self.context.get('current_number_count', 0)
        
    class List(serializers.ModelSerializer):
        products = ProductList(many=True) 
        class Meta:
            model = Game
            fields = [
                'id', 
                'products', 
                'amount', 
                'commission', 
                'rating_score',
                'comment',
                'special_product',
                'updated_at',
                'rating_no',
                'pending',
            ]
            ref_name = "Game Retrieve" 