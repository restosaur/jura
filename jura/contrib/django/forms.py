from django.forms import fields, models
from django.utils.encoding import force_text


__all__ = ['Form', 'FormErrors']


def choice_dict(x, empty=False):
    return {'key': x[0], 'label': x[1], 'empty': empty}


def choicefield_validators(f):
    opts = []

    if not f.required:
        opts.append(choice_dict([None, '-----'], empty=True))

    opts += map(choice_dict, f.choices)
    return {
            'choices': opts,
            }


FORMFIELD_VALIDATORS = {
        fields.IntegerField: lambda f: {
            'min_value': f.min_value, 'max_value': f.max_value,
            },
        fields.ChoiceField: choicefield_validators,
        models.ModelChoiceField: choicefield_validators,
        }


def form_as_filterspec(form):
    fields = {}
    if isinstance(form, type):
        form_fields = form.declared_fields.items()
    else:
        form_fields = form.fields.items()
    for key, field in form_fields:
        validation = {}
        validation.update(getattr(field, 'validation', {}))
        try:
            alidation.update(FORMFIELD_VALIDATORS[type(field)](field))
        except KeyError:
            pass
        fields[key] = {
                'type': type(field).__name__,
                'required': field.required,
                'fieldname': key,
                'help': field.help_text,
                'label': force_text(field.label) if field.label else key,
                'initial': field.initial,
                'validation':  validation,
                }
    return fields


class FormErrors(object):
    def __init__(self, form):
        self.form = form

    def as_dict(self, ctx=None):
        return {
                'errors': self.form.errors,
            }


class Form(object):
    def __init__(self, form, action=None, method='post', description=None):
        self.form = form
        self.action = action
        self.method = method
        self.description = description or ''

    def as_dict(self, ctx=None):
        return {
                'url': self.action or ctx.build_absolute_uri(),
                'method': self.method,
                'fields': form_as_filterspec(self.form),
                'description': self.description,
                }
