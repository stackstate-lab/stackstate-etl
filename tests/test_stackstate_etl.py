from stackstate_etl.model.instance import InstanceInfo
from stackstate_etl.model.etl import ETL
from stackstate_etl.model.factory import TopologyFactory
from stackstate_etl.etl.etl_driver import ETLDriver
import logging

logging.basicConfig()
logger = logging.getLogger("stackstate_etl")
logger.setLevel(logging.INFO)


def test_processing_sample():
    conf = InstanceInfo()
    conf.etl = ETL()
    conf.etl.refs = ["file://./tests/1_sample_host_etl.yaml", "file://./tests/2_sample_disk_etl.yaml"]
    factory = TopologyFactory()
    driver = ETLDriver(conf, factory, logger)
    driver.process()
    assert len(factory.components) == 2
    component = factory.get_component(factory.get_uid("nutanix", "host", "ed5edbbb-7428-4066-ae90-1270dcca2f37"))
    assert "processor:label" in component.properties.labels
    assert len(factory.relations) == 1
    assert len(factory.health) == 1
    assert len(factory.metrics) == 2
