from ... import register_representation
from . import forms as forms_repr


def register(api):
    register_representation(api, forms_repr.Form)
    register_representation(api, forms_repr.Errors)
