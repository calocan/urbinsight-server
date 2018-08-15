from app.helpers.geometry_helpers import ewkt_from_feature
from app.schema_models.user_sample import create_sample_user, sample_users, create_sample_users
from django.contrib.auth import get_user_model
from rescape_graphene import ramda as R
from app.models import Feature, Region
from django.db import transaction

sample_regions = [
    dict(
        key='belgium',
        name='Belgium',
        boundary=dict(
            name='Belgium bounds',
            geometry=ewkt_from_feature({
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [
                    [[49.5294835476, 2.51357303225], [51.4750237087, 2.51357303225], [51.4750237087, 6.15665815596],
                     [49.5294835476, 6.15665815596], [49.5294835476, 2.51357303225]]]
            }
        })),
        data=dict()
    ),
]


@transaction.atomic
def create_sample_region(region_dict):
    # Save the region with the complete data

    boundary = Feature(**R.prop('boundary', region_dict))
    boundary.save()
    region = Region(**R.merge(region_dict, dict(boundary=boundary)))
    region.save()
    return region





def delete_sample_regions():
    Region.objects.all().delete()


def create_sample_regions(users=None):
    """
        Create sample regions owned by the given users or users created with create_sample_users
    :param users:
    :return:
    """
    delete_sample_regions()
    users = users or create_sample_users()
    # Convert all sample region dicts to persisted Region instances
    # Give each reach an owner
    return R.map(
        lambda kv: create_sample_region(R.merge(kv[1], dict(owner=users[kv[0] % len(users)]))),
        enumerate(sample_regions))
