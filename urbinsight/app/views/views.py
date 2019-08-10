from django.shortcuts import render

def home(request):
    """
        This view exists until we stop relying on Django for client rendering.
    :param request:
    :return:
    """
    is_admin = 'Admin' in [g.name for g in request.user.groups.all()]
    return render(request, 'home.html', {
        'user': {
            # None if anonymous
            'id': '%s' % request.user.id if request.user.id else 'null',
            # None if anonymous
            'name': "'{} {}'".format(request.user.first_name, request.user.last_name) if request.user.id else 'null',
            'admin': 'true' if is_admin else 'false'
        }
    })
