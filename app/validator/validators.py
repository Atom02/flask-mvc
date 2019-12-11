from collections import Iterable
from werkzeug.datastructures import FileStorage
from wtforms.validators import DataRequired, StopValidation
class FileRequired(DataRequired):
    """Validates that the data is a Werkzeug
    :class:`~werkzeug.datastructures.FileStorage` object.
    :param message: error message
    You can also use the synonym ``file_required``.
    """

    def __call__(self, form, field):
        if not (isinstance(field.data, FileStorage) and field.data):
            raise StopValidation(self.message or field.gettext(
                'This field is required.'
            ))


file_required = FileRequired


class FileAllowed(object):
    """Validates that the uploaded file is allowed by a given list of
    extensions or a Flask-Uploads :class:`~flaskext.uploads.UploadSet`.
    :param upload_set: A list of extensions or an
        :class:`~flaskext.uploads.UploadSet`
    :param message: error message
    You can also use the synonym ``file_allowed``.
    """

    def __init__(self, upload_set, message=None):
        self.upload_set = upload_set
        self.message = message

    def __call__(self, form, field):
        if not (isinstance(field.data, FileStorage) and field.data):
            return

        filename = field.data.filename.lower()

        if isinstance(self.upload_set, Iterable):
            if any(filename.endswith('.' + x) for x in self.upload_set):
                return

            raise StopValidation(self.message or field.gettext(
                'File does not have an approved extension: {extensions}'
            ).format(extensions=', '.join(self.upload_set)))

        if not self.upload_set.file_allowed(field.data, filename):
            raise StopValidation(self.message or field.gettext(
                'File does not have an approved extension.'
            ))


file_allowed = FileAllowed