from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required

# Create your views here.


@login_required
@permission_required('quiz.add_patient')
def experiment_list(request, template_name="experiment/experiment_list.html"):
    context = {}
    return render(request, template_name, context)
