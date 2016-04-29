class validation_error(Exception):
    def __init__(self, schema_ctx, location, msg):
        self.schema_ctx = schema_ctx
        self.location = location
        self.msg = msg
        Exception.__init__(self, 'Validation error raised by schema:%s at %s. %s' % (
            schema_ctx, location, msg
        ))
