from app.helpers.geometry_helpers import ewkt_from_feature

sample_regions = [
    dict(
        key='belgium',
        name='Belgium',
        boundary=dict(
            name='Belgium bounds',
            location=ewkt_from_feature({
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
