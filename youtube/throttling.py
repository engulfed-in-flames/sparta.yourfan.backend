from rest_framework.throttling import UserRateThrottle, AnonRateThrottle

class ObjectThrottle(UserRateThrottle):
    rate = "10/day"
