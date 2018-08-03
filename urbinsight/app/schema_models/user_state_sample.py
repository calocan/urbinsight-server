from app.helpers.geometry_helpers import ewkt_from_feature
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from rescape_graphene import ramda as R
from app.models import Feature, Region, UserState
from django.db import transaction

from app.schema_models.user_sample import create_sample_users

sample_user_states = [
    dict(username="lion",),
    dict(username="cat", )
]


def delete_sample_user_states():
    UserState.objects.all().delete()


@R.curry
def create_sample_user_state(user, user_state_dict):
    # Save the user_state with the complete data
    user_state = UserState(**R.merge(user_state_dict, dict(user=user)))
    user_state.save()
    return user_state


def create_sample_user_states():
    users = create_sample_users()
    # Convert all sample user_state dicts to persisted UserState instances
    # Use the username to match a real user
    user_states = R.map(
        lambda sample_user_state: create_sample_user_state(
            get_user_model().objects.get(username=sample_user_state['username']),
            R.omit(['username'], sample_user_state)
        ),
        sample_user_states
    )
    return user_states
