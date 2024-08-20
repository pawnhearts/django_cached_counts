from django.core.cache import cache
from django.db.models.signals import m2m_changed, post_save, post_delete



class CachedCount(object):
    """
    Usage:
    class MyModel(models.Model):
        bar = models.ManyToManyField(Bar)
        foo_count = CachedCount("foo_set", filter=Q(foo__x__gte=10))
        total_user_count = CachedCount(User.objects.all())
        m2m_count = CachedCount('bar_set')

    class Foo(models.Model):
        mymodel = models.ForeignKey(MyModel)

    Those counts would be cached and invalidated when models Foo or User are saved/deleted
    """
    def __init__(self, expr, filter=None):
        self.expr = expr
        self.filter = filter
        self.name = None
        self.model = None
        self.m2m = False

    def __get__(self, obj, objtype):
        if self.name in cache:
            return cache.get(self.name)
        if isinstance(self.expr, str):
            qs = getattr(obj, self.expr)
        else:
            qs = self.expr
        if self.filter:
            qs = qs.filter(self.filter)
        res = qs.count()
        cache.set(self.name, res)
        return res

    def contribute_to_class(self, cls, field_name):
        self.name = f'{repr(cls)}_{repr(self.expr)}_{repr(self.filter)}'
        m2m = False

        if isinstance(self.expr, str):
            rel = getattr(cls, self.expr).rel
            if hasattr(rel, 'through'):
                model = rel.through
                m2m = True
            else:
                model = rel.related_model
        else:
            model = self.expr.model
        self.model = model
        self.m2m = m2m
        if m2m:
            m2m_changed.connect(self.clean_cache, sender=model)
        else:
            post_save.connect(self.clean_cache, sender=model)
            post_delete.connect(self.clean_cache, sender=model)

    def clean_cache(self, *args, **kwargs):
        cache.delete(self.name)

