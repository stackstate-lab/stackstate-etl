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
    conf.etl.refs = ["file://./tests/sample_etl.yaml"]
    factory = TopologyFactory()
    driver = ETLDriver(conf, factory, logger)
    driver.process()
    assert len(factory.components) == 1
