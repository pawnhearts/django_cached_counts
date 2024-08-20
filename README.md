## Usage
    from django_cached_counts import CachedCount

    class MyModel(models.Model):
        bar = models.ManyToManyField(Bar)
        foo_count = CachedCount("foo_set", filter=Q(foo__x__gte=10))
        total_user_count = CachedCount(User.objects.all())
        m2m_count = CachedCount('bar_set')

    class Foo(models.Model):
        mymodel = models.ForeignKey(MyModel)

    Those counts would be cached and invalidated when models Foo or User are saved/deleted
