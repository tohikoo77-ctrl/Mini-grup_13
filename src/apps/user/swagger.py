try:
    from drf_yasg.utils import swagger_auto_schema
except ImportError:
    try:
        from drf_spectacular.utils import extend_schema

        def swagger_post(serializer_class):
            return extend_schema(request=serializer_class, responses={200: dict})
    except ImportError:
        def swagger_post(serializer_class):
            def decorator(func):
                return func

            return decorator
else:
    def swagger_post(serializer_class):
        return swagger_auto_schema(
            request_body=serializer_class,
            responses={200: "OK"},
        )
