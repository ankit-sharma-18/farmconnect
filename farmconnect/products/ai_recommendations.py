# products/ai_recommendations.py
"""
AI-Powered Product Recommendation System
Uses collaborative filtering and content-based filtering
"""

from django.db.models import Count, Q, Avg
from collections import Counter
import math

class AIRecommendationEngine:
    """Smart product recommendation engine"""
    
    def __init__(self, user):
        self.user = user
    
    def get_personalized_recommendations(self, limit=6):
        """
        Get AI-powered personalized product recommendations
        Combines multiple algorithms:
        1. Collaborative filtering (users who bought X also bought Y)
        2. Content-based filtering (similar products)
        3. Location-based recommendations
        4. Popularity-based fallback
        """
        from products.models import Product
        from orders.models import Order
        from accounts.models import BuyerProfile
        
        recommendations = []
        
        # Get user's order history
        user_orders = Order.objects.filter(buyer=self.user).values_list('product_id', flat=True)
        user_products = list(user_orders)
        
        if user_products:
            # Collaborative Filtering: Find similar users
            similar_users = Order.objects.filter(
                product_id__in=user_products
            ).exclude(
                buyer=self.user
            ).values('buyer').annotate(
                common_products=Count('product')
            ).order_by('-common_products')[:10]
            
            similar_user_ids = [u['buyer'] for u in similar_users]
            
            # Get products bought by similar users
            collaborative_products = Order.objects.filter(
                buyer_id__in=similar_user_ids
            ).exclude(
                product_id__in=user_products
            ).values('product_id').annotate(
                frequency=Count('product_id')
            ).order_by('-frequency')[:limit]
            
            for item in collaborative_products:
                try:
                    product = Product.objects.get(id=item['product_id'], is_available=True)
                    recommendations.append({
                        'product': product,
                        'score': item['frequency'] * 2,  # Weighted score
                        'reason': 'People with similar tastes loved this'
                    })
                except Product.DoesNotExist:
                    pass
        
        # Content-Based Filtering: Similar categories
        if user_products:
            user_categories = Product.objects.filter(
                id__in=user_products
            ).values_list('category_id', flat=True).distinct()
            
            similar_products = Product.objects.filter(
                category_id__in=user_categories,
                is_available=True
            ).exclude(
                id__in=user_products
            ).annotate(
                avg_rating=Avg('farmer__farmer_profile__average_rating')
            ).order_by('-avg_rating')[:limit]
            
            for product in similar_products:
                recommendations.append({
                    'product': product,
                    'score': float(product.avg_rating or 0) + 1,
                    'reason': 'Similar to products you ordered'
                })
        
        # Location-Based Recommendations
        try:
            buyer_profile = self.user.buyer_profile
            nearby_products = Product.objects.filter(
                is_available=True,
                farmer__city=buyer_profile.city
            ).exclude(
                id__in=user_products
            )[:limit]
            
            for product in nearby_products:
                recommendations.append({
                    'product': product,
                    'score': 1.5,
                    'reason': 'Fresh from local farms near you'
                })
        except:
            pass
        
        # Popularity-Based Fallback
        popular_products = Product.objects.filter(
            is_available=True
        ).annotate(
            order_count=Count('orders')
        ).exclude(
            id__in=user_products
        ).order_by('-order_count')[:limit]
        
        for product in popular_products:
            recommendations.append({
                'product': product,
                'score': 1,
                'reason': 'Trending in your area'
            })
        
        # Remove duplicates and sort by score
        seen_products = set()
        unique_recommendations = []
        
        for rec in recommendations:
            product_id = rec['product'].id
            if product_id not in seen_products:
                seen_products.add(product_id)
                unique_recommendations.append(rec)
        
        # Sort by score (descending)
        unique_recommendations.sort(key=lambda x: x['score'], reverse=True)
        
        return unique_recommendations[:limit]
    
    def get_similar_products(self, product, limit=4):
        """
        Find products similar to the given product
        Uses content-based similarity
        """
        from products.models import Product
        
        similar = []
        
        # Same category
        if product.category:
            category_products = Product.objects.filter(
                category=product.category,
                is_available=True
            ).exclude(id=product.id)[:limit]
            
            for p in category_products:
                similar.append({
                    'product': p,
                    'similarity': 0.8,
                    'reason': f'Also in {product.category.name}'
                })
        
        # Same farmer
        farmer_products = Product.objects.filter(
            farmer=product.farmer,
            is_available=True
        ).exclude(id=product.id)[:limit]
        
        for p in farmer_products:
            if p.id not in [s['product'].id for s in similar]:
                similar.append({
                    'product': p,
                    'similarity': 0.7,
                    'reason': f'From {product.farmer.farm_name}'
                })
        
        # Price range similar products
        price_min = float(product.price) * 0.8
        price_max = float(product.price) * 1.2
        
        price_similar = Product.objects.filter(
            price__gte=price_min,
            price__lte=price_max,
            is_available=True
        ).exclude(id=product.id)[:limit]
        
        for p in price_similar:
            if p.id not in [s['product'].id for s in similar]:
                similar.append({
                    'product': p,
                    'similarity': 0.6,
                    'reason': 'Similar price range'
                })
        
        return similar[:limit]
    
    def get_smart_search_results(self, query, user_location=None):
        """
        AI-powered search with ranking
        """
        from products.models import Product
        
        products = Product.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query),
            is_available=True
        )
        
        results = []
        query_lower = query.lower()
        
        for product in products:
            score = 0
            
            # Exact match in name
            if query_lower in product.name.lower():
                score += 10
            
            # Match in description
            if query_lower in product.description.lower():
                score += 5
            
            # Category match
            if product.category and query_lower in product.category.name.lower():
                score += 7
            
            # Organic bonus
            if product.is_organic and 'organic' in query_lower:
                score += 3
            
            # Rating bonus
            if product.farmer.average_rating > 4:
                score += 2
            
            results.append({
                'product': product,
                'relevance_score': score
            })
        
        # Sort by relevance
        results.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        return [r['product'] for r in results]


# Helper function to use in views
def get_ai_recommendations_for_user(user, limit=6):
    """Convenient function to get recommendations"""
    engine = AIRecommendationEngine(user)
    return engine.get_personalized_recommendations(limit)


def get_similar_products_ai(product, limit=4):
    """Get similar products using AI"""
    engine = AIRecommendationEngine(None)
    return engine.get_similar_products(product, limit)