from django import forms
from .models import Product


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "name",
            "description",
            "price",
            "discount",
            "category",
            "is_new",
            "image",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            css_classes = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = (css_classes + " form-control").strip()
        # File input needs proper class
        self.fields["image"].widget.attrs["class"] = "form-control-file"

