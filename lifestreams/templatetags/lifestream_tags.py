from django import template

register = template.Library()


@register.simple_tag
def lifestream_render(item, template_suffix=None):
	return item.render() if template_suffix is None else item.render(template_suffix)
