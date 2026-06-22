"""
AI Recommendation Engine - Cosine Similarity (sklearn)
"""
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from collections import defaultdict


class RecommendationEngine:
    def __init__(self):
        self.matrix = None
        self.product_ids = []
        self.user_ids = []
        self.sim = None

    def build(self, purchases, views):
        scores = defaultdict(lambda: defaultdict(float))
        for uid, pid, cnt in purchases:
            scores[uid][pid] += cnt * 3.0
        for uid, pid, cnt in views:
            scores[uid][pid] += cnt * 1.0
        if not scores:
            return False
        self.user_ids = list(scores.keys())
        all_pids = set()
        for v in scores.values(): all_pids.update(v.keys())
        self.product_ids = list(all_pids)
        M = np.zeros((len(self.user_ids), len(self.product_ids)))
        for i, uid in enumerate(self.user_ids):
            for j, pid in enumerate(self.product_ids):
                M[i][j] = scores[uid].get(pid, 0)
        self.matrix = M
        self.sim = cosine_similarity(M)
        return True

    def for_user(self, user_id, n=8):
        if self.matrix is None or user_id not in self.user_ids:
            return []
        ui = self.user_ids.index(user_id)
        scores = np.zeros(len(self.product_ids))
        for oi, s in enumerate(self.sim[ui]):
            if oi != ui and s > 0:
                scores += s * self.matrix[oi]
        for j in range(len(self.product_ids)):
            if self.matrix[ui][j] > 0:
                scores[j] = 0
        top = np.argsort(scores)[::-1][:n]
        return [self.product_ids[i] for i in top if scores[i] > 0]

    def similar_to(self, product_id, n=6):
        if product_id not in self.product_ids or self.matrix is None:
            return []
        pi = self.product_ids.index(product_id)
        pvec = self.matrix[:, pi].reshape(1, -1)
        sims = cosine_similarity(pvec, self.matrix.T)[0]
        sims[pi] = 0
        top = np.argsort(sims)[::-1][:n]
        return [self.product_ids[i] for i in top if sims[i] > 0]


def _get_engine():
    from store.models import PurchaseHistory, RecentlyViewed
    from django.db.models import Count
    p = list(PurchaseHistory.objects.values('user_id','product_id').annotate(c=Count('id')))
    v = list(RecentlyViewed.objects.values('user_id','product_id').annotate(c=Count('id')))
    e = RecommendationEngine()
    e.build([(x['user_id'],x['product_id'],x['c']) for x in p],
            [(x['user_id'],x['product_id'],x['c']) for x in v])
    return e


def get_recommendations(user, n=8):
    from store.models import Product
    try:
        e = _get_engine()
        ids = e.for_user(user.id, n)
        products = list(Product.objects.filter(id__in=ids, is_active=True))
        if len(products) < 4:
            trending = Product.objects.filter(is_active=True,is_trending=True).exclude(id__in=[p.id for p in products])[:n]
            products += list(trending)
        return products[:n]
    except Exception:
        return list(Product.objects.filter(is_active=True,is_trending=True)[:n])


def get_similar_products(product, n=6):
    from store.models import Product
    try:
        e = _get_engine()
        ids = e.similar_to(product.id, n)
        similar = list(Product.objects.filter(id__in=ids, is_active=True))
        if len(similar) < 3:
            cat_products = Product.objects.filter(category=product.category,is_active=True).exclude(id=product.id).exclude(id__in=[p.id for p in similar])[:n]
            similar += list(cat_products)
        return similar[:n]
    except Exception:
        return list(Product.objects.filter(category=product.category,is_active=True).exclude(id=product.id)[:n])


def predict_discount(product):
    try:
        score = (product.sales_count * 2) + (product.views_count * 0.5) + (float(product.avg_rating) * 10)
        if score > 500: return 5.0
        elif score > 200: return 10.0
        elif score > 100: return 15.0
        elif score > 50: return 20.0
        else: return 25.0
    except Exception:
        return 0
