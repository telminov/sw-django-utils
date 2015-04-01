# coding: utf-8

def transform_form_error(form, verbose=True):
    """
        transform form errors to list like
        ["field1: error1", "field2: error2"]
    """
    errors = []
    for field, err_msg in form.errors.items():
        if field == '__all__':  # general errors
            errors.append(', '.join(err_msg))
        else:                   # field errors
            field_name = field
            if verbose and field in form.fields:
                field_name = form.fields[field].label or field
            errors.append('%s: %s' % (field_name, ', '.join(err_msg)))
    return errors
