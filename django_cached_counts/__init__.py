from django.core.cache import cache
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.apps import apps


from django.db.models.signals import m2m_changed, post_save, post_delete


class CachedCount(object):
    """
    Usage:
    class MyModel(models.Model):
        bar = models.ManyToManyField(Bar)
        foo_count = CachedCount("foo_set", filter=Q(foo__x__gte=10), timeout=120)
        total_user_count = CachedCount(User.objects.all())
        m2m_count = CachedCount('bar_set')

    class Foo(models.Model):
        mymodel = models.ForeignKey(MyModel)

    Those counts would be cached and invalidated when models Foo or User are saved/deleted.
    If there are some joins in filter which would affect count too - you can define them manually:

    user_count = CachedCount(User.objects.filter(groups__name='test'), also_invalidated=[User.groups])
    user_count = CachedCount(User.objects.filter(groups__name='test'), also_invalidated=[User.groups])

    """
    def __init__(self, expr, filter=None, timeout=DEFAULT_TIMEOUT, also_invalidate_on=None):
        self.expr = expr
        self.filter = filter
        self.name = None
        self.model = None
        self.m2m = False
        self.timeout = timeout
        self.also_invalidate_on = also_invalidate_on or []

    def __get__(self, obj, objtype):
        if self.name in cache:
            return cache.get(self.name)
        if isinstance(self.expr, str):
            qs = getattr(obj, self.expr)
        else:
            qs = self.expr
        if self.filter:
            qs = qs.filter(self.filter)
        # qs._lookup_joins - should invalidate too
        res = qs.count()
        cache.set(self.name, res, timeout=self.timeout)
        return res

    def contribute_to_class(self, cls, field_name):
        self.cls = cls
        self.name = f'{repr(cls)}_{repr(self.expr)}_{repr(self.filter)}'
        # that's wrong lol ^^
        signals = []

        if isinstance(self.expr, str):
            rel = getattr(cls, self.expr).rel
            if hasattr(rel, 'through'):
                signals.append((rel.through, True))
            else:
                signals.append((rel.related_model, False))
        else:
            signals.append((self.expr.model, False))
        for model in self.also_invalidate_on:
            model = getattr(model, 'rel', model)
            if hasattr(model, 'through'):
                signals.append((model.through, True))
            elif hasattr(model, 'related_model'):
                signals.append((model.related_model, False))
            else:
                signals.append((model, False))

        for model, m2m in signals:
            if m2m:
                m2m_changed.connect(self.clean_cache, sender=model)
            else:
                post_save.connect(self.clean_cache, sender=model)
                post_delete.connect(self.clean_cache, sender=model)

    def clean_cache(self, *args, **kwargs):
        cache.delete(self.name)

