import json

from django.core.paginator import Paginator
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import DetailView, ListView, CreateView, UpdateView, DeleteView
from rest_framework.generics import ListAPIView

from HomeWork_27 import settings

from ads.models import Categories, Ads
from ads.serializers import AdsListSerializer


def index(request):
    return JsonResponse({"status": "ok"}, status=200)


class CategoriesListView(ListView):
    model = Categories

    def get(self, request, *args, **kwargs):
        super().get(request, *args, **kwargs)
        self.object_list = self.object_list.order_by("name")
        response = []
        for category in self.object_list:
            response.append({
                "id": category.id,
                "name": category.name
            })

        return JsonResponse(response, safe=False, status=200)


class CategoriesDetailView(DetailView):
    model = Categories

    def get(self, request, *args, **kwargs):
        category = self.get_object()

        return JsonResponse({
            "id": category.id,
            "name": category.name
        }, safe=False)


@method_decorator(csrf_exempt, name='dispatch')
class CategoriesCreateView(CreateView):
    model = Categories
    fields = ["name"]

    def post(self, request, *args, **kwargs):
        category_data = json.loads(request.body)
        category = Categories.objects.create(name=category_data["name"])

        return JsonResponse({
            "id": category.id,
            "name": category.name,
        }, safe=False)


@method_decorator(csrf_exempt, name='dispatch')
class CategoriesUpdateView(UpdateView):
    model = Categories
    fields = ["name"]

    def patch(self, request, *args, **kwargs):
        super().post(request, *args, **kwargs)
        category_data = json.loads(request.body)
        self.object.name = category_data["name"]

        self.object.save()

        return JsonResponse({
            "id": self.object.id,
            "name": self.object.name,
        }, safe=False)


@method_decorator(csrf_exempt, name='dispatch')
class CategoriesDeleteView(DeleteView):
    model = Categories
    success_url = "/"

    def delete(self, request, *args, **kwargs):
        super().delete(request, *args, **kwargs)

        return JsonResponse({
            "status": "ok"
        }, status=200)


class AdsListView(ListAPIView):
    queryset = Ads.objects.all().order_by('-price')
    serializer_class = AdsListSerializer

    def get(self, request, *args, **kwargs):
        cat_search = request.GET.getlist("cat")
        if cat_search:
            self.queryset = self.queryset.filter(
                category_id__in=cat_search)

        text_search = request.GET.get("text", None)
        if text_search:
            self.queryset = self.queryset.filter(name__icontains=text_search)

        location_search = request.GET.get("location", None)
        if location_search:
            self.queryset = self.queryset.filter(author_id__locations__name__icontains=location_search)

        price_from = request.GET.get("price_from", None)
        if price_from:
            self.queryset = self.queryset.filter(price__gte=price_from)

        price_to = request.GET.get("price_to", None)
        if price_to:
            self.queryset = self.queryset.filter(price__lte=price_to)

        return super().get(request, *args, **kwargs)


# class AdsListView(ListView):
#     model = Ads
#
#     def get(self, request, *args, **kwargs):
#         super().get(request, *args, **kwargs)
#         cat_search = request.GET.get("cat")
#         if cat_search:
#             self.object_list = self.object_list.filter(
#                 category_id__exact=cat_search).select_related("author").order_by("-price")
#         else:
#             self.object_list = self.object_list.select_related("author").order_by("-price")
#
#         paginator = Paginator(self.object_list, settings.TOTAL_ON_PAGE)
#         page_number = request.GET.get("page")
#         page_obj = paginator.get_page(page_number)
#
#         ads_list = []
#         for ads in page_obj:
#             ads_list.append({"id": ads.id,
#                              "name": ads.name,
#                              "author_id": ads.author_id,
#                              "author": ads.author.first_name,
#                              "price": ads.price,
#                              "description": ads.description,
#                              "is_published": ads.is_published,
#                              "image": ads.image.url if ads.image else None,
#                              "category_id": ads.category_id
#                              })
#         response = {
#             "items": ads_list,
#             "num_pages": paginator.num_pages,
#             "total": paginator.count
#         }
#
#         return JsonResponse(response, safe=False, status=200)


class AdsDetailView(DetailView):
    model = Ads

    def get(self, request, *args, **kwargs):
        ads = self.get_object()

        return JsonResponse({
            "id": ads.id,
            "name": ads.name,
            "author_id": ads.author_id,
            "author": ads.author.first_name,
            "price": ads.price,
            "description": ads.description,
            "is_published": ads.is_published,
            "image": ads.image.url if ads.image else None,
            "category_id": ads.category_id
        }, safe=False)


@method_decorator(csrf_exempt, name='dispatch')
class AdsCreateView(CreateView):
    model = Ads
    fields = ["name", "author", "price", "description", "is_published", "image", "category"]

    def post(self, request, *args, **kwargs):
        ads_data = json.loads(request.body)
        ads = Ads.objects.create(
            name=ads_data["name"],
            author=ads_data["author"],
            price=ads_data["price"],
            description=ads_data["description"],
            is_published=ads_data["is_published"],
            image=ads_data["image"],
            category=ads_data["category"]
        )

        ads.save()

        return JsonResponse({
            "id": ads.id,
            "name": ads.name,
            "author_id": ads.author_id,
            "author": ads.author.first_name,
            "price": ads.price,
            "description": ads.description,
            "is_published": ads.is_published,
            "image": ads.image.url if ads.image else None,
            "category_id": ads.category_id
        }, safe=False)


@method_decorator(csrf_exempt, name='dispatch')
class AdsUpdateView(UpdateView):
    model = Ads
    fields = ["name", "author", "price", "description", "category"]

    def patch(self, request, *args, **kwargs):
        super().post(request, *args, **kwargs)
        ads_data = json.loads(request.body)

        self.object.name = ads_data["name"]
        self.object.author_id = ads_data["author_id"]
        self.object.price = ads_data["price"]
        self.object.description = ads_data["description"]
        self.object.category_id = ads_data["category_id"]

        self.object.save()

        return JsonResponse({
            "id": self.object.id,
            "name": self.object.name,
            "author_id": self.object.author_id,
            "author": self.object.author.first_name,
            "price": self.object.price,
            "description": self.object.description,
            "is_published": self.object.is_published,
            "image": self.object.image.url if self.object.image else None,
            "category_id": self.object.category_id
        }, safe=False)


@method_decorator(csrf_exempt, name='dispatch')
class AdsDeleteView(DeleteView):
    model = Ads
    success_url = "/"

    def delete(self, request, *args, **kwargs):
        super().delete(request, *args, **kwargs)

        return JsonResponse({
            "status": "ok"
        }, status=200)


@method_decorator(csrf_exempt, name='dispatch')
class AdsImageView(UpdateView):
    model = Ads
    fields = ["name", "image"]

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        self.object.image = request.FILES["image"]
        self.object.save()

        return JsonResponse({
            "id": self.object.id,
            "name": self.object.name,
            "author_id": self.object.author_id,
            "author": self.object.author.first_name,
            "price": self.object.price,
            "description": self.object.description,
            "is_published": self.object.is_published,
            "image": self.object.image.url if self.object.image else None,
            "category_id": self.object.category_id
        }, safe=False)
