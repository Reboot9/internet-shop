import redis
from django.conf import settings
from shop.models import Product

# connect to Redis
r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB)


class Recommender:
    def get_product_key(self, id_):
        return f'product:{id_}:purchased_with'

    def products_bought(self, products):
        product_ids = [p.id for p in products]
        for product_id in product_ids:
            for with_id in product_ids:
                # skip if this is the same product
                if product_id != with_id:
                    # Increase the score of the product bought together
                    r.zincrby(self.get_product_key(product_id), 1, with_id)

    def suggest_products_for(self, products, max_results=4):
        product_ids = [p.id for p in products]
        if len(product_ids) == 1:
            suggestions = self.get_suggestions_for_single_product(product_ids[0], max_results)
            # suggestions = r.zrange(self.get_product_key(product_ids[0]), 0, -1, desc=True)[:max_results]
        else:
            suggestions = self.get_suggestions_for_multiple_products(product_ids, max_results)

        suggested_product_ids = [int(id_) for id_ in suggestions]

        suggested_products = list(Product.objects.filter(id__in=suggested_product_ids))
        suggested_products.sort(key=lambda x: suggested_product_ids.index(x.id))

        return suggested_products

    def get_suggestions_for_single_product(self, product_id, max_results):
        return r.zrange(self.get_product_key(product_id), 0, -1, desc=True)[:max_results]

    def get_suggestions_for_multiple_products(self, product_ids, max_results):
        # generate temporary key
        flat_ids = ''.join([str(id_) for id_ in product_ids])
        tmp_key = f'tmp_{flat_ids}'

        # combine the scores of all products, save the resulting sorted set in a temporary key
        keys = [self.get_product_key(id_ for id_ in product_ids)]
        r.zunionstore(tmp_key, keys)
        # delete product ids that are recommended
        r.zrem(tmp_key, *product_ids)

        # sort products in descending order by their amount
        suggestions = r.zrange(tmp_key, 0, -1, desc=True)[:max_results]

        # delete temp key
        r.delete(tmp_key)

        return suggestions
    def clear_purchases(self):
        for id_ in Product.objects.values_list('id', flat=True):
            r.delete(self.get_product_key(id_))