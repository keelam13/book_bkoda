# manage_booking/utils.py

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def paginate_queryset(request, queryset, items_per_page=3):
    """
    Helper function to paginate a given queryset.

    Args:
        request: The HttpRequest object.
        queryset: The Django QuerySet to paginate.
        items_per_page (int): The number of items to display per page.

    Returns:
        django.core.paginator.Page: A Page object containing the items for the current page.
    """
    paginator = Paginator(queryset, items_per_page)
    page_number = request.GET.get('page')

    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        page_obj = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        page_obj = paginator.page(paginator.num_pages)

    return page_obj
