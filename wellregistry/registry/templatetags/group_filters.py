"""
Filters to use to determine information about a user's groups
"""

from django import template

register = template.Library()


@register.filter(name='is_in_group')
def is_in_group(user, group_name):
    """
    Return true if user is a member of the group with group_name
    :param user: UserModel
    :param group_name: str
    :return: boolean
    """
    return user.groups.filter(name=group_name).exists()
