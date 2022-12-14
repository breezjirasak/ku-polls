from re import S
from secrets import choice
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.http import Http404
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User

from .models import Question, Choice, Vote

class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        """
        Return the last five published questions (not including those set to be
        published in the future).
        """
        return Question.objects.filter(pub_date__lte=timezone.now()).order_by('-pub_date')[:5]


class DetailView(LoginRequiredMixin, generic.DetailView):
    model = Question
    template_name = 'polls/detail.html'
    
    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())
    
    def get(self, request, pk):
        """
        Show error message and return to index page if voting is not allowed.
        """
        user = request.user
        self.question = Question.objects.get(pk=pk)
        
        # To get exixting vote to display radio bullet.
        try:
            self.vote = Vote.objects.get(user=user, choice__question=self.question)
        except Vote.DoesNotExist:
            self.vote = None
        
        # check that you can vote or not. (on date)
        if self.question.can_vote():
            return render(request, 'polls/detail.html', {'question': self.question, 'votes': self.vote})
        else:
            messages.error(request, "Voting is not allowed.")
            return HttpResponseRedirect(reverse('polls:index'))
        
        


class ResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/results.html'

@login_required
def vote(request, question_id):
    """ 
    Show error message and return to detail page you did not select a choice.
    """
    
    # require login to vote
    user = request.user
    if not user.is_authenticated:
       return redirect('login')
   
    print("current user is", user.id, "login", user.username)
    print("Real name:", user.first_name, user.last_name)
   
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
        })
    else:
        try:
            vote_ = Vote.objects.get(user=user, choice__question=selected_choice.question)
        except Vote.DoesNotExist:
            vote_ = Vote.objects.create(user=user, choice=selected_choice) 
        vote_.choice = selected_choice
        vote_.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))