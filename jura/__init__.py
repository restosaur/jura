class Link(object):
    def __init__(
            self, url, method='get', rel=None, name=None,
            access=None, access_func=None, mimetypes=None,
            headers=None):
        self.url = url
        self.rel = rel
        self.name = name
        self.method = method
        self.access = access
        self.access_func = access_func
        self.headers = headers or {}
        self.mimetypes = mimetypes
        if self.access_func and self.access is not None:
            raise ValueError(
                'You should provide only `access` or `access_func`. Both set.')

    def as_dict(self, ctx=None):
        if self.access_func:
            access = self.access_func(ctx.user)
        else:
            access = self.access
        data = {'url': self.url, 'method': self.method, 'rel': self.rel}
        if self.name:
            data['name'] = self.name
        if access is not None:
            data.update({'access': access})
        if self.headers:
            data['headers'] = self.headers
        if self.mimetypes:
            data['mimetypes'] = self.mimetypes
        return data


class LinkAlreadyRegistered(Exception):
    pass


class Links(object):
    def __init__(self, links=None, key='links', as_list=False):
        self.links = links or []
        self.key = key

        if self.as_list:
            def links_factory(ctx):
                return list(map(
                    lambda x: self.link_to_dict(x, ctx),
                    self.links))
        else:
            def links_factory(ctx):
                return dict(map(
                    lambda x: (x.rel, self.link_to_dict(x, ctx)),
                    self.links))

        self._links_factory = links_factory

    def add(self, link_object):
        self.links.append(link_object)

    def create(self, *args, **kw):
        self.add(Link(*args, **kw))

    def link_to_dict(self, action, ctx):
        return ctx.transform_representation(action)

    def as_dict(self, ctx):
        return {
                self.key: self._links_factory(ctx)
                }


class Composition(object):
    def __init__(self, *items):
        self.items = items

    def add(self, instance):
        self.items.append(instance)

    def as_dict(self, ctx):
        output = {}
        for item in self.items:
            output.update(ctx.transform_representation(item))
        return output


class Collection(object):
    def __init__(
            self, items, field_name='items',
            total_count=None):
        self.items = items
        self.field_name = field_name
        self.total_count = total_count

    def as_dict(self, ctx):
        data = ctx.transform_representation(self.items)
        out = {
                self.field_name: data,
                }
        if self.total_count is not None:
            out['total_count'] = self.total_count
        return out


class Error(object):
    def __init__(self, error):
        self.error = error

    def as_dict(self, ctx):
        return {
                'error': self.error,
                }


class Mapping(object):
    def __init__(self, **kwargs):
        self.mapping = kwargs

    def as_dict(self, ctx):
        return dict([
            (key, ctx.transform_representation(value))
            for key, value in self.mapping.items()])


def compose(*items):
    return Composition(*items)


def register_representation(api, model_class, repr_class=None):
    repr_class = repr_class or model_class
    api.add_representation(
            repr_class, content_type='application/json',
            _transform_func=repr_class.as_dict)


def register(api):
    from . import geo
    register_representation(api, Error)
    register_representation(api, Link)
    register_representation(api, Links)
    register_representation(api, Composition)
    register_representation(api, Collection)
    register_representation(api, Mapping)
    register_representation(api, geo.Location)
