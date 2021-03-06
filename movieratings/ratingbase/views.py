from django.contrib.auth.forms import UserCreationForm
from .forms import RaterForm, RatingForm
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView

from .models import Movie, Rater, Rating


def index(request):
    significantly_rated = Movie.objects.filter(ratings_count__gte=15)
    top_twenty = significantly_rated.order_by('avg_rating').reverse()[:20]
    return render(request, 'ratingbase/index.html', {'top_twenty': top_twenty})


def movie_detail(request, movie_id):

    context = {}

    movie = get_object_or_404(Movie, movie_id=movie_id)
    context['movie'] = movie

    movie_ratings = Rating.objects.filter(movie=movie)
    context['movie_ratings'] = movie_ratings

    if movie_ratings.filter(rater=request.user.rater):
        context['rated'] = True

    blank_rating_form = RatingForm()
    context['rating_form'] = blank_rating_form

    if request.method == 'POST':
        rating_form = RatingForm(request.POST)
        if rating_form.is_valid():
            new_rating = rating_form.save(commit=False)
            new_rating.movie = movie
            new_rating.rater = request.user.rater
            new_rating.save()
            return HttpResponseRedirect('/ratingbase/')
        else:
            context['rating_form'] = rating_form
    return render(request, 'ratingbase/movie_detail.html', context)


class RaterDetailView(DetailView):
    model = Rater

    def get_context_data(self, **kwargs):
        context = super(RaterDetailView, self).get_context_data(**kwargs)
        context['ratings'] = self.object.get_ratings()
        return context


def rater_profile(request):
    if request.user.is_authenticated():
        rater = request.user.rater
        ratings = rater.get_ratings()

        if request.method == "POST":
            print(request.POST)
            rating = Rating.objects.get(id=request.POST['rating_id'])

            if request.POST['action'] == 'Delete':
                print(request.POST)
                rating.delete()
            else:
                print(rating.id)
                return HttpResponseRedirect(
                    '/ratingbase/edit/{}'.format(rating.id))

        context = {'rater': rater, 'ratings': ratings}
        return render(request, 'ratingbase/rater_profile.html', context)
    else:
        return HttpResponseRedirect('/register')


class RatingUpdate(UpdateView):
    model = Rating
    fields = ['rating', 'review']
    template_name_suffix = '_update_form'

    def form_valid(self, form):
        if form.instance.rater == self.request.user.rater:
            self.object = form.save()
            return super(ModelFormMixin, self).form_valid(form)
        else:
            return self.form_invalid(form)

# @login_required
# def edit(request, id):
#
#     rating = Rating.objects.get(id=id)
#     print(rating, rating.rater, request.user.rater)
#     if rating.rater == request.user.rater:
#
#         if request.method == 'POST':
#             rating_form = RatingForm(request.POST, instance=rating)
#             if rating_form.is_valid():
#                 rating_form.save()
#                 return HttpResponseRedirect('/ratingbase/rater/profile/')
#         else:
#             rating_form = RatingForm()
#
#         context = {'form': rating_form, 'rating': rating}
#         return render(request, 'ratingbase/edit.html', context)
#     else:
#         return HttpResponseRedirect('/ratingbase/')


@login_required
def redirect(request):
    url = '/ratingbase/rater/{}/'.format(request.user.rater.rater_id)
    return HttpResponseRedirect(url)


def register(request):
    if request.method == 'POST':
        user_form = UserCreationForm(request.POST)
        rater_form = RaterForm(request.POST)
        if user_form.is_valid() and rater_form.is_valid():
            new_user = user_form.save()
            new_rater = rater_form.save(commit=False)
            new_rater.user = new_user
            new_rater.save()
            return HttpResponseRedirect("/ratingbase/")
        else:
            print(user_form.errors, rater_form.errors)
    else:
        user_form = UserCreationForm()
        rater_form = RaterForm()

    context = {'user_form': user_form, 'rater_form': rater_form}
    return render(request, "registration/register.html", context)
