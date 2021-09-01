from django.http import JsonResponse


class Res(JsonResponse):
    def __init__(self, status, msg, data=None, error=None):
        obj = {
            'status': status,
            'message': msg,
        }
        if data is None and error is None:
            raise ValueError('needs at least one argument data or error')
        if data is not None:
            obj['data'] = data
        elif error is not None:
            if type(error) == list:
                obj['error'] = error
            else:
                obj['error'] = [error]

        super().__init__(data=obj)
