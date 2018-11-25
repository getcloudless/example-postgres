"""
Apache Test Fixture

This fixture doesn't do any setup, but verifies that the created service is
running default apache.
"""
import psycopg2
import requests
from cloudless.testutils.blueprint_tester import call_with_retries
from cloudless.testutils.fixture import BlueprintTestInterface, SetupInfo
from cloudless.types.networking import CidrBlock

RETRY_DELAY = float(10.0)
RETRY_COUNT = int(6)

class BlueprintTest(BlueprintTestInterface):
    """
    Fixture class that creates the dependent resources.
    """
    def setup_before_tested_service(self, network):
        """
        Create the dependent services needed to test this service.
        """
        # Since this service has no dependencies, do nothing.
        return SetupInfo({}, {})

    def setup_after_tested_service(self, network, service, setup_info):
        """
        Do any setup that must happen after the service under test has been
        created.
        """
        my_ip = requests.get("http://ipinfo.io/ip")
        test_machine = CidrBlock(my_ip.content.decode("utf-8").strip())
        self.client.paths.add(test_machine, service, 5432)

    def verify(self, network, service, setup_info):
        """
        Given the network name and the service name of the service under test,
        verify that it's behaving as expected.
        """
        def check_consul_setup():
            instances = self.client.service.get_instances(service)
            assert instances, "No instances found!"
            postgres_ip = instances[0].public_ip
            conn = psycopg2.connect("host=%s dbname=test user=test" % postgres_ip)
            cur = conn.cursor()
            cur.execute("CREATE TABLE test (id serial PRIMARY KEY, num integer, data varchar);")
            cur.execute("INSERT INTO test (num, data) VALUES (%s, %s)",(100, "abcdef"))
            cur.execute("SELECT * FROM test;")
            value = cur.fetchone()
            assert value == (1, 100, 'abcdef'), "Saved value does not match!"
        call_with_retries(check_consul_setup, RETRY_COUNT, RETRY_DELAY)
