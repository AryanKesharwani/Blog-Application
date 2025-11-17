from .models import Category

def categories_context(request):
    return {
        'navbar_categories': Category.objects.all()
    }
