from django.core.paginator import Paginator


class PaginationMixin:
    def paginate_queryset(self, queryset, page_size):
        paginator = Paginator(queryset, page_size)
        page_number = self.request.GET.get("page", 1)
        return paginator.get_page(page_number)
