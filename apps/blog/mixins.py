from django.contrib import messages


class SuccessMessageOnFormValidMixin:
    success_message = ''

    def form_valid(self, form):
        messages.success(self.request, self.success_message)
        return super().form_valid(form)


class ErrorMessageOnFormInvalidMixin:
    error_message = ''

    def form_invalid(self, form):
        messages.error(self.request, self.error_message)
        return super().form_invalid(form)


class MessagesOnFormProcessingMixin(SuccessMessageOnFormValidMixin,
                                    ErrorMessageOnFormInvalidMixin):
    pass
