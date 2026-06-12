from rest_framework import serializers
from .models import Review


class ReviewSerializer(serializers.ModelSerializer):
    reviewer_name = serializers.CharField(
        source="reviewer.display_name", read_only=True
    )

    class Meta:
        model = Review
        fields = [
            "id",
            "reviewer_name",
            "overall_rating",
            "punctuality_rating",
            "professionalism_rating",
            "comment",
            "created_at",
        ]
        read_only_fields = ["id", "reviewer_name", "created_at"]
