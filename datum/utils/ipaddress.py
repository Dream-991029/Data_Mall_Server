class NetAddress(object):
    def __init__(self, request):
        self.scheme = request.scheme
        self.host = request.get_host()
        self.ip_address = self.scheme + "://" + self.host
