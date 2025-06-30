from django.shortcuts import render


"""Views to handle errors"""
def custom_404_view(request, exception=None):
    """ Error Handler 404 - Page Not Found """
    return render(request, 'errors/404.html', status=404)


def custom_500_view(request):
    """ Error Handler 500 - Internal Server Error """
    return render(request, 'errors/500.html', status=500)


