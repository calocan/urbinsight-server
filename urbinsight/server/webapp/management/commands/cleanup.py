import logging

from sop.webapp.models import DataPoint
from django.core.management.base import BaseCommand, CommandError

log = logging.getLogger('info')

class Command(BaseCommand):
    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        """
            Deletes any duplicates having all of the same
            country, state, city, neighborhood, segment_id, blockname, latitude, longitude, classification, setting, source, other_id_neigh, intersc1, intersc2, observer, observer_id, date, time, rand, fid2, version
        :param data_points:
        :return:
        """
        for data_point in DataPoint.objects.all():
            if DataPoint.objects.filter(
                    country=data_point.country,
                    state=data_point.state,
                    city=data_point.city,
                    neighborhood=data_point.neighborhood,
                    segment_id=data_point.segment_id,
                    blockname=data_point.blockname,
                    latitude=data_point.latitude,
                    longitude=data_point.longitude,
                    classification=data_point.classification,
                    setting=data_point.setting,
                    source=data_point.source,
                    other_id_neigh=data_point.other_id_neigh,
                    intersc1=data_point.intersc1,
                    intersc2=data_point.intersc2,
                    observer=data_point.observer,
                    observer_id=data_point.observer_id,
                    date=data_point.date,
                    time=data_point.time,
                    rand=data_point.rand,
                    version=data_point.version).count() > 1:
                log.debug("Deleting id %s", data_point.id)
                data_point.delete()
