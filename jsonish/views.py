from . import DataResponse


class ErrorView:
    def __init__(self, status):
        self.status = status

    def __call__(self, request, exception=None):
        return DataResponse(
            request, f'{self.status}.html',
            {} if exception is None else {'exception': str(exception)},
            status=self.status,
        )


error_404 = ErrorView(404)
error_500 = ErrorView(500)
error_403 = ErrorView(403)
error_400 = ErrorView(400)
