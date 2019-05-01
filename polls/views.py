from django.http import HttpResponse,JsonResponse
# from django.shortcuts import render
from django.shortcuts import render, redirect
from django.db.models import Count
from polls.models import Poll, Question, Answer
from polls.forms import PollForm, PollModelForm, QuestionForm,ChoiceModelForm
from django.contrib.auth import authenticate, logout, login
from django.contrib.auth.decorators import login_required, permission_required
from django.forms import formset_factory
import json


def my_login(request):
    context = {}
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            next_url = request.POST.get('next_url')
            if next_url:
                return redirect(next_url)
            else:
                return redirect('index')
        else:
            context['username'] = username
            context['password'] = password
            context['error'] = "wrong username or password"
    next_url = request.GET.get('next')
    if next_url:
        context['next_url'] = next_url

    return render(request, 'polls/login.html', context)


def my_logout(request):
    logout(request)
    return redirect('login')


def index(request):
    poll_list = Poll.objects.annotate(question_count=Count('question'))
    # for poll in poll_list:
    #     question_count = Question.objects.filter(poll_id=poll.id).count()
    #     poll.question_count = question_count

    context = {
        'page_title': "My Polls",
        'poll_list': poll_list
    }
    return render(request, 'polls/index.html', context)


@login_required
@permission_required('polls.view_poll')
def detail(request, id):
    poll = Poll.objects.get(pk=id)

    if request.method == 'POST':
        for question in poll.question_set.all():
            name = 'choice' + str(question.id)
            # print(name)
            choice_id = request.POST.get(name)
            if choice_id:
                try:
                    ans = Answer.objects.get(question_id=question.id)
                    ans.choice_id = choice_id
                    ans.save()
                except Answer.DoesNotExist:
                    Answer.objects.create(
                        choice_id=choice_id,
                        question_id=question.id
                    )
            # print(choice_id)
    # print(request.GET)

    return render(request, 'polls/detail.html', {'poll': poll})


@login_required
@permission_required('polls.add_poll')
def create(request):
    context = {}
    QuestionFormSet = formset_factory(QuestionForm, extra=2, max_num=10)
    if request.method == 'POST':
        form = PollModelForm(request.POST)
        formset = QuestionFormSet(request.POST)
        # form = PollForm(request.POST)
        if form.is_valid():
            poll = form.save()
            # poll = Poll.objects.create(
            #     title = form.cleaned_data.get('title'),
            #     start_date = form.cleaned_data.get('start_date'),
            #     end_date = form.cleaned_data.get('end_date'),

            # )
            # for i in range(1,form.cleaned_data.get('no_questions')+1):
            #     Question.objects.create(
            #         text= 'Q'+str(i),
            #         type='01',
            #         poll=poll
            #     )
            if formset.is_valid():
                for question_form in formset:
                    Question.objects.create(
                        text=question_form.cleaned_data.get('text'),
                        type=question_form.cleaned_data.get('type'),
                        poll=poll
                    )
                    context['success'] = "Poll %s is successfully!" % poll.title
    else:
        form = PollModelForm()
        formset = QuestionFormSet()
    context['form'] = form
    context['formset'] = formset
    return render(request, 'polls/create.html', context)


@login_required
@permission_required('polls.change_poll')
def delete_question(request, question_id):
    question = Question.objects.get(id=question_id)
    question.delete()
    return redirect('update', id=question.poll.id)

@login_required
@permission_required('polls.change_poll')
def add_choice(request, question_id):
    question = Question.objects.get(id=question_id)
    context = {'question': question}
    return render(request, 'choices/add.html', context)
@login_required
@permission_required('polls.change_poll')
def update(request, id):
    QuestionFormSet = formset_factory(QuestionForm, extra=2, max_num=10)    
    poll = Poll.objects.get(pk=id)
    if request.method == 'POST':
        form = PollModelForm(request.POST, instance=poll)
        formset = QuestionFormSet(request.POST)
        if form.is_valid():
            form.save()
            if formset.is_valid():
                for i in formset:
                    if i.cleaned_data.get('question_id'):
                        question = Question.objects.get(id=i.cleaned_data.get('question_id'))

                        if question:
                            question.text = i.cleaned_data.get('text')
                            question.type = i.cleaned_data.get('type')
                            question.save()
                    elif i.cleaned_data.get('text'):
                        Question.objects.create(
                            text=i.cleaned_data.get('text'),
                            type=i.cleaned_data.get('type'),
                            poll=poll
                        )
                return redirect('update', id=id)
    else:
        form = PollModelForm(instance=poll)
        formset = QuestionFormSet(initial=[{'text': i.text, 'type': i.type, 'question_id': i.id}
                                            for i in poll.question_set.all()])
        data = [{'text': i.text, 'type': i.type, 'question_id': i.id}
                for i in poll.question_set.all()]
    context = {'form': form, 'poll': poll,'formset': formset}
    return render(request, 'polls/update.html', context)

def add_choice_api(request, question_id):
    if request.method == 'POST':
        choice_list = json.loads(request.body)
        error_list = []

        for choice in choice_list:
            data = {
                'text': choice['text'],
                'value': choice['value'],
                'question': question_id
            }
            form = ChoiceModelForm(data)
            if form.is_valid:
                form.save()
            else:
                error_list.append(form.error.as_text())
        if len(error_list) == 0:
            return JsonResponse({'message': 'success'}, status=200)
        else:
            return JsonResponse({'message': error_list}, status=400)
    return JsonResponse({'message': 'This API does not accept GET request.'}, status=405)