from django.shortcuts import redirect
from functools import wraps

def premium_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if hasattr(request.user, 'userprofile') and request.user.userprofile.is_premium:
            return view_func(request, *args, **kwargs)
        else:
            return redirect('premium_info')  # Premium olmaları gerektiğini anlatan bir sayfaya yönlendir
    return wrapper
