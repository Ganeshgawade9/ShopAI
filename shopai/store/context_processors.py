from .models import Category
def all_categories(request):
    return {'all_categories': Category.objects.filter(is_active=True, parent=None)[:10]}
